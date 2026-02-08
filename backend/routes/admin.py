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
    x_admin_token: str = Header(None)
):
    """Get dashboard statistics - all data combined"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    # User counts
    google_users = await db.users.count_documents({})
    legacy_users = await db.auth_users.count_documents({})
    total_users = google_users + legacy_users
    profiles_count = await db.auth_profiles.count_documents({})
    
    # Users today (Google OAuth only)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    users_today = await db.users.count_documents({"created_at": {"$gte": today_start}})
    
    # Orders - combine both collections, all statuses
    simplified_orders = await db.niro_simplified_orders.count_documents({})
    v2_orders = await db.niro_v2_orders.count_documents({})
    total_orders = simplified_orders + v2_orders
    
    # Paid/completed orders - check multiple status values
    paid_statuses = ["paid", "completed", "success", "Paid", "Completed", "Success"]
    paid_simplified = await db.niro_simplified_orders.count_documents({"status": {"$in": paid_statuses}})
    paid_v2 = await db.niro_v2_orders.count_documents({"status": {"$in": paid_statuses}})
    
    # Active plans
    active_plans = await db.niro_simplified_plans.count_documents({"status": "active"})
    
    # Chat threads and messages
    total_threads = await db.niro_simplified_threads.count_documents({})
    legacy_messages = await db.niro_messages.count_documents({})
    
    # Revenue - check multiple amount fields and status values
    total_revenue = 0
    
    # For simplified orders - check for paid/completed status
    simplified_cursor = db.niro_simplified_orders.find(
        {"status": {"$in": paid_statuses}},
        {"amount_inr": 1, "amount": 1, "total_amount": 1}
    )
    async for order in simplified_cursor:
        # Try different amount field names
        amount = order.get("amount_inr") or order.get("total_amount") or order.get("amount") or 0
        # If amount is in paise (> 10000), convert to INR
        if amount > 100000:
            amount = amount / 100
        total_revenue += amount
    
    # For v2 orders
    v2_cursor = db.niro_v2_orders.find(
        {"status": {"$in": paid_statuses}},
        {"total_amount": 1, "amount_inr": 1, "amount": 1}
    )
    async for order in v2_cursor:
        amount = order.get("total_amount") or order.get("amount_inr") or order.get("amount") or 0
        if amount > 100000:
            amount = amount / 100
        total_revenue += amount
    
    # Remedy orders
    remedy_orders = await db.niro_remedy_orders.count_documents({})
    
    return {
        "ok": True,
        "stats": {
            "total_users": total_users,
            "google_users": google_users,
            "legacy_users": legacy_users,
            "profiles_count": profiles_count,
            "users_today": users_today,
            "total_orders": total_orders,
            "simplified_orders": simplified_orders,
            "v2_orders": v2_orders,
            "paid_orders": paid_simplified + paid_v2,
            "active_plans": active_plans,
            "total_threads": total_threads,
            "legacy_messages": legacy_messages,
            "total_revenue_inr": total_revenue,
            "remedy_orders": remedy_orders
        }
    }


# ============================================================================
# USERS ENDPOINTS
# ============================================================================

@router.get("/users")
async def list_users(
    request: Request,
    x_admin_token: str = Header(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    search: str = Query(default=None),
    source: str = Query(default="all", description="Filter: all, google, legacy"),
    profile_status: str = Query(default="all", description="Filter: all, complete, incomplete"),
    sort_by: str = Query(default="created_at", description="Sort by: created_at, name, email"),
    sort_order: str = Query(default="desc", description="Sort order: asc, desc")
):
    """List all users with pagination, filtering, and sorting"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    all_users = []
    
    # Get Google OAuth users (new system)
    if source in ["all", "google"]:
        query = {}
        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}}
            ]
        
        google_users = await db.users.find(query, {"_id": 0}).to_list(5000)
        for u in google_users:
            u["auth_source"] = "google"
            u["profile_complete"] = bool(u.get("dob") and u.get("tob") and u.get("pob"))
        all_users.extend(google_users)
    
    # Get legacy auth_users with profiles (old system)
    if source in ["all", "legacy"]:
        legacy_query = {}
        if search:
            legacy_query["identifier"] = {"$regex": search, "$options": "i"}
        
        legacy_users = await db.auth_users.find(legacy_query, {"_id": 0}).to_list(5000)
        
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
            
            user["email"] = user.get("identifier", "")
            user["auth_source"] = "legacy"
        
        # Filter by name search for legacy
        if search:
            legacy_users = [u for u in legacy_users if 
                search.lower() in u.get("email", "").lower() or 
                search.lower() in u.get("name", "").lower()]
        
        all_users.extend(legacy_users)
    
    # Filter by profile status
    if profile_status == "complete":
        all_users = [u for u in all_users if u.get("profile_complete")]
    elif profile_status == "incomplete":
        all_users = [u for u in all_users if not u.get("profile_complete")]
    
    # Sort
    def get_sort_key(x):
        if sort_by == "name":
            return (x.get("name") or "").lower()
        elif sort_by == "email":
            return (x.get("email") or "").lower()
        else:  # created_at
            created = x.get("created_at", "")
            if isinstance(created, datetime):
                return created.isoformat()
            return str(created) if created else ""
    
    reverse = sort_order == "desc"
    all_users.sort(key=get_sort_key, reverse=reverse)
    
    # Get total count before pagination
    total = len(all_users)
    
    # Apply pagination
    skip = (page - 1) * limit
    paginated_users = all_users[skip:skip + limit]
    
    # Get order count for each user (from both collections)
    for user in paginated_users:
        user_id = user.get("user_id")
        if user_id:
            # Count from simplified orders
            simplified_count = await db.niro_simplified_orders.count_documents({"user_id": user_id})
            # Count from v2 orders
            v2_count = await db.niro_v2_orders.count_documents({"user_id": user_id})
            user["order_count"] = simplified_count + v2_count
            
            # Calculate total spent from both collections
            total_spent = 0
            
            # Simplified orders
            simp_cursor = db.niro_simplified_orders.find({"user_id": user_id}, {"amount_inr": 1, "status": 1})
            async for order in simp_cursor:
                if order.get("status") == "paid":
                    total_spent += order.get("amount_inr", 0)
            
            # V2 orders  
            v2_cursor = db.niro_v2_orders.find({"user_id": user_id}, {"total_amount": 1, "status": 1})
            async for order in v2_cursor:
                if order.get("status") == "paid":
                    total_spent += order.get("total_amount", 0)
            
            user["total_spent"] = total_spent
    
    return {
        "ok": True,
        "users": paginated_users,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        },
        "filters": {
            "source": source,
            "profile_status": profile_status,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
    }

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: str,
    request: Request,
    x_admin_token: str = Header(None)
):
    """Get detailed user info including all orders"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    # Try to find in Google users first
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    
    if not user:
        # Try legacy auth_users
        user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0})
        if user:
            profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0})
            if profile:
                user.update({
                    "name": profile.get("name", ""),
                    "dob": profile.get("dob", ""),
                    "tob": profile.get("tob", ""),
                    "pob": profile.get("location", ""),
                    "gender": profile.get("gender", ""),
                    "marital_status": profile.get("marital_status", ""),
                })
            user["email"] = user.get("identifier", "")
            user["auth_source"] = "legacy"
    else:
        user["auth_source"] = "google"
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's orders from both collections
    simplified_orders = await db.niro_simplified_orders.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    v2_orders = await db.niro_v2_orders.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    # Get user's plans
    plans = await db.niro_simplified_plans.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    # Get user's remedy orders
    remedy_orders = await db.niro_remedy_orders.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return {
        "ok": True,
        "user": user,
        "simplified_orders": simplified_orders,
        "v2_orders": v2_orders,
        "plans": plans,
        "remedy_orders": remedy_orders
    }


# ============================================================================
# ORDERS ENDPOINTS - Combined view of all orders
# ============================================================================

# Paid status values to check
PAID_STATUSES = ["paid", "completed", "success", "Paid", "Completed", "Success"]


@router.get("/orders")
async def list_orders(
    request: Request,
    x_admin_token: str = Header(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    status: str = Query(default="all", description="Filter: all, created, pending, paid, completed, failed"),
    order_type: str = Query(default="all", description="Filter: all, simplified, v2"),
    sort_by: str = Query(default="created_at", description="Sort by: created_at, amount"),
    sort_order: str = Query(default="desc", description="Sort order: asc, desc")
):
    """List all orders from both simplified and v2 collections"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    all_orders = []
    
    # Get simplified orders
    if order_type in ["all", "simplified"]:
        query = {}
        if status != "all":
            if status in ["paid", "completed"]:
                query["status"] = {"$in": PAID_STATUSES}
            else:
                query["status"] = status
        
        simplified_cursor = db.niro_simplified_orders.find(query, {"_id": 0})
        simplified_orders = await simplified_cursor.to_list(1000)
        
        for order in simplified_orders:
            order["order_type"] = "simplified"
            # Try different amount field names
            amount = order.get("amount_inr") or order.get("total_amount") or order.get("amount") or 0
            if amount > 100000:  # If in paise, convert
                amount = amount / 100
            order["amount_display"] = amount
            # Get user info
            user_id = order.get("user_id")
            if user_id:
                user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0, "identifier": 1})
                profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
                order["user_email"] = user.get("identifier") if user else None
                order["user_name"] = profile.get("name") if profile else None
        
        all_orders.extend(simplified_orders)
    
    # Get v2 orders
    if order_type in ["all", "v2"]:
        query = {}
        if status != "all":
            if status in ["paid", "completed"]:
                query["status"] = {"$in": PAID_STATUSES}
            else:
                query["status"] = status
        
        v2_cursor = db.niro_v2_orders.find(query, {"_id": 0})
        v2_orders = await v2_cursor.to_list(1000)
        
        for order in v2_orders:
            order["order_type"] = "v2"
            amount = order.get("total_amount") or order.get("amount_inr") or order.get("amount") or 0
            if amount > 100000:
                amount = amount / 100
            order["amount_display"] = amount
            # Get user info
            user_id = order.get("user_id")
            if user_id and user_id != "unknown":
                user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0, "identifier": 1})
                profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
                order["user_email"] = user.get("identifier") if user else None
                order["user_name"] = profile.get("name") if profile else None
        
        all_orders.extend(v2_orders)
    
    # Sort
    def get_sort_key(x):
        if sort_by == "amount":
            return x.get("amount_display", 0)
        else:
            created = x.get("created_at", "")
            if isinstance(created, datetime):
                return created.isoformat()
            return str(created) if created else ""
    
    reverse = sort_order == "desc"
    all_orders.sort(key=get_sort_key, reverse=reverse)
    
    # Calculate totals - include all paid/completed statuses
    total = len(all_orders)
    total_amount = sum(o.get("amount_display", 0) for o in all_orders)
    paid_amount = sum(o.get("amount_display", 0) for o in all_orders if o.get("status") in PAID_STATUSES)
    
    # Pagination
    skip = (page - 1) * limit
    paginated_orders = all_orders[skip:skip + limit]
    
    return {
        "ok": True,
        "orders": paginated_orders,
        "summary": {
            "total_orders": total,
            "total_amount_inr": total_amount,
            "paid_amount_inr": paid_amount
        },
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        },
        "filters": {
            "status": status,
            "order_type": order_type,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
    }


