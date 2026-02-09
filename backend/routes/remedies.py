"""
Remedies Purchase API Routes
Handles remedy purchases with Razorpay integration
"""

import os
import uuid
import hmac
import hashlib
import razorpay
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Header, Request, BackgroundTasks
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/remedies", tags=["Remedies"])

# Razorpay client
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')

razorpay_client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    logger.info("Razorpay client initialized for remedies")

# Remedy catalog (same as frontend)
REMEDIES_CATALOG = {
    "chakra_balance": {"name": "Chakra Balance Program (3 Sessions)", "price": 3500, "category": "healing"},
    "santan_pooja": {"name": "Santan / Fertility Pooja", "price": 2499, "category": "pooja"},
    "shanti_pooja": {"name": "Shanti / Peace Pooja", "price": 1999, "category": "pooja"},
    "lakshmi_pooja": {"name": "Lakshmi Prosperity Pooja", "price": 2499, "category": "pooja"},
    "obstacle_removal": {"name": "Obstacle Removal Pooja", "price": 1999, "category": "pooja"},
    "gemstone_career": {"name": "Career & Abundance Gemstone", "price": 1499, "category": "gemstone"},
    "gemstone_calm": {"name": "Calm & Grounding Gemstone", "price": 1499, "category": "gemstone"},
    "gemstone_relationship": {"name": "Relationship Harmony Gemstone", "price": 1499, "category": "gemstone"},
    "stress_sleep_kit": {"name": "Stress & Sleep Kit", "price": 899, "category": "kit"},
    "protection_kit": {"name": "Protection Kit", "price": 799, "category": "kit"},
    "prosperity_kit": {"name": "Prosperity Kit", "price": 999, "category": "kit"},
    "vitality_kit": {"name": "Vitality Kit", "price": 799, "category": "kit"},
    "venus_harmony": {"name": "Venus Harmony Ritual", "price": 999, "category": "ritual"},
    "mercury_focus": {"name": "Mercury Focus Ritual", "price": 799, "category": "ritual"},
    "moon_calm": {"name": "Moon-Mercury Calm Ritual", "price": 899, "category": "ritual"},
}

def get_environment_from_request(request: Request) -> str:
    """Detect environment from request host"""
    host = request.headers.get('host', '')
    origin = request.headers.get('origin', '')
    if '.emergent.host' in host or '.emergent.host' in origin:
        return 'production'
    return 'preview'

def get_user_id_from_token(authorization: str) -> Optional[str]:
    """Extract user_id from authorization header"""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if token.startswith("user_"):
        return token
    if token.startswith("niro_session_"):
        return None  # Session-based auth handled separately
    return None

