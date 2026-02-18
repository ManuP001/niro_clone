"""
Admin Dashboard API Routes
Secure endpoints for viewing users, orders, plans, and remedies
"""

import os
import csv
import io
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Header, Query, Request, Response, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Admin credentials from environment
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'NiroAdmin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'NewAdmin@123')

# Simple token store - NOW USES DATABASE for persistence across restarts
# In-memory cache for performance (checked first, then DB)
active_admin_sessions: Dict[str, datetime] = {}

def generate_admin_token(username: str) -> str:
    """Generate a simple admin session token"""
    token_data = f"{username}:{datetime.now(timezone.utc).isoformat()}:{os.urandom(16).hex()}"
    return hashlib.sha256(token_data.encode()).hexdigest()

async def verify_admin_token_async(token: str, db) -> bool:
    """Verify admin token is valid and not expired (async, checks DB)"""
    if not token:
        return False
    
    # Check in-memory cache first
    if token in active_admin_sessions:
        expiry = active_admin_sessions.get(token)
        if expiry and expiry > datetime.now(timezone.utc):
            return True
        # Token expired, remove from cache
        active_admin_sessions.pop(token, None)
    
    # Check database if not in cache
    if db is not None:
        try:
            session = await db.admin_sessions.find_one({"token": token}, {"_id": 0})
            if session:
                expiry = session.get("expires_at")
                if isinstance(expiry, str):
                    expiry = datetime.fromisoformat(expiry)
                if expiry and expiry.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                    # Valid - add to cache
                    active_admin_sessions[token] = expiry.replace(tzinfo=timezone.utc)
                    return True
                else:
                    # Expired - remove from DB
                    await db.admin_sessions.delete_one({"token": token})
        except Exception as e:
            logger.warning(f"Admin token DB check failed: {e}")
    
    return False

def verify_admin_token(token: str) -> bool:
    """Verify admin token (sync, cache only - for backwards compatibility)"""
    if not token or token not in active_admin_sessions:
        return False
    expiry = active_admin_sessions.get(token)
    if expiry and expiry > datetime.now(timezone.utc):
        return True
    # Token expired, remove it
    active_admin_sessions.pop(token, None)
    return False

async def save_admin_session(token: str, username: str, expiry: datetime, db):
    """Save admin session to database for persistence"""
    try:
        await db.admin_sessions.update_one(
            {"token": token},
            {"$set": {
                "token": token,
                "username": username,
                "expires_at": expiry,
                "created_at": datetime.now(timezone.utc)
            }},
            upsert=True
        )
    except Exception as e:
        logger.warning(f"Failed to save admin session to DB: {e}")

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
async def admin_login(req: AdminLoginRequest, request: Request):
    """Admin login endpoint"""
    if req.username == ADMIN_USERNAME and req.password == ADMIN_PASSWORD:
        token = generate_admin_token(req.username)
        expiry = datetime.now(timezone.utc) + timedelta(hours=24)
        # Token valid for 24 hours - store in memory and DB
        active_admin_sessions[token] = expiry
        
        # Save to database for persistence across restarts
        db = await get_db(request)
        await save_admin_session(token, req.username, expiry, db)
        
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
async def verify_session(request: Request, x_admin_token: str = Header(None)):
    """Verify admin session is still valid"""
    db = await get_db(request)
    if await verify_admin_token_async(x_admin_token, db):
        return {"ok": True, "message": "Session valid"}
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
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


# ============================================================================
# TOPICS CRUD
# ============================================================================

class TopicCreate(BaseModel):
    topic_id: str
    label: str
    icon: str = "📌"
    tagline: str = ""
    color: str = "gray"
    order: int = 99
    modalities: List[str] = []
    active: bool = True

class TopicUpdate(BaseModel):
    label: Optional[str] = None
    icon: Optional[str] = None
    tagline: Optional[str] = None
    color: Optional[str] = None
    order: Optional[int] = None
    modalities: Optional[List[str]] = None
    active: Optional[bool] = None

@router.get("/topics")
async def list_admin_topics(
    request: Request,
    x_admin_token: str = Header(None),
    include_inactive: bool = Query(default=False)
):
    """List all topics for admin management"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {} if include_inactive else {"active": {"$ne": False}}
    topics = await db.admin_topics.find(query, {"_id": 0}).sort("order", 1).to_list(100)
    
    return {"ok": True, "topics": topics, "count": len(topics)}

@router.post("/topics")
async def create_admin_topic(
    request: Request,
    topic: TopicCreate,
    x_admin_token: str = Header(None)
):
    """Create a new topic"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    # Check if topic_id already exists
    existing = await db.admin_topics.find_one({"topic_id": topic.topic_id})
    if existing:
        raise HTTPException(status_code=400, detail="Topic ID already exists")
    
    topic_dict = topic.model_dump()
    topic_dict["created_at"] = datetime.now(timezone.utc)
    topic_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.admin_topics.insert_one(topic_dict)
    
    logger.info(f"Admin created topic: {topic.topic_id}")
    return {"ok": True, "topic": {k: v for k, v in topic_dict.items() if k != "_id"}}