# ============================================================================
# PLANS ENDPOINTS
# ============================================================================

@router.get("/plans")
async def list_plans(
    request: Request,
    x_admin_token: str = Header(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    status: str = Query(default="all"),
    topic: str = Query(default=None)
):
    """List all plans"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {}
    if status != "all":
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
            user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0, "identifier": 1})
            profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
            plan["user_email"] = user.get("identifier") if user else None
            plan["user_name"] = profile.get("name") if profile else None
    
    return {
        "ok": True,
        "plans": plans,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


# ============================================================================
# REMEDY ORDERS ENDPOINTS
# ============================================================================

@router.get("/remedy-orders")
async def list_remedy_orders(
    request: Request,
    x_admin_token: str = Header(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    status: str = Query(default="all"),
    category: str = Query(default=None)
):
    """List all remedy orders"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {}
    if status != "all":
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
            # Try Google users first
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            if user:
                order["user_email"] = user.get("email")
                order["user_name"] = user.get("name")
            else:
                # Try legacy
                legacy_user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0, "identifier": 1})
                profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
                order["user_email"] = legacy_user.get("identifier") if legacy_user else None
                order["user_name"] = profile.get("name") if profile else None
    
    return {
        "ok": True,
        "orders": orders,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if total > 0 else 0
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
    source: str = Query(default="all")
):
    """Export users as CSV"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    all_users = []
    
    # Get Google OAuth users
    if source in ["all", "google"]:
        google_users = await db.users.find({}, {"_id": 0}).to_list(10000)
        for u in google_users:
            u["auth_source"] = "google"
        all_users.extend(google_users)
    
    # Get legacy users with profiles
    if source in ["all", "legacy"]:
        legacy_users = await db.auth_users.find({}, {"_id": 0}).to_list(10000)
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
            user["email"] = user.get("identifier", "")
            user["auth_source"] = "legacy"
        all_users.extend(legacy_users)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "user_id", "email", "name", "dob", "tob", "pob", 
        "gender", "marital_status", "auth_source", "created_at"
    ])
    
    for user in all_users:
        writer.writerow([
            user.get("user_id", ""),
            user.get("email", ""),
            user.get("name", ""),
            user.get("dob", ""),
            user.get("tob", ""),
            user.get("pob", ""),
            user.get("gender", ""),
            user.get("marital_status", ""),
            user.get("auth_source", "unknown"),
            format_datetime(user.get("created_at"))
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
    x_admin_token: str = Header(None)
):
    """Export all orders as CSV"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    all_orders = []
    
    # Get simplified orders
    simplified_orders = await db.niro_simplified_orders.find({}, {"_id": 0}).to_list(10000)
    for order in simplified_orders:
        order["order_type"] = "simplified"
        order["amount_display"] = order.get("amount_inr", 0)
        user_id = order.get("user_id")
        if user_id:
            user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0, "identifier": 1})
            profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
            order["user_email"] = user.get("identifier") if user else ""
            order["user_name"] = profile.get("name") if profile else ""
    all_orders.extend(simplified_orders)
    
    # Get v2 orders
    v2_orders = await db.niro_v2_orders.find({}, {"_id": 0}).to_list(10000)
    for order in v2_orders:
        order["order_type"] = "v2"
        order["amount_display"] = order.get("total_amount", 0)
        user_id = order.get("user_id")
        if user_id and user_id != "unknown":
            user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0, "identifier": 1})
            profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
            order["user_email"] = user.get("identifier") if user else ""
            order["user_name"] = profile.get("name") if profile else ""
    all_orders.extend(v2_orders)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "order_id", "order_type", "user_email", "user_name", "topic_id", "package_id",
        "amount_inr", "razorpay_order_id", "status", "created_at"
    ])
    
    for order in all_orders:
        writer.writerow([
            order.get("order_id", ""),
            order.get("order_type", ""),
            order.get("user_email", ""),
            order.get("user_name", ""),
            order.get("topic_id", order.get("package_id", "")),
            order.get("tier_id", order.get("package_id", "")),
            order.get("amount_display", 0),
            order.get("razorpay_order_id", ""),
            order.get("status", ""),
            format_datetime(order.get("created_at"))
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
    x_admin_token: str = Header(None)
):
    """Export plans as CSV"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    plans = await db.niro_simplified_plans.find({}, {"_id": 0}).to_list(10000)
    
    for plan in plans:
        user_id = plan.get("user_id")
        if user_id:
            user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0, "identifier": 1})
            profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
            plan["user_email"] = user.get("identifier") if user else ""
            plan["user_name"] = profile.get("name") if profile else ""
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "plan_id", "user_email", "user_name", "topic_id", "tier_level",
        "price_inr", "status", "validity_weeks", "purchased_at", "expires_at"
    ])
    
    for plan in plans:
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
            format_datetime(plan.get("expires_at"))
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
    x_admin_token: str = Header(None)
):
    """Export remedy orders as CSV"""
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    orders = await db.niro_remedy_orders.find({}, {"_id": 0}).to_list(10000)
    
    for order in orders:
        user_id = order.get("user_id")
        if user_id:
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            if user:
                order["user_email"] = user.get("email", "")
                order["user_name"] = user.get("name", "")
            else:
                legacy_user = await db.auth_users.find_one({"user_id": user_id}, {"_id": 0, "identifier": 1})
                profile = await db.auth_profiles.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
                order["user_email"] = legacy_user.get("identifier") if legacy_user else ""
                order["user_name"] = profile.get("name") if profile else ""
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "remedy_order_id", "user_email", "user_name", "remedy_id", "remedy_name",
        "remedy_category", "price_inr", "source", "status", "created_at"
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
            order.get("source", "direct"),
            order.get("status", ""),
            format_datetime(order.get("created_at"))
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=niro_remedies_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