async def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Get database from app state"""
    return request.app.state.db

async def get_user_from_session(request: Request, db: AsyncIOMotorDatabase) -> Optional[Dict]:
    """Get user from session cookie or auth header"""
    # Try cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        return None
    
    # Find session
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        return None
    
    # Get user
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    return user


# ============================================================================
# MODELS
# ============================================================================

class CreateRemedyOrderRequest(BaseModel):
    remedy_id: str
    expert_id: Optional[str] = None
    expert_name: Optional[str] = None
    plan_id: Optional[str] = None
    source: str = "direct"  # direct or expert_recommended
    notes: Optional[str] = None
    delivery_address: Optional[Dict[str, str]] = None

class CreateRemedyOrderResponse(BaseModel):
    ok: bool
    remedy_order_id: str
    razorpay_order_id: str
    amount: int
    currency: str
    key_id: str

class VerifyRemedyPaymentRequest(BaseModel):
    remedy_order_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class VerifyRemedyPaymentResponse(BaseModel):
    ok: bool
    remedy_order_id: str
    message: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/catalog")
async def get_remedies_catalog():
    """Get available remedies catalog"""
    remedies = []
    for remedy_id, data in REMEDIES_CATALOG.items():
        remedies.append({
            "remedy_id": remedy_id,
            "name": data["name"],
            "price": data["price"],
            "category": data["category"]
        })
    return {"ok": True, "remedies": remedies}


@router.post("/create-order", response_model=CreateRemedyOrderResponse)
async def create_remedy_order(
    request: Request,
    req: CreateRemedyOrderRequest,
    authorization: str = Header(default=None)
):
    """Create a Razorpay order for remedy purchase"""
    if not razorpay_client:
        raise HTTPException(status_code=500, detail="Payment gateway not configured")
    
    db = await get_db(request)
    
    # Get user
    user = await get_user_from_session(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = user.get("user_id")
    
    # Validate remedy
    if req.remedy_id not in REMEDIES_CATALOG:
        raise HTTPException(status_code=400, detail="Invalid remedy ID")
    
    remedy = REMEDIES_CATALOG[req.remedy_id]
    price_inr = remedy["price"]
    amount_paise = price_inr * 100
    
    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"remedy_{uuid.uuid4().hex[:12]}",
            "notes": {
                "user_id": user_id,
                "remedy_id": req.remedy_id,
                "source": req.source
            }
        })
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment order")
    
    # Create remedy order in DB
    remedy_order_id = f"rem_{uuid.uuid4().hex[:12]}"
    environment = get_environment_from_request(request)
    
    remedy_order = {
        "remedy_order_id": remedy_order_id,
        "user_id": user_id,
        "remedy_id": req.remedy_id,
        "remedy_name": remedy["name"],
        "remedy_category": remedy["category"],
        "price_inr": price_inr,
        "expert_id": req.expert_id,
        "expert_name": req.expert_name,
        "plan_id": req.plan_id,
        "source": req.source,
        "notes": req.notes,
        "delivery_address": req.delivery_address,
        "razorpay_order_id": razorpay_order["id"],
        "status": "pending",
        "environment": environment,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.niro_remedy_orders.insert_one(remedy_order)
    logger.info(f"Remedy order created: {remedy_order_id} for {req.remedy_id}")
    
    return CreateRemedyOrderResponse(
        ok=True,
        remedy_order_id=remedy_order_id,
        razorpay_order_id=razorpay_order["id"],
        amount=amount_paise,
        currency="INR",
        key_id=RAZORPAY_KEY_ID
    )


@router.post("/verify-payment", response_model=VerifyRemedyPaymentResponse)
async def verify_remedy_payment(
    request: Request,
    req: VerifyRemedyPaymentRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(default=None)
):
    """Verify Razorpay payment and activate remedy order"""
    if not razorpay_client:
        raise HTTPException(status_code=500, detail="Payment gateway not configured")
    
    db = await get_db(request)
    
    # Get user
    user = await get_user_from_session(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get remedy order
    remedy_order = await db.niro_remedy_orders.find_one(
        {"remedy_order_id": req.remedy_order_id},
        {"_id": 0}
    )
    
    if not remedy_order:
        raise HTTPException(status_code=404, detail="Remedy order not found")
    
    if remedy_order.get("status") == "paid":
        return VerifyRemedyPaymentResponse(
            ok=True,
            remedy_order_id=req.remedy_order_id,
            message="Payment already verified"
        )
    
    # Verify signature
    try:
        signature_payload = f"{req.razorpay_order_id}|{req.razorpay_payment_id}"
        expected_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            signature_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if expected_signature != req.razorpay_signature:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
    except Exception as e:
        logger.error(f"Signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    # Update remedy order
    await db.niro_remedy_orders.update_one(
        {"remedy_order_id": req.remedy_order_id},
        {
            "$set": {
                "status": "paid",
                "razorpay_payment_id": req.razorpay_payment_id,
                "paid_at": datetime.now(timezone.utc)
            }
        }
    )
    
    logger.info(f"Remedy payment verified: {req.remedy_order_id}")
    
    # Send notification email (background task)
    try:
        from backend.services.email_service import send_booking_notification
        
        user_email = user.get("email", "")
        user_name = user.get("name", "")
        
        background_tasks.add_task(
            send_booking_notification,
            user_email=user_email,
            user_name=user_name,
            user_phone=None,
            package_name=f"Remedy: {remedy_order.get('remedy_name')}",
            package_tier=remedy_order.get("remedy_category", "remedy"),
            package_price=remedy_order.get("price_inr", 0),
            topic_name="Remedy Purchase",
            transaction_id=req.razorpay_payment_id,
            payment_method="Razorpay",
            additional_info={
                "remedy_order_id": req.remedy_order_id,
                "remedy_id": remedy_order.get("remedy_id"),
                "source": remedy_order.get("source"),
                "expert_name": remedy_order.get("expert_name"),
                "user_id": user.get("user_id"),
                "dob": user.get("dob"),
                "tob": user.get("tob"),
                "pob": user.get("pob"),
                "gender": user.get("gender")
            }
        )
    except Exception as e:
        logger.error(f"Failed to queue remedy notification email: {e}")
    
    return VerifyRemedyPaymentResponse(
        ok=True,
        remedy_order_id=req.remedy_order_id,
        message="Payment successful! Your remedy order is confirmed."
    )


@router.get("/my-orders")
async def get_my_remedy_orders(
    request: Request,
    authorization: str = Header(default=None)
):
    """Get user's remedy orders"""
    db = await get_db(request)
    
    user = await get_user_from_session(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = user.get("user_id")
    
    orders = await db.niro_remedy_orders.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return {"ok": True, "orders": orders}
