"""
Admin Dashboard API Routes
Secure endpoints for viewing users, orders, plans, and remedies
"""

import os
import csv
import io
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Header, Query, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Admin credentials from environment
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'NiroAdmin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'NewAdmin@123')

# Simple token store (in production, use Redis or DB)
active_admin_sessions: Dict[str, datetime] = {}

def generate_admin_token(username: str) -> str:
    """Generate a simple admin session token"""
    token_data = f"{username}:{datetime.now(timezone.utc).isoformat()}:{os.urandom(16).hex()}"
    return hashlib.sha256(token_data.encode()).hexdigest()

def verify_admin_token(token: str) -> bool:
    """Verify admin token is valid and not expired"""
    if not token or token not in active_admin_sessions:
        return False
    expiry = active_admin_sessions.get(token)
    if expiry and expiry > datetime.now(timezone.utc):
        return True
    # Token expired, remove it
    active_admin_sessions.pop(token, None)
    return False

def get_environment_from_request(request: Request) -> str:
    """Detect environment from request host"""
    host = request.headers.get('host', '')
    origin = request.headers.get('origin', '')
    
    # Check for production domain
    if '.emergent.host' in host or '.emergent.host' in origin:
        return 'production'
    return 'preview'

async def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Get database from app state"""
    return request.app.state.db


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    ok: bool
    token: Optional[str] = None
    message: str

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(req: AdminLoginRequest):
    """Admin login endpoint"""
    if req.username == ADMIN_USERNAME and req.password == ADMIN_PASSWORD:
        token = generate_admin_token(req.username)
        # Token valid for 24 hours
        active_admin_sessions[token] = datetime.now(timezone.utc) + timedelta(hours=24)
        logger.info(f"Admin login successful for {req.username}")
        return AdminLoginResponse(ok=True, token=token, message="Login successful")
    
    logger.warning(f"Admin login failed for {req.username}")
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/logout")
async def admin_logout(x_admin_token: str = Header(None)):
    """Admin logout endpoint"""
    if x_admin_token and x_admin_token in active_admin_sessions:
        del active_admin_sessions[x_admin_token]
    return {"ok": True, "message": "Logged out"}

@router.get("/verify")
async def verify_session(x_admin_token: str = Header(None)):
    """Verify admin session is valid"""
    if verify_admin_token(x_admin_token):
        return {"ok": True, "valid": True}
    raise HTTPException(status_code=401, detail="Invalid or expired session")


# ============================================================================
# STATS ENDPOINT
# ============================================================================

@router.get("/stats")
async def get_dashboard_stats(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all", description="Filter by environment: all, production, preview")
):
    """Get dashboard statistics"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    # Build environment filter
    env_filter = {}
    if environment != "all":
        env_filter["environment"] = environment
    
    # Get counts - combine both user collections
    google_users = await db.users.count_documents(env_filter if env_filter else {})
    legacy_users = await db.auth_users.count_documents({})
    total_users = google_users + legacy_users
    
    # Users today (Google OAuth only - legacy doesn't have proper datetime)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    users_today_filter = {"created_at": {"$gte": today_start}}
    if env_filter:
        users_today_filter.update(env_filter)
    users_today = await db.users.count_documents(users_today_filter)
    
    # Orders (plans)
    orders_filter = {"status": "paid"}
    if env_filter:
        orders_filter.update(env_filter)
    total_orders = await db.niro_simplified_orders.count_documents(orders_filter)
    
    # Also count legacy v2 orders
    legacy_orders = await db.niro_v2_orders.count_documents({})
    
    # Active plans
    plans_filter = {"status": "active"}
    if env_filter:
        plans_filter.update(env_filter)
    active_plans = await db.niro_simplified_plans.count_documents(plans_filter)
    
    # Chat threads
    threads_filter = {}
    if env_filter:
        threads_filter.update(env_filter)
    total_threads = await db.niro_simplified_threads.count_documents(threads_filter)
    
    # Also count legacy messages
    legacy_messages = await db.niro_messages.count_documents({})
    
    # Revenue calculation
    revenue_pipeline = [
        {"$match": {"status": "paid", **env_filter}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    revenue_result = await db.niro_simplified_orders.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] / 100 if revenue_result else 0  # Convert paise to INR
    
    # Remedy orders
    remedy_orders = await db.niro_remedy_orders.count_documents({"status": "paid", **env_filter})
    
    # Profiles count
    profiles_count = await db.auth_profiles.count_documents({})
    
    # Recent activity (last 10 events) - from both collections
    recent_google_users = await db.users.find(
        env_filter if env_filter else {},
        {"_id": 0, "email": 1, "name": 1, "created_at": 1}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    recent_orders = await db.niro_simplified_orders.find(
        {"status": "paid", **env_filter},
        {"_id": 0, "order_id": 1, "amount": 1, "topic_id": 1, "tier_level": 1, "created_at": 1}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "ok": True,
        "stats": {
            "total_users": total_users,
            "google_users": google_users,
            "legacy_users": legacy_users,
            "profiles_count": profiles_count,
            "users_today": users_today,
            "total_orders": total_orders + legacy_orders,
            "active_plans": active_plans,
            "total_threads": total_threads,
            "legacy_messages": legacy_messages,
            "total_revenue_inr": total_revenue,
            "remedy_orders": remedy_orders
        },
        "recent_activity": {
            "users": recent_google_users,
            "orders": recent_orders
        },
        "environment_filter": environment
    }


# ============================================================================
# USERS ENDPOINTS
# ============================================================================

@router.get("/users")
async def list_users(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    search: str = Query(default=None),
    has_purchase: bool = Query(default=None),
    source: str = Query(default="all", description="Filter by source: all, google, legacy")
):
    """List all users with pagination - combines Google OAuth users and legacy auth_users"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    all_users = []
    
    # Get Google OAuth users (new system)
    if source in ["all", "google"]:
        query = {}
        if environment != "all":
            query["environment"] = environment
        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}}
            ]
        
        google_users = await db.users.find(query, {"_id": 0}).to_list(1000)
        for u in google_users:
            u["auth_source"] = "google"
        all_users.extend(google_users)
    
    # Get legacy auth_users with profiles (old system)
    if source in ["all", "legacy"]:
        legacy_query = {}
        if search:
            legacy_query["identifier"] = {"$regex": search, "$options": "i"}
        
        legacy_users_cursor = db.auth_users.find(legacy_query, {"_id": 0})
        legacy_users = await legacy_users_cursor.to_list(1000)
        
        # Enrich with profile data
        for user in legacy_users:
            user_id = user.get("user_id")
            profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0})
            if profile:
                user["name"] = profile.get("name", "")
                user["dob"] = profile.get("dob", "")
                user["tob"] = profile.get("tob", "")
                user["pob"] = profile.get("location", "")
                user["gender"] = profile.get("gender", "")
                user["marital_status"] = profile.get("marital_status", "")
                user["profile_complete"] = True
            else:
                user["profile_complete"] = False
            
            # Map identifier to email
            user["email"] = user.get("identifier", "")
            user["auth_source"] = "legacy"
        
        # Filter by search on name if provided
        if search:
            legacy_users = [u for u in legacy_users if 
                search.lower() in u.get("email", "").lower() or 
                search.lower() in u.get("name", "").lower()]
        
        all_users.extend(legacy_users)
    
    # Sort by created_at descending
    all_users.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Get total count
    total = len(all_users)
    
    # Apply pagination
    skip = (page - 1) * limit
    paginated_users = all_users[skip:skip + limit]
    
    # If filtering by purchase status, we need to check plans
    if has_purchase is not None:
        user_ids_with_purchases = set()
        plans_cursor = db.niro_simplified_plans.find({}, {"user_id": 1})
        async for plan in plans_cursor:
            user_ids_with_purchases.add(plan.get("user_id"))
        
        # Also check orders
        orders_cursor = db.niro_simplified_orders.find({"status": "paid"}, {"user_id": 1})
        async for order in orders_cursor:
            user_ids_with_purchases.add(order.get("user_id"))
        
        if has_purchase:
            paginated_users = [u for u in paginated_users if u.get("user_id") in user_ids_with_purchases]
        else:
            paginated_users = [u for u in paginated_users if u.get("user_id") not in user_ids_with_purchases]
    
    # Get purchase stats for each user
    for user in paginated_users:
        user_id = user.get("user_id")
        if user_id:
            # Count purchases
            purchase_count = await db.niro_simplified_plans.count_documents({"user_id": user_id})
            user["purchase_count"] = purchase_count
            
            # Calculate total spent
            spent_pipeline = [
                {"$match": {"user_id": user_id, "status": "paid"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            spent_result = await db.niro_simplified_orders.aggregate(spent_pipeline).to_list(1)
            user["total_spent"] = spent_result[0]["total"] / 100 if spent_result else 0
    
    return {
        "ok": True,
        "users": paginated_users,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: str,
    request: Request,
    x_admin_token: str = Header(None)
):
    """Get detailed user info"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's orders
    orders = await db.niro_simplified_orders.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    # Get user's plans
    plans = await db.niro_simplified_plans.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    # Get user's remedy orders
    remedy_orders = await db.niro_remedy_orders.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return {
        "ok": True,
        "user": user,
        "orders": orders,
        "plans": plans,
        "remedy_orders": remedy_orders
    }


# ============================================================================
# ORDERS ENDPOINTS
# ============================================================================

@router.get("/orders")
async def list_orders(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    status: str = Query(default=None),
    topic: str = Query(default=None)
):
    """List all package orders"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    # Build query
    query = {}
    if environment != "all":
        query["environment"] = environment
    if status:
        query["status"] = status
    if topic:
        query["topic_id"] = topic
    
    total = await db.niro_simplified_orders.count_documents(query)
    skip = (page - 1) * limit
    
    orders_cursor = db.niro_simplified_orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    orders = await orders_cursor.to_list(limit)
    
    # Enrich with user info
    for order in orders:
        user_id = order.get("user_id")
        if user_id:
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            order["user_email"] = user.get("email") if user else None
            order["user_name"] = user.get("name") if user else None
    
    # Revenue summary
    revenue_pipeline = [
        {"$match": {"status": "paid", **({} if environment == "all" else {"environment": environment})}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    revenue_result = await db.niro_simplified_orders.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] / 100 if revenue_result else 0
    
    return {
        "ok": True,
        "orders": orders,
        "revenue_inr": total_revenue,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


# ============================================================================
# PLANS ENDPOINTS
# ============================================================================

@router.get("/plans")
async def list_plans(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    status: str = Query(default=None),
    topic: str = Query(default=None)
):
    """List all plans"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {}
    if environment != "all":
        query["environment"] = environment
    if status:
        query["status"] = status
    if topic:
        query["topic_id"] = topic
    
    total = await db.niro_simplified_plans.count_documents(query)
    skip = (page - 1) * limit
    
    plans_cursor = db.niro_simplified_plans.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    plans = await plans_cursor.to_list(limit)
    
    # Enrich with user info
    for plan in plans:
        user_id = plan.get("user_id")
        if user_id:
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            plan["user_email"] = user.get("email") if user else None
            plan["user_name"] = user.get("name") if user else None
    
    return {
        "ok": True,
        "plans": plans,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


# ============================================================================
# REMEDY ORDERS ENDPOINTS
# ============================================================================

@router.get("/remedy-orders")
async def list_remedy_orders(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    status: str = Query(default=None),
    category: str = Query(default=None)
):
    """List all remedy orders"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {}
    if environment != "all":
        query["environment"] = environment
    if status:
        query["status"] = status
    if category:
        query["remedy_category"] = category
    
    total = await db.niro_remedy_orders.count_documents(query)
    skip = (page - 1) * limit
    
    orders_cursor = db.niro_remedy_orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    orders = await orders_cursor.to_list(limit)
    
    # Enrich with user info
    for order in orders:
        user_id = order.get("user_id")
        if user_id:
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            order["user_email"] = user.get("email") if user else None
            order["user_name"] = user.get("name") if user else None
    
    return {
        "ok": True,
        "orders": orders,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

def format_datetime(dt):
    """Format datetime for CSV"""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt) if dt else ""

@router.get("/export/users")
async def export_users_csv(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all")
):
    """Export users as CSV"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {} if environment == "all" else {"environment": environment}
    users_cursor = db.users.find(query, {"_id": 0}).sort("created_at", -1)
    users = await users_cursor.to_list(10000)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "user_id", "email", "name", "dob", "tob", "pob", 
        "gender", "marital_status", "profile_complete", 
        "created_at", "last_login", "environment"
    ])
    
    for user in users:
        writer.writerow([
            user.get("user_id", ""),
            user.get("email", ""),
            user.get("name", ""),
            user.get("dob", ""),
            user.get("tob", ""),
            user.get("pob", ""),
            user.get("gender", ""),
            user.get("marital_status", ""),
            user.get("profile_complete", False),
            format_datetime(user.get("created_at")),
            format_datetime(user.get("last_login")),
            user.get("environment", "preview")
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=niro_users_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@router.get("/export/orders")
async def export_orders_csv(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all")
):
    """Export orders as CSV"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {} if environment == "all" else {"environment": environment}
    orders_cursor = db.niro_simplified_orders.find(query, {"_id": 0}).sort("created_at", -1)
    orders = await orders_cursor.to_list(10000)
    
    # Enrich with user info
    for order in orders:
        user_id = order.get("user_id")
        if user_id:
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            order["user_email"] = user.get("email") if user else ""
            order["user_name"] = user.get("name") if user else ""
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "order_id", "user_email", "user_name", "topic_id", "tier_level",
        "amount_inr", "razorpay_order_id", "razorpay_payment_id",
        "expert_id", "expert_name", "status", "created_at", "environment"
    ])
    
    for order in orders:
        writer.writerow([
            order.get("order_id", ""),
            order.get("user_email", ""),
            order.get("user_name", ""),
            order.get("topic_id", ""),
            order.get("tier_level", ""),
            order.get("amount", 0) / 100,
            order.get("razorpay_order_id", ""),
            order.get("razorpay_payment_id", ""),
            order.get("expert_id", ""),
            order.get("expert_name", ""),
            order.get("status", ""),
            format_datetime(order.get("created_at")),
            order.get("environment", "preview")
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=niro_orders_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@router.get("/export/plans")
async def export_plans_csv(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all")
):
    """Export plans as CSV"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {} if environment == "all" else {"environment": environment}
    plans_cursor = db.niro_simplified_plans.find(query, {"_id": 0}).sort("created_at", -1)
    plans = await plans_cursor.to_list(10000)
    
    # Enrich with user info
    for plan in plans:
        user_id = plan.get("user_id")
        if user_id:
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            plan["user_email"] = user.get("email") if user else ""
            plan["user_name"] = user.get("name") if user else ""
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "plan_id", "user_email", "user_name", "topic_id", "tier_level",
        "price_inr", "status", "validity_weeks", "purchased_at", 
        "expires_at", "scenarios", "environment"
    ])
    
    for plan in plans:
        scenarios = plan.get("selected_scenarios", [])
        writer.writerow([
            plan.get("plan_id", ""),
            plan.get("user_email", ""),
            plan.get("user_name", ""),
            plan.get("topic_id", ""),
            plan.get("tier_level", ""),
            plan.get("price_paid_inr", 0),
            plan.get("status", ""),
            plan.get("validity_weeks", ""),
            format_datetime(plan.get("purchased_at")),
            format_datetime(plan.get("expires_at")),
            "; ".join(scenarios) if scenarios else "",
            plan.get("environment", "preview")
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=niro_plans_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@router.get("/export/remedies")
async def export_remedies_csv(
    request: Request,
    x_admin_token: str = Header(None),
    environment: str = Query(default="all")
):
    """Export remedy orders as CSV"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {} if environment == "all" else {"environment": environment}
    orders_cursor = db.niro_remedy_orders.find(query, {"_id": 0}).sort("created_at", -1)
    orders = await orders_cursor.to_list(10000)
    
    # Enrich with user info
    for order in orders:
        user_id = order.get("user_id")
        if user_id:
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            order["user_email"] = user.get("email") if user else ""
            order["user_name"] = user.get("name") if user else ""
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "remedy_order_id", "user_email", "user_name", "remedy_id", "remedy_name",
        "remedy_category", "price_inr", "expert_id", "expert_name",
        "source", "status", "created_at", "environment"
    ])
    
    for order in orders:
        writer.writerow([
            order.get("remedy_order_id", ""),
            order.get("user_email", ""),
            order.get("user_name", ""),
            order.get("remedy_id", ""),
            order.get("remedy_name", ""),
            order.get("remedy_category", ""),
            order.get("price_inr", 0),
            order.get("expert_id", ""),
            order.get("expert_name", ""),
            order.get("source", "direct"),
            order.get("status", ""),
            format_datetime(order.get("created_at")),
            order.get("environment", "preview")
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=niro_remedies_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