@router.put("/topics/{topic_id}")
async def update_admin_topic(
    request: Request,
    topic_id: str,
    topic: TopicUpdate,
    x_admin_token: str = Header(None)
):
    """Update an existing topic"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    update_data = {k: v for k, v in topic.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.admin_topics.update_one(
        {"topic_id": topic_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    updated = await db.admin_topics.find_one({"topic_id": topic_id}, {"_id": 0})
    logger.info(f"Admin updated topic: {topic_id}")
    return {"ok": True, "topic": updated}

@router.delete("/topics/{topic_id}")
async def delete_admin_topic(
    request: Request,
    topic_id: str,
    x_admin_token: str = Header(None),
    hard_delete: bool = Query(default=False)
):
    """Delete (soft or hard) a topic"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    if hard_delete:
        result = await db.admin_topics.delete_one({"topic_id": topic_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Topic not found")
        logger.info(f"Admin hard deleted topic: {topic_id}")
    else:
        result = await db.admin_topics.update_one(
            {"topic_id": topic_id},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Topic not found")
        logger.info(f"Admin soft deleted topic: {topic_id}")
    
    return {"ok": True, "message": f"Topic {'deleted' if hard_delete else 'deactivated'}"}


# ============================================================================
# CATEGORIES CRUD (Parent groupings for tiles on homepage)
# ============================================================================

class CategoryCreate(BaseModel):
    category_id: str
    title: str
    helper_copy: str = ""
    order: int = 1
    active: bool = True

class CategoryUpdate(BaseModel):
    title: Optional[str] = None
    helper_copy: Optional[str] = None
    order: Optional[int] = None
    active: Optional[bool] = None

@router.get("/categories")
async def list_admin_categories(
    request: Request,
    x_admin_token: str = Header(None),
    include_inactive: bool = Query(default=False)
):
    """List all categories (homepage groupings)"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = {} if include_inactive else {"active": {"$ne": False}}
    categories = await db.admin_categories.find(query, {"_id": 0}).sort("order", 1).to_list(50)
    
    return {"ok": True, "categories": categories, "count": len(categories)}

@router.post("/categories")
async def create_admin_category(
    request: Request,
    category: CategoryCreate,
    x_admin_token: str = Header(None)
):
    """Create a new category"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    existing = await db.admin_categories.find_one({"category_id": category.category_id})
    if existing:
        raise HTTPException(status_code=400, detail="Category ID already exists")
    
    category_dict = category.model_dump()
    
    # New categories must start as inactive (can't go live without tiles)
    # They can be activated later after adding tiles
    if category_dict.get("active", True):
        category_dict["active"] = False  # Force inactive on creation
        logger.info(f"Category '{category.category_id}' created as inactive - add tiles before activating")
    
    category_dict["created_at"] = datetime.now(timezone.utc)
    category_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.admin_categories.insert_one(category_dict)
    
    logger.info(f"Admin created category: {category.category_id}")
    return {
        "ok": True, 
        "category": {k: v for k, v in category_dict.items() if k != "_id"},
        "message": "Category created as inactive. Add tiles before activating."
    }

@router.put("/categories/{category_id}")
async def update_admin_category(
    request: Request,
    category_id: str,
    category: CategoryUpdate,
    x_admin_token: str = Header(None)
):
    """Update an existing category"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    update_data = {k: v for k, v in category.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Validation: Category cannot be activated without tiles
    if update_data.get("active") == True:
        tile_count = await db.admin_tiles.count_documents({
            "category_id": category_id, 
            "active": {"$ne": False}
        })
        if tile_count == 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot activate category '{category_id}' - it has no active tiles. Add at least one tile first."
            )
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.admin_categories.update_one(
        {"category_id": category_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    updated = await db.admin_categories.find_one({"category_id": category_id}, {"_id": 0})
    logger.info(f"Admin updated category: {category_id}")
    return {"ok": True, "category": updated}

@router.delete("/categories/{category_id}")
async def delete_admin_category(
    request: Request,
    category_id: str,
    x_admin_token: str = Header(None),
    hard_delete: bool = Query(default=False)
):
    """Delete (soft or hard) a category"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if hard_delete:
        result = await db.admin_categories.delete_one({"category_id": category_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        logger.info(f"Admin hard deleted category: {category_id}")
    else:
        result = await db.admin_categories.update_one(
            {"category_id": category_id},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        logger.info(f"Admin soft deleted category: {category_id}")
    
    return {"ok": True, "message": f"Category {'deleted' if hard_delete else 'deactivated'}"}


# ============================================================================
# TILES CRUD (Individual tiles on homepage, grouped under categories)
# ============================================================================

class TileCreate(BaseModel):
    tile_id: str
    category_id: str  # Parent category (love, career, health)
    short_title: str
    full_title: str = ""
    icon_type: str = "star"
    order: int = 1
    active: bool = True
    # Direct package linking (optional - tile can link directly to a package)
    linked_package_id: Optional[str] = None  # Direct link to a specific package/tier
    linked_topic_id: Optional[str] = None  # Or link to a topic (shows all tiers for that topic)

class TileUpdate(BaseModel):
    category_id: Optional[str] = None
    short_title: Optional[str] = None
    full_title: Optional[str] = None
    icon_type: Optional[str] = None
    order: Optional[int] = None
    active: Optional[bool] = None
    linked_package_id: Optional[str] = None
    linked_topic_id: Optional[str] = None

@router.get("/tiles")
async def list_admin_tiles(
    request: Request,
    x_admin_token: str = Header(None),
    include_inactive: bool = Query(default=False),
    category_id: str = Query(default=None)
):
    """List all tiles (homepage items)"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = {} if include_inactive else {"active": {"$ne": False}}
    if category_id:
        query["category_id"] = category_id
    
    tiles = await db.admin_tiles.find(query, {"_id": 0}).sort([("category_id", 1), ("order", 1)]).to_list(100)
    
    return {"ok": True, "tiles": tiles, "count": len(tiles)}

@router.post("/tiles")
async def create_admin_tile(
    request: Request,
    tile: TileCreate,
    x_admin_token: str = Header(None)
):
    """Create a new tile"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    existing = await db.admin_tiles.find_one({"tile_id": tile.tile_id})
    if existing:
        raise HTTPException(status_code=400, detail="Tile ID already exists")
    
    tile_dict = tile.model_dump()
    tile_dict["created_at"] = datetime.now(timezone.utc)
    tile_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.admin_tiles.insert_one(tile_dict)
    
    logger.info(f"Admin created tile: {tile.tile_id}")
    return {"ok": True, "tile": {k: v for k, v in tile_dict.items() if k != "_id"}}

@router.put("/tiles/{tile_id}")
async def update_admin_tile(
    request: Request,
    tile_id: str,
    tile: TileUpdate,
    x_admin_token: str = Header(None)
):
    """Update an existing tile"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    update_data = {k: v for k, v in tile.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.admin_tiles.update_one(
        {"tile_id": tile_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tile not found")
    
    updated = await db.admin_tiles.find_one({"tile_id": tile_id}, {"_id": 0})
    logger.info(f"Admin updated tile: {tile_id}")
    return {"ok": True, "tile": updated}

@router.delete("/tiles/{tile_id}")
async def delete_admin_tile(
    request: Request,
    tile_id: str,
    x_admin_token: str = Header(None),
    hard_delete: bool = Query(default=False)
):
    """Delete (soft or hard) a tile"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if hard_delete:
        result = await db.admin_tiles.delete_one({"tile_id": tile_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Tile not found")
        logger.info(f"Admin hard deleted tile: {tile_id}")
    else:
        result = await db.admin_tiles.update_one(
            {"tile_id": tile_id},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tile not found")
        logger.info(f"Admin soft deleted tile: {tile_id}")
    
    return {"ok": True, "message": f"Tile {'deleted' if hard_delete else 'deactivated'}"}


# ============================================================================
# EXPERTS CRUD
# ============================================================================

class ExpertCreate(BaseModel):
    expert_id: str
    name: str
    modality: str
    modality_label: str = ""
    bio: str = ""
    languages: str = "Hindi, English"
    years_experience: int = 5
    rating: float = 4.5
    total_consults: int = 0
    topics: List[str] = []
    photo_url: str = ""
    tags: List[str] = []  # legacy flat tags
    life_situation_tags: List[str] = []
    method_tags: List[str] = []
    remedy_tags: List[str] = []
    active: bool = True

class ExpertUpdate(BaseModel):
    name: Optional[str] = None
    modality: Optional[str] = None
    modality_label: Optional[str] = None
    bio: Optional[str] = None
    languages: Optional[str] = None
    years_experience: Optional[int] = None
    rating: Optional[float] = None
    total_consults: Optional[int] = None
    topics: Optional[List[str]] = None
    photo_url: Optional[str] = None
    tags: Optional[List[str]] = None
    life_situation_tags: Optional[List[str]] = None
    method_tags: Optional[List[str]] = None
    remedy_tags: Optional[List[str]] = None
    active: Optional[bool] = None

# Master tag options by type
EXPERT_TAG_OPTIONS = {
    "life_situation": {
        "Career & Work": [
            "Career direction clarity",
            "Job switch decision (stay vs leave)",
            "Job change / transition support",
            "Interview + offer timing",
            "Promotion timing",
            "Salary growth / negotiation clarity",
            "Layoff / job loss recovery",
            "Career break + re-entry",
            "Workplace conflict / toxic manager",
            "Workplace politics / team friction",
            "Relocation for job",
            "Burnout / work stress management",
            "Work-life balance reset",
            "Leadership growth / people management",
        ],
        "Business & Finance": [
            "Business launch timing",
            "Business slowdown / recovery phase",
            "Partnership / cofounder compatibility",
            "Cashflow stress / debt phase",
            "Investment timing (buy/hold/sell windows)",
            "Major purchase timing (house/vehicle)",
            "Property purchase timing",
            "Tax / compliance decision timing",
            "Legal/contract decision timing",
        ],
        "Relationships": [
            "Relationship clarity (where is this going?)",
            "On/off relationship clarity",
            "Breakup recovery",
            "Trust issues / cheating suspicion",
            "Communication fights / repeated conflict",
            "Long-distance relationship",
            "Family opposition to relationship",
            "In-law issues / family dynamics",
            "Emotional dependency / attachment patterns",
        ],
        "Marriage": [
            "Marriage delay (why isn't it happening?)",
            "Finding the right partner (what suits me)",
            "Shortlisting profiles (who is a good match?)",
            "Kundli matching deep-dive (beyond score)",
            "Manglik / non-manglik / anshik guidance",
            "Inter-caste / inter-faith marriage clarity",
            "Second marriage / remarriage",
            "Engagement-to-marriage planning",
            "Family pressure management",
        ],
        "Health & Wellness": [
            "Stress + anxiety management",
            "Sleep issues support",
            "Energy drain / fatigue phase",
            "Recovery phase guidance",
            "Holistic health routine support",
            "Disease-prevention mindset (non-medical)",
        ],
        "Spiritual": [
            "Faith crisis / loss of direction",
            "Life purpose clarity",
            "Meditation habit building",
            "Karma / repeating pattern clarity",
            "Inner peace / emotional steadiness",
            "Spiritual practice guidance (daily routine)",
        ],
        "Other": [
            "Moving abroad / foreign settlement",
            "Visa / immigration timing",
            "Education / exam timing",
            "Goal clarity + planning",
            "Confidence building for decisions",
        ],
    },
    "method": [
        "Dasha analysis",
        "Transit guidance",
        "Good vs caution periods (phase guidance)",
        "Sade Sati guidance",
        "Rahu-Ketu phase guidance",
        "Retrograde impact guidance",
        "Muhurat selection (wedding/engagement/roka)",
        "Court case / legal timing guidance",
        "Travel muhurat",
        "Vastu timing / direction guidance",
    ],
    "remedy_support": [
        "Breathwork guidance",
        "Chakra meditation",
        "Daily practice / routines",
        "Mantra guidance (basic)",
        "Pooja guidance",
        "Gemstone guidance",
        "Energy healing session",
        "Sound healing",
        "Wellness kits guidance",
        "Rituals / sankalp guidance",
    ],
}

@router.get("/tag-options")
async def get_tag_options(
    request: Request,
    x_admin_token: str = Header(None)
):
    """Get all available expert tag options grouped by type"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"ok": True, "tag_options": EXPERT_TAG_OPTIONS}


# Ensure upload directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    x_admin_token: str = Header(None)
):
    """Upload an image file and return its URL"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Validate file type
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} not allowed. Use JPEG, PNG, WebP, or GIF.")
    
    # Generate unique filename
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex[:12]}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Build URL using request base URL
    image_url = f"/api/admin/uploads/{filename}"
    
    logger.info(f"Admin uploaded image: {filename} ({len(content)} bytes)")
    return {"ok": True, "url": image_url, "filename": filename}

from fastapi.responses import FileResponse

@router.get("/uploads/{filename}")
async def serve_upload(filename: str):
    """Serve uploaded files"""
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)




@router.get("/experts")
async def list_admin_experts(
    request: Request,
    x_admin_token: str = Header(None),
    include_inactive: bool = Query(default=False),
    topic: str = Query(default=None)
):
    """List all experts for admin management"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {} if include_inactive else {"active": {"$ne": False}}
    if topic:
        query["topics"] = topic
    
    experts = await db.admin_experts.find(query, {"_id": 0}).sort("name", 1).to_list(500)
    
    return {"ok": True, "experts": experts, "count": len(experts)}

@router.post("/experts")
async def create_admin_expert(
    request: Request,
    expert: ExpertCreate,
    x_admin_token: str = Header(None)
):
    """Create a new expert"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    existing = await db.admin_experts.find_one({"expert_id": expert.expert_id})
    if existing:
        raise HTTPException(status_code=400, detail="Expert ID already exists")
    
    expert_dict = expert.model_dump()
    expert_dict["created_at"] = datetime.now(timezone.utc)
    expert_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.admin_experts.insert_one(expert_dict)
    
    logger.info(f"Admin created expert: {expert.expert_id}")
    return {"ok": True, "expert": {k: v for k, v in expert_dict.items() if k != "_id"}}

@router.put("/experts/{expert_id}")
async def update_admin_expert(
    request: Request,
    expert_id: str,
    expert: ExpertUpdate,
    x_admin_token: str = Header(None)
):
    """Update an existing expert"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    update_data = {k: v for k, v in expert.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.admin_experts.update_one(
        {"expert_id": expert_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    updated = await db.admin_experts.find_one({"expert_id": expert_id}, {"_id": 0})
    logger.info(f"Admin updated expert: {expert_id}")
    return {"ok": True, "expert": updated}

@router.delete("/experts/{expert_id}")
async def delete_admin_expert(
    request: Request,
    expert_id: str,
    x_admin_token: str = Header(None),
    hard_delete: bool = Query(default=False)
):
    """Delete (soft or hard) an expert"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    if hard_delete:
        result = await db.admin_experts.delete_one({"expert_id": expert_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Expert not found")
        logger.info(f"Admin hard deleted expert: {expert_id}")
    else:
        result = await db.admin_experts.update_one(
            {"expert_id": expert_id},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Expert not found")
        logger.info(f"Admin soft deleted expert: {expert_id}")
    
    return {"ok": True, "message": f"Expert {'deleted' if hard_delete else 'deactivated'}"}


# ============================================================================
# REMEDIES CRUD
# ============================================================================

class RemedyCreate(BaseModel):
    remedy_id: str
    title: str
    category: str  # healing, pooja, gemstone, kit, ritual
    price: int
    description: str = ""
    subtitle: str = ""
    benefits: List[str] = []
    helps_with: List[str] = []
    image: str = "✨"
    featured: bool = False
    active: bool = True
    expert_name: Optional[str] = None
    expert_title: Optional[str] = None
    expert_bio: Optional[str] = None

class RemedyUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    subtitle: Optional[str] = None
    benefits: Optional[List[str]] = None
    helps_with: Optional[List[str]] = None
    image: Optional[str] = None
    featured: Optional[bool] = None
    active: Optional[bool] = None
    expert_name: Optional[str] = None
    expert_title: Optional[str] = None
    expert_bio: Optional[str] = None

@router.get("/remedies-catalog")
async def list_admin_remedies(
    request: Request,
    x_admin_token: str = Header(None),
    include_inactive: bool = Query(default=False),
    category: str = Query(default=None)
):
    """List all remedies for admin management"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {} if include_inactive else {"active": {"$ne": False}}
    if category:
        query["category"] = category
    
    remedies = await db.admin_remedies.find(query, {"_id": 0}).sort("title", 1).to_list(200)
    
    return {"ok": True, "remedies": remedies, "count": len(remedies)}

@router.post("/remedies-catalog")
async def create_admin_remedy(
    request: Request,
    remedy: RemedyCreate,
    x_admin_token: str = Header(None)
):
    """Create a new remedy"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    existing = await db.admin_remedies.find_one({"remedy_id": remedy.remedy_id})
    if existing:
        raise HTTPException(status_code=400, detail="Remedy ID already exists")
    
    remedy_dict = remedy.model_dump()
    remedy_dict["created_at"] = datetime.now(timezone.utc)
    remedy_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.admin_remedies.insert_one(remedy_dict)
    
    logger.info(f"Admin created remedy: {remedy.remedy_id}")
    return {"ok": True, "remedy": {k: v for k, v in remedy_dict.items() if k != "_id"}}

@router.put("/remedies-catalog/{remedy_id}")
async def update_admin_remedy(
    request: Request,
    remedy_id: str,
    remedy: RemedyUpdate,
    x_admin_token: str = Header(None)
):
    """Update an existing remedy"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    update_data = {k: v for k, v in remedy.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.admin_remedies.update_one(
        {"remedy_id": remedy_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Remedy not found")
    
    updated = await db.admin_remedies.find_one({"remedy_id": remedy_id}, {"_id": 0})
    logger.info(f"Admin updated remedy: {remedy_id}")
    return {"ok": True, "remedy": updated}

@router.delete("/remedies-catalog/{remedy_id}")
async def delete_admin_remedy(
    request: Request,
    remedy_id: str,
    x_admin_token: str = Header(None),
    hard_delete: bool = Query(default=False)
):
    """Delete (soft or hard) a remedy"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    if hard_delete:
        result = await db.admin_remedies.delete_one({"remedy_id": remedy_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Remedy not found")
        logger.info(f"Admin hard deleted remedy: {remedy_id}")
    else:
        result = await db.admin_remedies.update_one(
            {"remedy_id": remedy_id},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Remedy not found")
        logger.info(f"Admin soft deleted remedy: {remedy_id}")
    
    return {"ok": True, "message": f"Remedy {'deleted' if hard_delete else 'deactivated'}"}


# ============================================================================
# TIERS/PACKAGES CRUD
# ============================================================================

# Rich content structure for packages
class HelpSection(BaseModel):
    title: str
    items: List[str] = []

class AnalysisSection(BaseModel):
    title: str
    items: List[str] = []

class PackageContent(BaseModel):
    # Hero Section
    hero_title: str = ""
    hero_subtitle: str = ""
    trust_line: str = ""
    
    # Package Overview
    overview_title: str = ""
    overview_description: str = ""
    includes: List[str] = []
    
    # What This Helps With (multiple sections like Clarity, Timeline, Support)
    help_sections: List[HelpSection] = []
    
    # How We Analyse
    analysis_intro: str = ""
    analysis_sections: List[AnalysisSection] = []
    
    # What You Receive / Deliverables
    deliverables: List[str] = []

class TierCreate(BaseModel):
    tier_id: str
    name: str  # e.g., "Focussed", "Supported", "Comprehensive"
    topic_id: Optional[str] = None  # Which topic this tier belongs to (optional now)
    price: int
    duration_weeks: int = 4
    duration_days: int = 7  # Alternative to weeks
    calls_included: int = 2
    call_duration_mins: int = 30
    features: List[str] = []
    description: str = ""
    popular: bool = False
    active: bool = True
    # Expert assignment
    expert_ids: List[str] = []  # Astrologers who can handle this package
    # Rich content
    content: Optional[dict] = None  # Full package content (PackageContent structure)

class TierUpdate(BaseModel):
    name: Optional[str] = None
    topic_id: Optional[str] = None
    price: Optional[int] = None
    duration_weeks: Optional[int] = None
    duration_days: Optional[int] = None
    calls_included: Optional[int] = None
    call_duration_mins: Optional[int] = None
    features: Optional[List[str]] = None
    description: Optional[str] = None
    popular: Optional[bool] = None
    active: Optional[bool] = None
    expert_ids: Optional[List[str]] = None
    content: Optional[dict] = None  # Rich package content

@router.get("/tiers")
async def list_admin_tiers(
    request: Request,
    x_admin_token: str = Header(None),
    include_inactive: bool = Query(default=False),
    topic_id: str = Query(default=None)
):
    """List all tiers for admin management"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    query = {} if include_inactive else {"active": {"$ne": False}}
    if topic_id:
        query["topic_id"] = topic_id
    
    tiers = await db.admin_tiers.find(query, {"_id": 0}).sort([("topic_id", 1), ("price", 1)]).to_list(500)
    
    return {"ok": True, "tiers": tiers, "count": len(tiers)}

@router.post("/tiers")
async def create_admin_tier(
    request: Request,
    tier: TierCreate,
    x_admin_token: str = Header(None)
):
    """Create a new tier"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    existing = await db.admin_tiers.find_one({"tier_id": tier.tier_id})
    if existing:
        raise HTTPException(status_code=400, detail="Tier ID already exists")
    
    tier_dict = tier.model_dump()
    tier_dict["created_at"] = datetime.now(timezone.utc)
    tier_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.admin_tiers.insert_one(tier_dict)
    
    logger.info(f"Admin created tier: {tier.tier_id}")
    return {"ok": True, "tier": {k: v for k, v in tier_dict.items() if k != "_id"}}

@router.put("/tiers/{tier_id}")
async def update_admin_tier(
    request: Request,
    tier_id: str,
    tier: TierUpdate,
    x_admin_token: str = Header(None)
):
    """Update an existing tier"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    update_data = {k: v for k, v in tier.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.admin_tiers.update_one(
        {"tier_id": tier_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    updated = await db.admin_tiers.find_one({"tier_id": tier_id}, {"_id": 0})
    logger.info(f"Admin updated tier: {tier_id}")
    return {"ok": True, "tier": updated}

@router.delete("/tiers/{tier_id}")
async def delete_admin_tier(
    request: Request,
    tier_id: str,
    x_admin_token: str = Header(None),
    hard_delete: bool = Query(default=False)
):
    """Delete (soft or hard) a tier"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = await get_db(request)
    
    if hard_delete:
        result = await db.admin_tiers.delete_one({"tier_id": tier_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Tier not found")
        logger.info(f"Admin hard deleted tier: {tier_id}")
    else:
        result = await db.admin_tiers.update_one(
            {"tier_id": tier_id},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tier not found")
        logger.info(f"Admin soft deleted tier: {tier_id}")
    
    return {"ok": True, "message": f"Tier {'deleted' if hard_delete else 'deactivated'}"}


# ============================================================================
# CLEAN DUPLICATES ENDPOINT
# ============================================================================

@router.post("/clean-orphaned")
async def clean_orphaned_entries(
    request: Request,
    x_admin_token: str = Header(None)
):
    """Remove catalog entries that have no ID or empty IDs (orphaned data)"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")

    results = {"categories": 0, "tiles": 0, "topics": 0, "tiers": 0}

    # Delete categories without category_id
    r = await db.admin_categories.delete_many({
        "$or": [
            {"category_id": {"$exists": False}},
            {"category_id": None},
            {"category_id": ""},
        ]
    })
    results["categories"] = r.deleted_count

    # Delete tiles without tile_id
    r = await db.admin_tiles.delete_many({
        "$or": [
            {"tile_id": {"$exists": False}},
            {"tile_id": None},
            {"tile_id": ""},
        ]
    })
    results["tiles"] = r.deleted_count

    # Delete topics without topic_id
    r = await db.admin_topics.delete_many({
        "$or": [
            {"topic_id": {"$exists": False}},
            {"topic_id": None},
            {"topic_id": ""},
        ]
    })
    results["topics"] = r.deleted_count

    # Delete tiers without tier_id
    r = await db.admin_tiers.delete_many({
        "$or": [
            {"tier_id": {"$exists": False}},
            {"tier_id": None},
            {"tier_id": ""},
        ]
    })
    results["tiers"] = r.deleted_count

    total = sum(results.values())
    logger.info(f"Admin cleaned orphaned entries: {results}")
    return {
        "ok": True,
        "message": f"Removed {total} orphaned entries (items with missing IDs)",
        "removed": results
    }


@router.delete("/categories/by-title/{title}")
async def delete_category_by_title(
    request: Request,
    title: str,
    x_admin_token: str = Header(None)
):
    """Delete a category by its title — for cases where category_id is missing"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.admin_categories.delete_many({"title": {"$regex": title, "$options": "i"}})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No category found with title matching '{title}'")

    logger.info(f"Admin deleted {result.deleted_count} categories matching title '{title}'")
    return {"ok": True, "message": f"Deleted {result.deleted_count} categories matching '{title}'"}



@router.post("/clean-duplicates")
async def clean_duplicates(
    request: Request,
    x_admin_token: str = Header(None)
):
    """Remove duplicate entries from catalog collections, keeping the first occurrence"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    results = {"categories": 0, "tiles": 0, "topics": 0, "experts": 0, "remedies": 0, "tiers": 0}
    
    # Clean categories duplicates
    seen_categories = set()
    async for cat in db.admin_categories.find({}, {"_id": 1, "category_id": 1}):
        if cat.get("category_id") in seen_categories:
            await db.admin_categories.delete_one({"_id": cat["_id"]})
            results["categories"] += 1
        else:
            seen_categories.add(cat.get("category_id"))
    
    # Clean tiles duplicates
    seen_tiles = set()
    async for tile in db.admin_tiles.find({}, {"_id": 1, "tile_id": 1}):
        if tile.get("tile_id") in seen_tiles:
            await db.admin_tiles.delete_one({"_id": tile["_id"]})
            results["tiles"] += 1
        else:
            seen_tiles.add(tile.get("tile_id"))
    
    # Clean topics duplicates
    seen_topics = set()
    async for topic in db.admin_topics.find({}, {"_id": 1, "topic_id": 1}):
        if topic.get("topic_id") in seen_topics:
            await db.admin_topics.delete_one({"_id": topic["_id"]})
            results["topics"] += 1
        else:
            seen_topics.add(topic.get("topic_id"))
    
    # Clean experts duplicates
    seen_experts = set()
    async for expert in db.admin_experts.find({}, {"_id": 1, "expert_id": 1}):
        if expert.get("expert_id") in seen_experts:
            await db.admin_experts.delete_one({"_id": expert["_id"]})
            results["experts"] += 1
        else:
            seen_experts.add(expert.get("expert_id"))
    
    # Clean tiers duplicates
    seen_tiers = set()
    async for tier in db.admin_tiers.find({}, {"_id": 1, "tier_id": 1}):
        if tier.get("tier_id") in seen_tiers:
            await db.admin_tiers.delete_one({"_id": tier["_id"]})
            results["tiers"] += 1
        else:
            seen_tiers.add(tier.get("tier_id"))
    
    total_removed = sum(results.values())
    logger.info(f"Admin cleaned duplicates: {results}")
    
    return {
        "ok": True,
        "message": f"Removed {total_removed} duplicate entries",
        "removed": results
    }

# ============================================================================
# SEED DATA ENDPOINT (One-time migration from hardcoded to DB)
# ============================================================================

@router.post("/seed-catalog")
async def seed_catalog_data(
    request: Request,
    x_admin_token: str = Header(None),
    force: bool = Query(default=False, description="Force reseed even if data exists")
):
    """Seed initial catalog data from the live SimplifiedCatalog to database"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    results = {"categories": 0, "tiles": 0, "topics": 0, "experts": 0, "remedies": 0, "tiers": 0}
    
    # Check if data already exists
    if not force:
        existing_categories = await db.admin_categories.count_documents({})
        existing_tiles = await db.admin_tiles.count_documents({})
        existing_topics = await db.admin_topics.count_documents({})
        existing_experts = await db.admin_experts.count_documents({})
        existing_tiers = await db.admin_tiers.count_documents({})
        
        if existing_categories > 0 or existing_tiles > 0 or existing_topics > 0 or existing_experts > 0 or existing_tiers > 0:
            return {
                "ok": False,
                "message": "Data already exists. Use force=true to reseed.",
                "existing": {
                    "categories": existing_categories,
                    "tiles": existing_tiles,
                    "topics": existing_topics,
                    "experts": existing_experts,
                    "tiers": existing_tiers
                }
            }
    
    # Seed Categories (3 main homepage groupings)
    categories_data = [
        {"category_id": "love", "title": "Love & Relationships", "helper_copy": "Dating, commitment, healing, family dynamics", "order": 1, "active": True},
        {"category_id": "career", "title": "Career & Money", "helper_copy": "Work direction, stability, timing, growth", "order": 2, "active": True},
        {"category_id": "health", "title": "Health & Wellness", "helper_copy": "Stress, recovery, energy, emotional balance", "order": 3, "active": True},
    ]
    
    for cat in categories_data:
        cat["created_at"] = datetime.now(timezone.utc)
        cat["updated_at"] = datetime.now(timezone.utc)
        await db.admin_categories.update_one(
            {"category_id": cat["category_id"]},
            {"$set": cat},
            upsert=True
        )
        results["categories"] += 1
    
    # Seed Tiles (18 tiles grouped under 3 categories)
    tiles_data = [
        # Love & Relationships (6 tiles)
        {"tile_id": "relationship_healing", "category_id": "love", "short_title": "Healing", "full_title": "Relationship Healing", "icon_type": "healing", "order": 1, "active": True},
        {"tile_id": "dating_compatibility", "category_id": "love", "short_title": "Dating", "full_title": "Dating & Compatibility", "icon_type": "heart", "order": 2, "active": True},
        {"tile_id": "marriage_planning", "category_id": "love", "short_title": "Marriage", "full_title": "Marriage Planning", "icon_type": "rings", "order": 3, "active": True},
        {"tile_id": "communication_trust", "category_id": "love", "short_title": "Trust", "full_title": "Communication & Trust", "icon_type": "chat", "order": 4, "active": True},
        {"tile_id": "family_relationships", "category_id": "love", "short_title": "Family", "full_title": "Family Relationships", "icon_type": "family", "order": 5, "active": True},
        {"tile_id": "breakup_closure", "category_id": "love", "short_title": "Closure", "full_title": "Breakup & Closure", "icon_type": "breakup", "order": 6, "active": True},
        # Career & Money (6 tiles)
        {"tile_id": "career_clarity", "category_id": "career", "short_title": "Clarity", "full_title": "Career Clarity", "icon_type": "compass", "order": 1, "active": True},
        {"tile_id": "job_transition", "category_id": "career", "short_title": "Job Change", "full_title": "Job Transition", "icon_type": "briefcase", "order": 2, "active": True},
        {"tile_id": "money_stability", "category_id": "career", "short_title": "Money", "full_title": "Money & Stability", "icon_type": "wallet", "order": 3, "active": True},
        {"tile_id": "big_decision_timing", "category_id": "career", "short_title": "Timing", "full_title": "Big Decision Timing", "icon_type": "clock", "order": 4, "active": True},
        {"tile_id": "work_stress", "category_id": "career", "short_title": "Work Stress", "full_title": "Work Stress", "icon_type": "stress", "order": 5, "active": True},
        {"tile_id": "office_politics", "category_id": "career", "short_title": "Office", "full_title": "Office Politics", "icon_type": "office", "order": 6, "active": True},
        # Health & Wellness (6 tiles)
        {"tile_id": "stress_management", "category_id": "health", "short_title": "Stress", "full_title": "Stress Management", "icon_type": "stress", "order": 1, "active": True},
        {"tile_id": "sleep_reset", "category_id": "health", "short_title": "Sleep", "full_title": "Sleep Reset", "icon_type": "sleep", "order": 2, "active": True},
        {"tile_id": "energy_balance", "category_id": "health", "short_title": "Energy", "full_title": "Energy Balance", "icon_type": "energy", "order": 3, "active": True},
        {"tile_id": "health_timing", "category_id": "health", "short_title": "Timing", "full_title": "Health Timing", "icon_type": "healing", "order": 4, "active": True},
        {"tile_id": "emotional_wellbeing", "category_id": "health", "short_title": "Emotional", "full_title": "Emotional Wellbeing", "icon_type": "emotional", "order": 5, "active": True},
        {"tile_id": "recovery_support", "category_id": "health", "short_title": "Recovery", "full_title": "Recovery Support", "icon_type": "wellness", "order": 6, "active": True},
    ]
    
    for tile in tiles_data:
        tile["created_at"] = datetime.now(timezone.utc)
        tile["updated_at"] = datetime.now(timezone.utc)
        await db.admin_tiles.update_one(
            {"tile_id": tile["tile_id"]},
            {"$set": tile},
            upsert=True
        )
        results["tiles"] += 1
    
    # Import the live catalog for topics, experts, tiers
    try:
        from backend.niro_simplified.catalog import get_simplified_catalog
        catalog = get_simplified_catalog()
    except Exception as e:
        logger.error(f"Failed to import catalog: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load catalog: {str(e)}")
    
    # Seed Topics from catalog
    for topic_id, topic in catalog.topics.items():
        topic_data = {
            "topic_id": topic.topic_id,
            "label": topic.label,
            "icon": topic.icon,
            "tagline": topic.tagline,
            "color": topic.color_scheme,
            "order": topic.display_order,
            "modalities": topic.expert_modalities,
            "active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.admin_topics.update_one(
            {"topic_id": topic_id},
            {"$set": topic_data},
            upsert=True
        )
        results["topics"] += 1
    
    # Seed Experts from catalog
    for expert_id, expert in catalog.experts.items():
        expert_data = {
            "expert_id": expert.expert_id,
            "name": expert.name,
            "modality": expert.modality,
            "modality_label": expert.modality_label,
            "bio": expert.short_bio,
            "languages": ", ".join(expert.languages) if isinstance(expert.languages, list) else expert.languages,
            "years_experience": expert.experience_years,
            "rating": expert.rating,
            "total_consults": expert.total_consultations,
            "topics": expert.topics,
            "photo_url": expert.photo_url or "",
            "tags": expert.best_for_tags or [],
            "active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.admin_experts.update_one(
            {"expert_id": expert_id},
            {"$set": expert_data},
            upsert=True
        )
        results["experts"] += 1
    
    # Seed Tiers from catalog
    for tier_id, tier in catalog.tiers.items():
        tier_data = {
            "tier_id": tier.tier_id,
            "name": tier.name,
            "topic_id": tier.topic_id,
            "price": tier.price_inr,
            "duration_weeks": tier.validity_weeks,
            "calls_included": tier.access_policy.calls_per_month if tier.access_policy else 0,
            "call_duration_mins": tier.access_policy.call_duration_minutes if tier.access_policy else 30,
            "features": tier.features or [],
            "description": tier.tagline or "",
            "popular": tier.is_recommended or False,
            "tier_level": tier.tier_level,
            "active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.admin_tiers.update_one(
            {"tier_id": tier_id},
            {"$set": tier_data},
            upsert=True
        )
        results["tiers"] += 1
    
    # Seed Remedies - these are defined separately in RemediesScreen
    remedies_data = [
        {"remedy_id": "chakra_balance", "title": "Chakra Balance Program", "subtitle": "3 Guided Sessions", "category": "healing", "price": 3500, "description": "A structured 3-session chakra healing plan to feel calmer, clearer, and more grounded", "benefits": ["3 × guided chakra healing sessions", "Daily micro-practice plan (5-10 mins)", "Guided meditation support", "Diet guidance for energy balance", "24-hour follow-up support"], "helps_with": ["Stress, anxiety, overthinking", "Emotional heaviness, feeling stuck", "Low confidence, low energy"], "image": "🧘", "featured": True, "active": True, "expert_name": "Anu Khanna", "expert_title": "Vedic Astrology + Chakra Healing", "expert_bio": "Anu blends chakra healing with yoga and meditation to help you find calm, clarity, and alignment."},
        {"remedy_id": "santan_pooja", "title": "Santan / Fertility Pooja", "category": "pooja", "price": 2499, "description": "Verified blessing for fertility and conception support", "benefits": ["Performed by verified priests", "Includes prasad delivery", "60-day prayer cycle"], "image": "🙏", "featured": False, "active": True},
        {"remedy_id": "shanti_pooja", "title": "Shanti / Peace Pooja", "category": "pooja", "price": 1999, "description": "Calming ritual for mental peace and harmony", "benefits": ["Reduces stress and anxiety", "Promotes peaceful environment", "7-day ritual cycle"], "image": "🕯️", "featured": False, "active": True},
        {"remedy_id": "lakshmi_pooja", "title": "Lakshmi Prosperity Pooja", "category": "pooja", "price": 2499, "description": "Attract abundance and prosperity", "benefits": ["Attracts wealth energy", "Removes financial blocks", "Includes lakshmi yantra"], "image": "✨", "featured": False, "active": True},
        {"remedy_id": "obstacle_removal", "title": "Obstacle Removal Pooja", "category": "pooja", "price": 1999, "description": "Clear obstacles from your path", "benefits": ["Removes negative influences", "Clears karmic blocks", "Ganesh blessing"], "image": "🔱", "featured": False, "active": True},
        {"remedy_id": "gemstone_career", "title": "Career & Abundance Gemstone", "category": "gemstone", "price": 1499, "description": "Certified gemstone for career growth", "benefits": ["Lab certified", "Energized gemstone", "Career focus"], "image": "💎", "featured": False, "active": True},
        {"remedy_id": "gemstone_calm", "title": "Calm & Grounding Gemstone", "category": "gemstone", "price": 1499, "description": "Natural stone for emotional balance", "benefits": ["Reduces anxiety", "Better sleep", "Emotional stability"], "image": "💎", "featured": False, "active": True},
        {"remedy_id": "gemstone_relationship", "title": "Relationship Harmony Gemstone", "category": "gemstone", "price": 1499, "description": "Stone for love and relationships", "benefits": ["Attracts love", "Heals heart chakra", "Improves communication"], "image": "💎", "featured": False, "active": True},
        {"remedy_id": "stress_sleep_kit", "title": "Stress & Sleep Kit", "category": "kit", "price": 899, "description": "Natural remedies for better rest", "benefits": ["Herbal supplements", "Sleep aid aromatherapy", "Guided meditation audio"], "image": "😴", "featured": False, "active": True},
        {"remedy_id": "protection_kit", "title": "Protection Kit", "category": "kit", "price": 799, "description": "Ward off negative energies", "benefits": ["Protection amulet", "Cleansing herbs", "Daily protection mantra"], "image": "🛡️", "featured": False, "active": True},
        {"remedy_id": "prosperity_kit", "title": "Prosperity Kit", "category": "kit", "price": 999, "description": "Attract abundance and success", "benefits": ["Wealth yantra", "Prosperity herbs", "Abundance affirmations"], "image": "💫", "featured": False, "active": True},
        {"remedy_id": "vitality_kit", "title": "Vitality Kit", "category": "kit", "price": 799, "description": "Boost your energy naturally", "benefits": ["Energy supplements", "Vitality herbs", "Morning ritual guide"], "image": "⚡", "featured": False, "active": True},
        {"remedy_id": "venus_harmony", "title": "Venus Harmony Ritual", "category": "ritual", "price": 999, "description": "Enhance love and beauty in life", "benefits": ["Venus mantra practice", "Relationship healing", "Beauty ritual"], "image": "💖", "featured": False, "active": True},
        {"remedy_id": "mercury_focus", "title": "Mercury Focus Ritual", "category": "ritual", "price": 799, "description": "Sharpen mind and communication", "benefits": ["Mercury mantra", "Communication enhancement", "Mental clarity"], "image": "🧠", "featured": False, "active": True},
        {"remedy_id": "moon_calm", "title": "Moon-Mercury Calm Ritual", "category": "ritual", "price": 899, "description": "Balance emotions and thoughts", "benefits": ["Moon mantra", "Emotional balance", "Mental peace"], "image": "🌙", "featured": False, "active": True},
    ]
    
    for remedy in remedies_data:
        remedy["created_at"] = datetime.now(timezone.utc)
        remedy["updated_at"] = datetime.now(timezone.utc)
        await db.admin_remedies.update_one(
            {"remedy_id": remedy["remedy_id"]},
            {"$set": remedy},
            upsert=True
        )
        results["remedies"] += 1
    
    logger.info(f"Admin seeded catalog data: {results}")
    return {"ok": True, "message": "Catalog data seeded successfully from live catalog", "results": results}


# ============================================================================
# PUBLIC ENDPOINTS (No authentication required for frontend display)
# ============================================================================

@router.get("/public/homepage-data")
async def get_public_homepage_data(request: Request):
    """
    Get homepage categories and tiles for frontend display.
    No authentication required - this is public data.
    Falls back to hardcoded defaults if database is empty.
    """
    db = await get_db(request)
    
    # Fetch categories
    categories = await db.admin_categories.find(
        {"active": {"$ne": False}}, 
        {"_id": 0}
    ).sort("order", 1).to_list(50)
    
    # Fetch tiles
    tiles = await db.admin_tiles.find(
        {"active": {"$ne": False}}, 
        {"_id": 0}
    ).sort([("category_id", 1), ("order", 1)]).to_list(100)
    
    # If no data in DB, return hardcoded defaults
    if not categories or not tiles:
        default_categories = [
            {"category_id": "love", "title": "Love & Relationships", "helper_copy": "Dating, commitment, healing, family dynamics", "order": 1},
            {"category_id": "career", "title": "Career & Money", "helper_copy": "Work direction, stability, timing, growth", "order": 2},
            {"category_id": "health", "title": "Health & Wellness", "helper_copy": "Stress, recovery, energy, emotional balance", "order": 3},
        ]
        
        default_tiles = [
            # Love tiles
            {"tile_id": "relationship_healing", "category_id": "love", "short_title": "Healing", "full_title": "Relationship Healing", "icon_type": "healing", "order": 1},
            {"tile_id": "dating_compatibility", "category_id": "love", "short_title": "Dating", "full_title": "Dating & Compatibility", "icon_type": "heart", "order": 2},
            {"tile_id": "marriage_planning", "category_id": "love", "short_title": "Marriage", "full_title": "Marriage Planning", "icon_type": "rings", "order": 3},
            {"tile_id": "communication_trust", "category_id": "love", "short_title": "Trust", "full_title": "Communication & Trust", "icon_type": "chat", "order": 4},
            {"tile_id": "family_relationships", "category_id": "love", "short_title": "Family", "full_title": "Family Relationships", "icon_type": "family", "order": 5},
            {"tile_id": "breakup_closure", "category_id": "love", "short_title": "Closure", "full_title": "Breakup & Closure", "icon_type": "breakup", "order": 6},
            # Career tiles
            {"tile_id": "career_clarity", "category_id": "career", "short_title": "Clarity", "full_title": "Career Clarity", "icon_type": "compass", "order": 1},
            {"tile_id": "job_transition", "category_id": "career", "short_title": "Job Change", "full_title": "Job Transition", "icon_type": "briefcase", "order": 2},
            {"tile_id": "money_stability", "category_id": "career", "short_title": "Money", "full_title": "Money & Stability", "icon_type": "wallet", "order": 3},
            {"tile_id": "big_decision_timing", "category_id": "career", "short_title": "Timing", "full_title": "Big Decision Timing", "icon_type": "clock", "order": 4},
            {"tile_id": "work_stress", "category_id": "career", "short_title": "Work Stress", "full_title": "Work Stress", "icon_type": "stress", "order": 5},
            {"tile_id": "office_politics", "category_id": "career", "short_title": "Office", "full_title": "Office Politics", "icon_type": "office", "order": 6},
            # Health tiles
            {"tile_id": "stress_management", "category_id": "health", "short_title": "Stress", "full_title": "Stress Management", "icon_type": "stress", "order": 1},
            {"tile_id": "sleep_reset", "category_id": "health", "short_title": "Sleep", "full_title": "Sleep Reset", "icon_type": "sleep", "order": 2},
            {"tile_id": "energy_balance", "category_id": "health", "short_title": "Energy", "full_title": "Energy Balance", "icon_type": "energy", "order": 3},
            {"tile_id": "health_timing", "category_id": "health", "short_title": "Timing", "full_title": "Health Timing", "icon_type": "healing", "order": 4},
            {"tile_id": "emotional_wellbeing", "category_id": "health", "short_title": "Emotional", "full_title": "Emotional Wellbeing", "icon_type": "emotional", "order": 5},
            {"tile_id": "recovery_support", "category_id": "health", "short_title": "Recovery", "full_title": "Recovery Support", "icon_type": "wellness", "order": 6},
        ]
        
        return {
            "ok": True,
            "source": "defaults",
            "categories": default_categories,
            "tiles": default_tiles
        }
    
    # Group tiles by category for easier frontend consumption
    tiles_by_category = {}
    for tile in tiles:
        cat_id = tile.get("category_id", "other")
        if cat_id not in tiles_by_category:
            tiles_by_category[cat_id] = []
        tile_data = {
            "id": tile.get("tile_id"),
            "shortTitle": tile.get("short_title"),
            "fullTitle": tile.get("full_title"),
            "iconType": tile.get("icon_type", "star")
        }
        # Include linked_package_id if present (for standalone packages like Valentine's)
        if tile.get("linked_package_id"):
            tile_data["linkedPackageId"] = tile.get("linked_package_id")
        if tile.get("linked_topic_id"):
            tile_data["linkedTopicId"] = tile.get("linked_topic_id")
        tiles_by_category[cat_id].append(tile_data)
    
    # Build response in frontend-friendly format
    homepage_data = []
    for cat in categories:
        cat_id = cat.get("category_id")
        homepage_data.append({
            "id": cat_id,
            "title": cat.get("title"),
            "helperCopy": cat.get("helper_copy", ""),
            "order": cat.get("order", 99),
            "tiles": tiles_by_category.get(cat_id, [])
        })
    
    # Sort by order to ensure correct display
    homepage_data.sort(key=lambda x: x.get("order", 99))
    
    return {
        "ok": True,
        "source": "database",
        "data": homepage_data,
        "categories": categories,
        "tiles": tiles
    }


@router.get("/public/topics-with-packages")
async def get_topics_with_packages(request: Request):
    """
    Get list of topic IDs that have packages/tiers available.
    No authentication required - used to enable/disable topic tiles on frontend.
    
    Returns both:
    - topic_id values from tiers (e.g., 'career_clarity', 'stress_management')
    - tier_id root names that match frontend tiles (e.g., 'dating_compatibility', 'job_transition')
    
    Normalizes hyphen format to underscore format for frontend compatibility.
    """
    db = await get_db(request)
    
    available_ids = set()
    
    # Get all active tiers
    tiers = await db.admin_tiers.find(
        {"active": {"$ne": False}}, 
        {"_id": 0, "topic_id": 1, "tier_id": 1}
    ).to_list(500)
    
    def normalize_id(id_str):
        """Convert hyphen format to underscore format for frontend compatibility"""
        return id_str.replace("-", "_")
    
    for tier in tiers:
        # Add topic_id (normalized)
        if tier.get("topic_id"):
            available_ids.add(normalize_id(tier["topic_id"]))
        
        # Also extract root name from tier_id (before _focussed, _supported, _comprehensive, _starter, _plus, _pro)
        tier_id = tier.get("tier_id", "")
        for suffix in ["_focussed", "_supported", "_comprehensive", "_starter", "_plus", "_pro"]:
            if tier_id.endswith(suffix):
                root_name = tier_id.replace(suffix, "")
                available_ids.add(normalize_id(root_name))
                break
        else:
            # No suffix found - the tier_id itself might be a tile ID (like 'dating_compatibility')
            # Only add if it looks like a tile ID (contains underscore or hyphen)
            if "_" in tier_id or "-" in tier_id:
                available_ids.add(normalize_id(tier_id))
    
    return {
        "ok": True,
        "topic_ids": sorted(list(available_ids)),
        "count": len(available_ids)
    }


@router.get("/public/package/{package_id}")
async def get_public_package(request: Request, package_id: str):
    """
    Get package details for frontend landing page display.
    No authentication required - this is public data for landing pages.
    Returns package info including rich content.
    """
    db = await get_db(request)
    
    # Fetch the package/tier
    package = await db.admin_tiers.find_one(
        {"tier_id": package_id, "active": {"$ne": False}}, 
        {"_id": 0}
    )
    
    if not package:
        return {"ok": False, "message": "Package not found"}
    
    return {
        "ok": True,
        "package": package
    }


@router.get("/public/tile/{tile_id}")
async def get_public_tile(request: Request, tile_id: str):
    """
    Get tile details including linked package info.
    No authentication required.
    """
    db = await get_db(request)
    
    # Fetch the tile
    tile = await db.admin_tiles.find_one(
        {"tile_id": tile_id, "active": {"$ne": False}}, 
        {"_id": 0}
    )
    
    if not tile:
        return {"ok": False, "message": "Tile not found"}
    
    # If tile has a linked package, fetch that too
    linked_package = None
    if tile.get("linked_package_id"):
        linked_package = await db.admin_tiers.find_one(
            {"tier_id": tile.get("linked_package_id"), "active": {"$ne": False}}, 
            {"_id": 0}
        )
    
    return {
        "ok": True,
        "tile": tile,
        "linked_package": linked_package
    }


@router.get("/export/valentine-data")
async def export_valentine_data(
    request: Request,
    x_admin_token: str = Header(None),
):
    """
    Export all Valentine's Special data (category, tiles, packages) for syncing to production.
    Returns JSON that can be directly imported via /admin/import/catalog-data endpoint.
    """
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Get Valentine's category
    category = await db.admin_categories.find_one(
        {"category_id": "valentine-special"},
        {"_id": 0}
    )
    
    # Get Valentine's tiles
    tiles = await db.admin_tiles.find(
        {"category_id": "valentine-special"},
        {"_id": 0}
    ).to_list(20)
    
    # Get linked packages
    package_ids = [t.get("linked_package_id") for t in tiles if t.get("linked_package_id")]
    packages = await db.admin_tiers.find(
        {"tier_id": {"$in": package_ids}},
        {"_id": 0}
    ).to_list(20)
    
    return {
        "ok": True,
        "export_type": "valentine_special",
        "data": {
            "category": category,
            "tiles": tiles,
            "packages": packages
        }
    }


@router.post("/import/catalog-data")
async def import_catalog_data(
    request: Request,
    x_admin_token: str = Header(None),
):
    """
    Import catalog data (categories, tiles, packages).
    Used to sync data from testing to production environment.
    """
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    body = await request.json()
    data = body.get("data", {})
    
    results = {
        "categories_imported": 0,
        "tiles_imported": 0,
        "packages_imported": 0,
        "errors": []
    }
    
    # Import category
    if data.get("category"):
        cat = data["category"]
        try:
            await db.admin_categories.update_one(
                {"category_id": cat.get("category_id")},
                {"$set": cat},
                upsert=True
            )
            results["categories_imported"] += 1
        except Exception as e:
            results["errors"].append(f"Category error: {str(e)}")
    
    # Import tiles
    for tile in data.get("tiles", []):
        try:
            await db.admin_tiles.update_one(
                {"tile_id": tile.get("tile_id")},
                {"$set": tile},
                upsert=True
            )
            results["tiles_imported"] += 1
        except Exception as e:
            results["errors"].append(f"Tile error: {str(e)}")
    
    # Import packages
    for pkg in data.get("packages", []):
        try:
            await db.admin_tiers.update_one(
                {"tier_id": pkg.get("tier_id")},
                {"$set": pkg},
                upsert=True
            )
            results["packages_imported"] += 1
        except Exception as e:
            results["errors"].append(f"Package error: {str(e)}")
    
    return {
        "ok": True,
        "message": "Import completed",
        "results": results
    }



# ============================================================================
# BULK UPLOAD ENDPOINT
# ============================================================================

class BulkUploadTile(BaseModel):
    tile_id: str
    short_title: str
    full_title: str = ""
    icon_type: str = "star"
    order: int = 1
    active: bool = True
    linked_package_id: Optional[str] = None  # Will auto-link to package if created in same upload

class BulkUploadPackage(BaseModel):
    tier_id: str
    name: str
    price: int
    duration_days: int = 7
    features: List[str] = []
    description: str = ""
    content: Optional[dict] = None  # Rich content (hero_title, help_sections, etc.)
    active: bool = True

class BulkUploadPayload(BaseModel):
    """Single payload to create a category + tiles + packages in one go"""
    category: Optional[dict] = None  # {category_id, title, helper_copy, order, active}
    tiles: List[BulkUploadTile] = []
    packages: List[BulkUploadPackage] = []


@router.post("/bulk-upload")
async def bulk_upload(
    request: Request,
    x_admin_token: str = Header(None)
):
    """
    Bulk upload: create category + tiles + packages in one request.
    Accepts JSON with {category, tiles, packages}.
    Auto-links tiles to packages when tile.linked_package_id matches a package.tier_id in the same upload.
    """
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    now = datetime.now(timezone.utc)

    results = {
        "category_created": False,
        "tiles_created": 0,
        "packages_created": 0,
        "tiles_skipped": [],
        "packages_skipped": [],
        "errors": []
    }

    # 1. Create category (if provided)
    cat_data = body.get("category")
    if cat_data:
        cat_id = cat_data.get("category_id")
        if not cat_id:
            results["errors"].append("Category missing 'category_id'")
        else:
            existing = await db.admin_categories.find_one({"category_id": cat_id})
            if existing:
                # Update existing
                cat_data["updated_at"] = now
                await db.admin_categories.update_one(
                    {"category_id": cat_id},
                    {"$set": cat_data}
                )
                results["category_created"] = True
                logger.info(f"Bulk upload: updated category {cat_id}")
            else:
                cat_data["created_at"] = now
                cat_data["updated_at"] = now
                await db.admin_categories.insert_one(cat_data)
                results["category_created"] = True
                logger.info(f"Bulk upload: created category {cat_id}")

    # 2. Create packages first (so tiles can link to them)
    created_package_ids = set()
    for pkg in body.get("packages", []):
        tier_id = pkg.get("tier_id")
        if not tier_id:
            results["errors"].append(f"Package missing 'tier_id': {pkg.get('name', '?')}")
            continue

        existing = await db.admin_tiers.find_one({"tier_id": tier_id})
        if existing:
            # Update existing
            pkg["updated_at"] = now
            await db.admin_tiers.update_one(
                {"tier_id": tier_id},
                {"$set": pkg}
            )
            results["packages_created"] += 1
            created_package_ids.add(tier_id)
            logger.info(f"Bulk upload: updated package {tier_id}")
        else:
            pkg["created_at"] = now
            pkg["updated_at"] = now
            await db.admin_tiers.insert_one(pkg)
            results["packages_created"] += 1
            created_package_ids.add(tier_id)
            logger.info(f"Bulk upload: created package {tier_id}")

    # 3. Create tiles
    for tile in body.get("tiles", []):
        tile_id = tile.get("tile_id")
        if not tile_id:
            results["errors"].append(f"Tile missing 'tile_id': {tile.get('short_title', '?')}")
            continue

        # Auto-set category_id from the uploaded category
        if cat_data and not tile.get("category_id"):
            tile["category_id"] = cat_data.get("category_id")

        existing = await db.admin_tiles.find_one({"tile_id": tile_id})
        if existing:
            # Update existing
            tile["updated_at"] = now
            await db.admin_tiles.update_one(
                {"tile_id": tile_id},
                {"$set": tile}
            )
            results["tiles_created"] += 1
            logger.info(f"Bulk upload: updated tile {tile_id}")
        else:
            tile["created_at"] = now
            tile["updated_at"] = now
            await db.admin_tiles.insert_one(tile)
            results["tiles_created"] += 1
            logger.info(f"Bulk upload: created tile {tile_id}")

    total = (1 if results["category_created"] else 0) + results["tiles_created"] + results["packages_created"]
    logger.info(f"Bulk upload complete: {results}")

    return {
        "ok": True,
        "message": f"Bulk upload complete: {total} items processed",
        "results": results
    }


@router.get("/bulk-upload/template")
async def get_bulk_upload_template(
    request: Request,
    x_admin_token: str = Header(None)
):
    """Return a JSON template for bulk upload"""
    db = await get_db(request)
    if not await verify_admin_token_async(x_admin_token, db):
        raise HTTPException(status_code=401, detail="Unauthorized")

    template = {
        "_instructions": "Fill in this template and upload via Bulk Upload. All IDs must be unique. Tiles auto-link to the category if category_id is omitted from tiles.",
        "category": {
            "category_id": "my-category",
            "title": "My Category Name",
            "helper_copy": "Short description of what this category covers",
            "order": 1,
            "active": True
        },
        "tiles": [
            {
                "tile_id": "my-tile-1",
                "short_title": "Tile 1",
                "full_title": "Full Title for Tile 1",
                "icon_type": "star",
                "order": 1,
                "active": True,
                "linked_package_id": "my-package-1"
            },
            {
                "tile_id": "my-tile-2",
                "short_title": "Tile 2",
                "full_title": "Full Title for Tile 2",
                "icon_type": "heart",
                "order": 2,
                "active": True,
                "linked_package_id": "my-package-2"
            }
        ],
        "packages": [
            {
                "tier_id": "my-package-1",
                "name": "Package 1 Name",
                "price": 1999,
                "duration_days": 7,
                "features": [
                    "Feature 1",
                    "Feature 2",
                    "Feature 3"
                ],
                "description": "Short description for listings",
                "active": True,
                "content": {
                    "hero_title": "Package 1 Headline",
                    "hero_subtitle": "A compelling subtitle that explains the value",
                    "trust_line": "Senior experts . Unlimited follow-ups . Private & secure",
                    "overview_title": "7-Day Guidance",
                    "overview_description": "What the user gets in detail",
                    "includes": [
                        "1 structured analysis",
                        "Unlimited chat for 7 days",
                        "Written summary within 24 hours"
                    ],
                    "help_sections": [
                        {
                            "title": "CLARITY",
                            "items": [
                                "Question 1 this helps answer",
                                "Question 2 this helps answer"
                            ]
                        },
                        {
                            "title": "TIMELINE",
                            "items": [
                                "When to act",
                                "Key timing windows"
                            ]
                        }
                    ],
                    "analysis_intro": "Your guidance is based on structured analysis, not guesswork.",
                    "analysis_sections": [
                        {
                            "title": "We look at:",
                            "items": [
                                "Analysis point 1",
                                "Analysis point 2"
                            ]
                        }
                    ],
                    "deliverables": [
                        "Clear direction summary",
                        "A timing window table",
                        "Unlimited topic-specific chat for 7 days"
                    ]
                }
            }
        ]
    }

    return {"ok": True, "template": template}

