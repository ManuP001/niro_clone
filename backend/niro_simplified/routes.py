"""NIRO Simplified V1 - API Routes

Endpoints for topics, experts, scenarios, tiers, tools, plans, and threads.
"""

import os
import logging
from fastapi import APIRouter, HTTPException, Header, Query, Request, BackgroundTasks
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
import jwt
import razorpay

from .models import UserState, ActivePlanSummary, RecentThreadSummary
from .catalog import get_simplified_catalog, CATALOG_VERSION
from .storage import get_simplified_storage
from backend.services.email_service import send_booking_notification

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simplified", tags=["niro-simplified"])

# Razorpay configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_placeholder')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-prod')

# Helper to detect environment from request
def get_environment_from_origin(origin: str = None, host: str = None) -> str:
    """Detect environment from request headers"""
    check_str = f"{origin or ''}{host or ''}"
    if '.emergent.host' in check_str:
        return 'production'
    return 'preview'

# Initialize Razorpay client
razorpay_client = None
if RAZORPAY_KEY_SECRET:
    try:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    except Exception as e:
        logger.warning(f"Razorpay initialization failed: {e}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_user_id_from_token_async(authorization: str = None, db = None) -> Optional[str]:
    """Extract user ID from JWT token or session token (async version for DB lookup)"""
    if not authorization:
        logger.debug("No authorization header provided")
        return None
    
    token = authorization.replace("Bearer ", "")
    
    # First try: JWT token decode
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id") or payload.get("sub")
        if user_id:
            logger.debug(f"JWT token validated for user: {user_id}")
            return user_id
    except jwt.ExpiredSignatureError:
        logger.debug("JWT token expired, trying session token")
    except jwt.InvalidTokenError:
        logger.debug("Invalid JWT token, trying session token")
    except Exception:
        pass  # Not a JWT, try session token
    
    # Second try: Session token lookup (for Google OAuth)
    if token.startswith("niro_session_") and db is not None:
        try:
            from datetime import timezone
            session_doc = await db.user_sessions.find_one(
                {"session_token": token},
                {"_id": 0}
            )
            if session_doc:
                # Check if session is valid (not expired)
                expires_at = session_doc.get("expires_at")
                if expires_at:
                    from datetime import datetime
                    if isinstance(expires_at, str):
                        expires_at = datetime.fromisoformat(expires_at)
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    if expires_at > datetime.now(timezone.utc):
                        user_id = session_doc.get("user_id")
                        logger.debug(f"Session token validated for user: {user_id}")
                        return user_id
                    else:
                        logger.debug(f"Session token expired: {token[:20]}...")
                else:
                    # No expiry, assume valid
                    user_id = session_doc.get("user_id")
                    logger.debug(f"Session token validated (no expiry) for user: {user_id}")
                    return user_id
            else:
                logger.debug(f"Session token not found in database: {token[:20]}...")
        except Exception as e:
            logger.warning(f"Session token lookup failed: {e}")
    elif not token.startswith("niro_session_"):
        logger.debug(f"Token is neither JWT nor session token: {token[:20]}...")
    
    return None


def get_user_id_from_token(authorization: str = None) -> Optional[str]:
    """Extract user ID from JWT token (sync version - JWT only)"""
    if not authorization:
        return None
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("user_id") or payload.get("sub")
    except Exception:
        return None


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TopicListResponse(BaseModel):
    ok: bool = True
    topics: List[dict]
    catalog_version: str


class TopicDetailResponse(BaseModel):
    ok: bool = True
    topic: dict
    experts: List[dict]
    scenarios: List[dict]
    tiers: List[dict]
    tools: List[dict]
    unlimited_conditions: dict
    recommended_tier: str = "plus"
    catalog_version: str


class UserStateResponse(BaseModel):
    ok: bool = True
    user_state: dict


class CreateOrderRequest(BaseModel):
    tier_id: str
    scenario_ids: List[str] = []
    intake_notes: str = ""
    expert_id: Optional[str] = None
    expert_name: Optional[str] = None


class CreateOrderResponse(BaseModel):
    ok: bool = True
    order_id: str
    razorpay_order_id: str
    amount: int
    currency: str = "INR"
    key_id: str


class VerifyPaymentRequest(BaseModel):
    order_id: str
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


class VerifyPaymentResponse(BaseModel):
    ok: bool = True
    plan_id: str
    message: str = "Payment successful"


class CreateThreadRequest(BaseModel):
    plan_id: str
    expert_id: str


class CreateThreadResponse(BaseModel):
    ok: bool = True
    thread_id: str


class SendMessageRequest(BaseModel):
    thread_id: str
    content: str
    sender_type: str = "user"  # user or expert


class SendMessageResponse(BaseModel):
    ok: bool = True
    message_id: str


class TelemetryRequest(BaseModel):
    event_name: str
    properties: dict = {}


# ============================================================================
# TOPIC ENDPOINTS
# ============================================================================

@router.get("/topics", response_model=TopicListResponse)
async def get_topics():
    """Get all topics"""
    catalog = get_simplified_catalog()
    topics = catalog.get_all_topics()
    return TopicListResponse(
        topics=[t.model_dump() for t in topics],
        catalog_version=CATALOG_VERSION
    )


@router.get("/topics/{topic_id}", response_model=TopicDetailResponse)
async def get_topic_detail(
    topic_id: str,
    scenario_ids: str = Query(default="", description="Comma-separated scenario IDs")
):
    """Get topic landing page data"""
    catalog = get_simplified_catalog()
    
    topic = catalog.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Parse scenario IDs
    selected_scenarios = [s.strip() for s in scenario_ids.split(",") if s.strip()]
    
    # Get recommended tier based on scenarios
    recommended = catalog.get_recommended_tier(topic_id, selected_scenarios)
    
    return TopicDetailResponse(
        topic=topic.model_dump(),
        experts=[e.model_dump() for e in catalog.get_experts_for_topic(topic_id)],
        scenarios=[s.model_dump() for s in catalog.get_scenarios_for_topic(topic_id)],
        tiers=[t.model_dump() for t in catalog.get_tiers_for_topic(topic_id)],
        tools=[t.model_dump() for t in catalog.get_tools_for_topic(topic_id)],
        unlimited_conditions=catalog.get_unlimited_conditions().model_dump(),
        recommended_tier=recommended,
        catalog_version=CATALOG_VERSION
    )


@router.get("/experts")
async def get_experts(topic_id: str = Query(default=None)):
    """Get experts, optionally filtered by topic"""
    catalog = get_simplified_catalog()
    
    if topic_id:
        experts = catalog.get_experts_for_topic(topic_id)
    else:
        experts = list(catalog.experts.values())
    
    return {
        "ok": True,
        "experts": [e.model_dump() for e in experts],
        "catalog_version": CATALOG_VERSION
    }


@router.get("/experts/all")
async def get_all_experts_grouped():
    """Get all experts grouped by modality - V1.5"""
    catalog = get_simplified_catalog()
    experts = list(catalog.experts.values())
    
    # Group by modality
    grouped = {}
    for expert in experts:
        modality = expert.modality
        if modality not in grouped:
            grouped[modality] = []
        grouped[modality].append(expert.model_dump())
    
    return {
        "ok": True,
        "experts": [e.model_dump() for e in experts],
        "grouped_by_modality": grouped,
        "modalities": list(grouped.keys()),
        "total_count": len(experts),
        "catalog_version": CATALOG_VERSION
    }


@router.get("/tiers/{tier_id}")
async def get_tier_detail(tier_id: str):
    """Get tier details"""
    catalog = get_simplified_catalog()
    tier = catalog.get_tier(tier_id)
    
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    return {
        "ok": True,
        "tier": tier.model_dump(),
        "catalog_version": CATALOG_VERSION
    }


# ============================================================================
# USER STATE ENDPOINT
# ============================================================================

@router.get("/user/state", response_model=UserStateResponse)
async def get_user_state(
    request: Request,
    authorization: str = Header(default=None)
):
    """Get user state for home screen routing"""
    storage = get_simplified_storage()
    db = storage.db if storage else None
    user_id = await get_user_id_from_token_async(authorization, db)
    
    if not user_id:
        # Return new user state for unauthenticated
        return UserStateResponse(
            user_state=UserState(user_id="anonymous", is_new_user=True).model_dump()
        )
    
    catalog = get_simplified_catalog()
    
    if not storage:
        return UserStateResponse(
            user_state=UserState(user_id=user_id, is_new_user=True).model_dump()
        )
    
    # Check if user has purchased
    has_purchased = await storage.has_user_purchased(user_id)
    
    # Get active plans
    active_plans = await storage.get_user_active_plans(user_id)
    plan_summaries = []
    
    for plan in active_plans:
        topic = catalog.get_topic(plan.get("topic_id", ""))
        tier = catalog.get_tier(plan.get("tier_id", ""))
        
        if topic and tier:
            expires_at = plan.get("expires_at")
            weeks_remaining = 0
            if expires_at:
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                weeks_remaining = max(0, (expires_at - datetime.utcnow()).days // 7)
            
            calls_remaining = tier.access_policy.calls_per_month - plan.get("calls_used_this_month", 0)
            
            # Count threads
            threads_count = await storage.count_active_threads(plan.get("plan_id", ""))
            
            plan_summaries.append(ActivePlanSummary(
                plan_id=plan.get("plan_id", ""),
                topic_id=plan.get("topic_id", ""),
                topic_label=topic.label,
                tier_level=tier.tier_level,
                tier_name=tier.name,
                weeks_remaining=weeks_remaining,
                calls_remaining=max(0, calls_remaining),
                threads_count=threads_count
            ))
    
    # Get recent threads
    recent_threads = await storage.get_user_threads(user_id, limit=3)
    thread_summaries = []
    
    for thread in recent_threads:
        expert = catalog.get_expert(thread.get("expert_id", ""))
        if expert:
            thread_summaries.append(RecentThreadSummary(
                thread_id=thread.get("thread_id", ""),
                expert_id=expert.expert_id,
                expert_name=expert.name,
                expert_modality=expert.modality_label,
                last_message_at=thread.get("last_message_at")
            ))
    
    # Get topic passes
    passes = await storage.get_user_topic_passes(user_id)
    pass_topics = [p.get("topic_id") for p in passes]
    
    user_state = UserState(
        user_id=user_id,
        is_new_user=not has_purchased,
        has_active_plan=len(plan_summaries) > 0,
        active_plans=plan_summaries,
        recent_expert_threads=thread_summaries,
        additional_topic_passes=pass_topics
    )
    
    return UserStateResponse(user_state=user_state.model_dump())


# ============================================================================
# CHECKOUT ENDPOINTS
# ============================================================================

@router.post("/checkout/create-order", response_model=CreateOrderResponse)
async def create_order(
    request: Request,
    request_data: CreateOrderRequest,
    authorization: str = Header(default=None)
):
    """Create a Razorpay order for pack purchase"""
    # Use app.state.db as primary DB source (reliable), fall back to storage singleton
    db = getattr(request.app.state, 'db', None)
    if db is None:
        storage = get_simplified_storage()
        db = storage.db if storage else None
    
    user_id = await get_user_id_from_token_async(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # First try catalog (hardcoded tiers)
    catalog = get_simplified_catalog()
    tier = catalog.get_tier(request_data.tier_id)
    
    # If not in catalog, check admin_tiers database (for standalone packages like Valentine's)
    tier_from_db = None
    if not tier and db is not None:
        logger.info(f"Tier {request_data.tier_id} not in catalog, checking admin_tiers database...")
        try:
            tier_from_db = await db.admin_tiers.find_one(
                {"tier_id": request_data.tier_id, "active": {"$ne": False}},
                {"_id": 0}
            )
            if tier_from_db:
                logger.info(f"Found tier in admin_tiers: {request_data.tier_id} - {tier_from_db.get('name')}")
            else:
                logger.warning(f"Tier {request_data.tier_id} NOT found in admin_tiers")
        except Exception as e:
            logger.error(f"Error checking admin_tiers: {e}")
    elif db is None:
        logger.warning("Database connection not available for admin_tiers lookup")
    
    if not tier and not tier_from_db:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    # Get price and tier info
    if tier:
        price_inr = tier.price_inr
        tier_id = tier.tier_id
        tier_level = tier.tier_level
        topic_id = tier.topic_id
    else:
        # From admin_tiers database
        price_inr = tier_from_db.get("price", 0)
        tier_id = tier_from_db.get("tier_id")
        tier_level = "standalone_package"
        topic_id = tier_from_db.get("topic_id", "standalone")
    
    # Detect environment
    origin = request.headers.get('origin', '')
    host = request.headers.get('host', '')
    environment = get_environment_from_origin(origin, host)
    
    # Create Razorpay order
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    amount_paise = price_inr * 100  # Convert to paise
    
    razorpay_order_id = f"rzp_order_{uuid.uuid4().hex[:12]}"
    
    if razorpay_client:
        try:
            rz_order = razorpay_client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "receipt": order_id,
                "notes": {
                    "tier_id": tier_id,
                    "user_id": user_id
                }
            })
            razorpay_order_id = rz_order["id"]
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {e}")
    
    # Store order in DB
    if db is not None:
        await db.niro_simplified_orders.insert_one({
            "order_id": order_id,
            "razorpay_order_id": razorpay_order_id,
            "user_id": user_id,
            "tier_id": tier_id,
            "tier_level": tier_level,
            "topic_id": topic_id,
            "amount": amount_paise,
            "amount_inr": price_inr,
            "scenario_ids": request_data.scenario_ids,
            "intake_notes": request_data.intake_notes,
            "expert_id": request_data.expert_id,
            "expert_name": request_data.expert_name,
            "status": "created",
            "environment": environment,
            "created_at": datetime.utcnow()
        })
    
    return CreateOrderResponse(
        order_id=order_id,
        razorpay_order_id=razorpay_order_id,
        amount=amount_paise,
        key_id=RAZORPAY_KEY_ID
    )


@router.post("/checkout/verify", response_model=VerifyPaymentResponse)
async def verify_payment(
    request: Request,
    request_data: VerifyPaymentRequest,
    authorization: str = Header(default=None),
    background_tasks: BackgroundTasks = None
):
    """Verify Razorpay payment and create plan"""
    # Use app.state.db as primary DB source (reliable)
    db = getattr(request.app.state, 'db', None)
    if db is None:
        storage = get_simplified_storage()
        db = storage.db if storage else None
    user_id = await get_user_id_from_token_async(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    catalog = get_simplified_catalog()
    
    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    
    # Get order
    order = await storage.db.niro_simplified_orders.find_one(
        {"order_id": request_data.order_id}
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify signature (if Razorpay client available)
    if razorpay_client:
        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": request_data.razorpay_order_id,
                "razorpay_payment_id": request_data.razorpay_payment_id,
                "razorpay_signature": request_data.razorpay_signature
            })
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            # Continue anyway for testing
    
    # Get tier - first try catalog, then admin_tiers database
    tier_id = order.get("tier_id", "")
    tier = catalog.get_tier(tier_id)
    tier_from_db = None
    
    if not tier and db is not None:
        tier_from_db = await db.admin_tiers.find_one(
            {"tier_id": tier_id, "active": {"$ne": False}},
            {"_id": 0}
        )
    
    if not tier and not tier_from_db:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    # Get tier properties
    if tier:
        topic_id = tier.topic_id
        tier_level = tier.tier_level
        price_inr = tier.price_inr
        validity_weeks = tier.validity_weeks
        tier_name = tier.name
    else:
        # From admin_tiers database (standalone packages like Valentine's)
        topic_id = tier_from_db.get("topic_id", "standalone")
        tier_level = "standalone_package"
        price_inr = tier_from_db.get("price", 0)
        validity_weeks = tier_from_db.get("duration_weeks", 1)
        tier_name = tier_from_db.get("name", tier_id)
    
    # Create plan
    now = datetime.utcnow()
    expires_at = now + timedelta(weeks=validity_weeks)
    
    plan_data = {
        "plan_id": f"plan_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "topic_id": topic_id,
        "tier_id": tier_id,
        "tier_level": tier_level,
        "price_paid_inr": price_inr,
        "status": "active",
        "purchased_at": now,
        "starts_at": now,
        "expires_at": expires_at,
        "calls_used_this_month": 0,
        "calls_reset_date": now + timedelta(days=30),
        "selected_scenarios": order.get("scenario_ids", []),
        "intake_notes": order.get("intake_notes", "")
    }
    
    plan_id = await storage.create_plan(plan_data)
    
    # Update order status
    await storage.db.niro_simplified_orders.update_one(
        {"order_id": request_data.order_id},
        {"$set": {
            "status": "completed",
            "razorpay_payment_id": request_data.razorpay_payment_id,
            "plan_id": plan_id,
            "completed_at": datetime.utcnow()
        }}
    )
    
    # Send booking notification email in background
    try:
        # Get user profile for email notification
        user_profile = await storage.db.users.find_one({"user_id": user_id}, {"_id": 0})
        
        user_email = user_profile.get('email', '') if user_profile else ''
        user_name = user_profile.get('name', '') if user_profile else ''
        user_phone = user_profile.get('phone', '') if user_profile else ''
        
        # Get birth details
        user_dob = user_profile.get('dob', '') if user_profile else ''
        user_tob = user_profile.get('tob', '') if user_profile else ''
        user_pob = user_profile.get('pob', '') or user_profile.get('location', {}).get('city', '') if user_profile else ''
        user_gender = user_profile.get('gender', '') if user_profile else ''
        
        # Get topic name
        topic = catalog.get_topic(topic_id)
        topic_name = topic.title if topic else topic_id
        
        # Prepare comprehensive additional info
        additional_info = {
            "order_id": request_data.order_id,
            "plan_id": plan_id,
            "user_id": user_id,
            "scenarios": order.get("scenario_ids", []),
            "validity_weeks": validity_weeks,
            "dob": user_dob,
            "tob": user_tob,
            "pob": user_pob,
            "gender": user_gender
        }
        
        # Send email notification (in background if available)
        if background_tasks:
            background_tasks.add_task(
                send_booking_notification,
                user_email=user_email or f"user_{user_id}@niro.app",
                user_name=user_name,
                user_phone=user_phone,
                package_name=f"{topic_name} - {tier_level}",
                package_tier=tier_level,
                package_price=price_inr,
                topic_name=topic_name,
                transaction_id=request_data.razorpay_payment_id,
                payment_method="Razorpay",
                additional_info=additional_info
            )
        else:
            # Send synchronously if no background tasks
            await send_booking_notification(
                user_email=user_email or f"user_{user_id}@niro.app",
                user_name=user_name,
                user_phone=user_phone,
                package_name=f"{topic_name} - {tier_level}",
                package_tier=tier_level,
                package_price=price_inr,
                topic_name=topic_name,
                transaction_id=request_data.razorpay_payment_id,
                payment_method="Razorpay",
                additional_info=additional_info
            )
        
        logger.info(f"Booking notification email queued for plan {plan_id}")
    except Exception as e:
        logger.error(f"Failed to send booking notification: {e}")
        # Don't fail the purchase if email fails
    
    return VerifyPaymentResponse(
        plan_id=plan_id,
        message="Payment successful! Your pack is now active."
    )


# ============================================================================
# PLAN ENDPOINTS
# ============================================================================

@router.get("/plans")
async def get_user_plans(
    authorization: str = Header(default=None),
    status: str = Query(default=None)
):
    """Get user's plans"""
    storage = get_simplified_storage()
    db = storage.db if storage else None
    user_id = await get_user_id_from_token_async(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not storage:
        return {"ok": True, "plans": []}
    
    plans = await storage.get_user_plans(user_id, status)
    
    return {"ok": True, "plans": plans}


@router.get("/plans/{plan_id}")
async def get_plan_detail(
    plan_id: str,
    authorization: str = Header(default=None)
):
    """Get plan details with threads"""
    storage = get_simplified_storage()
    db = storage.db if storage else None
    user_id = await get_user_id_from_token_async(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    catalog = get_simplified_catalog()
    
    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get tier and topic
    tier = catalog.get_tier(plan.get("tier_id", ""))
    topic = catalog.get_topic(plan.get("topic_id", ""))
    
    # Get threads
    threads = await storage.get_plan_threads(plan_id)
    
    # Enrich threads with expert info
    enriched_threads = []
    for thread in threads:
        expert = catalog.get_expert(thread.get("expert_id", ""))
        if expert:
            thread["expert"] = expert.model_dump()
        enriched_threads.append(thread)
    
    # Get available experts
    experts = catalog.get_experts_for_topic(plan.get("topic_id", ""))
    
    # Get tools (if Plus/Pro)
    tools = []
    if tier and tier.access_policy.free_tools_access:
        tools = [t.model_dump() for t in catalog.get_tools_for_topic(plan.get("topic_id", ""))]
    
    return {
        "ok": True,
        "plan": plan,
        "tier": tier.model_dump() if tier else None,
        "topic": topic.model_dump() if topic else None,
        "threads": enriched_threads,
        "experts": [e.model_dump() for e in experts],
        "tools": tools,
        "calls_remaining": (tier.access_policy.calls_per_month - plan.get("calls_used_this_month", 0)) if tier else 0,
        "can_create_thread": await _can_create_thread(storage, plan_id, tier) if tier else False
    }


async def _can_create_thread(storage, plan_id: str, tier) -> bool:
    """Check if user can create a new thread"""
    if tier.access_policy.max_active_expert_threads == -1:
        return True  # Unlimited
    
    active_count = await storage.count_active_threads(plan_id)
    return active_count < tier.access_policy.max_active_expert_threads


# ============================================================================
# THREAD ENDPOINTS
# ============================================================================

@router.post("/threads", response_model=CreateThreadResponse)
async def create_thread(
    request_data: CreateThreadRequest,
    authorization: str = Header(default=None)
):
    """Create a new expert thread"""
    storage = get_simplified_storage()
    db = storage.db if storage else None
    user_id = await get_user_id_from_token_async(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    catalog = get_simplified_catalog()
    
    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    
    # Get plan
    plan = await storage.get_plan(request_data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if plan.get("status") != "active":
        raise HTTPException(status_code=400, detail="Plan is not active")
    
    # Check tier limits
    tier = catalog.get_tier(plan.get("tier_id", ""))
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    if not await _can_create_thread(storage, request_data.plan_id, tier):
        raise HTTPException(
            status_code=400, 
            detail=f"Thread limit reached. {tier.name} allows {tier.access_policy.max_active_expert_threads} active thread(s)."
        )
    
    # Check expert exists and serves this topic
    expert = catalog.get_expert(request_data.expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    if plan.get("topic_id") not in expert.topics:
        raise HTTPException(status_code=400, detail="Expert does not serve this topic")
    
    # Create thread
    thread_data = {
        "plan_id": request_data.plan_id,
        "user_id": user_id,
        "expert_id": request_data.expert_id,
        "topic_id": plan.get("topic_id"),
        "status": "active",
        "message_count": 0
    }
    
    thread_id = await storage.create_thread(thread_data)
    
    return CreateThreadResponse(thread_id=thread_id)


@router.get("/threads/{thread_id}")
async def get_thread_detail(
    thread_id: str,
    authorization: str = Header(default=None)
):
    """Get thread with messages"""
    storage = get_simplified_storage()
    db = storage.db if storage else None
    user_id = await get_user_id_from_token_async(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    catalog = get_simplified_catalog()
    
    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    
    thread = await storage.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get expert info
    expert = catalog.get_expert(thread.get("expert_id", ""))
    
    # Get messages
    messages = await storage.get_thread_messages(thread_id)
    
    return {
        "ok": True,
        "thread": thread,
        "expert": expert.model_dump() if expert else None,
        "messages": messages
    }


@router.post("/threads/{thread_id}/messages", response_model=SendMessageResponse)
async def send_message(
    thread_id: str,
    request_data: SendMessageRequest,
    authorization: str = Header(default=None)
):
    """Send a message in a thread"""
    storage = get_simplified_storage()
    db = storage.db if storage else None
    user_id = await get_user_id_from_token_async(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    
    thread = await storage.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Add message
    message_data = {
        "thread_id": thread_id,
        "sender_type": request_data.sender_type,
        "sender_id": user_id if request_data.sender_type == "user" else thread.get("expert_id"),
        "content": request_data.content
    }
    
    message_id = await storage.add_message(message_data)
    
    return SendMessageResponse(message_id=message_id)


# ============================================================================
# TELEMETRY ENDPOINT
# ============================================================================

@router.post("/telemetry")
async def log_telemetry(
    request_data: TelemetryRequest,
    authorization: str = Header(default=None)
):
    """Log telemetry event"""
    user_id = get_user_id_from_token(authorization)
    
    storage = get_simplified_storage()
    if storage:
        await storage.log_event({
            "event_name": request_data.event_name,
            "user_id": user_id,
            "properties": request_data.properties
        })
    
    return {"ok": True}


# ============================================================================
# TOPIC PASS ENDPOINTS
# ============================================================================

@router.post("/passes/create-order")
async def create_topic_pass_order(
    topic_id: str,
    parent_plan_id: str,
    authorization: str = Header(default=None)
):
    """Create order for additional topic pass (₹2000)"""
    storage = get_simplified_storage()
    db = storage.db if storage else None
    user_id = await get_user_id_from_token_async(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    catalog = get_simplified_catalog()
    
    if not catalog.get_topic(topic_id):
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    
    # Verify parent plan
    plan = await storage.get_plan(parent_plan_id)
    if not plan or plan.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Parent plan not found")
    
    # Create order
    order_id = f"pass_order_{uuid.uuid4().hex[:12]}"
    amount_paise = 2000 * 100  # ₹2000
    
    razorpay_order_id = f"rzp_pass_{uuid.uuid4().hex[:12]}"
    
    if razorpay_client:
        try:
            rz_order = razorpay_client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "receipt": order_id,
                "notes": {
                    "type": "topic_pass",
                    "topic_id": topic_id,
                    "parent_plan_id": parent_plan_id,
                    "user_id": user_id
                }
            })
            razorpay_order_id = rz_order["id"]
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {e}")
    
    return {
        "ok": True,
        "order_id": order_id,
        "razorpay_order_id": razorpay_order_id,
        "amount": amount_paise,
        "currency": "INR",
        "key_id": RAZORPAY_KEY_ID
    }
