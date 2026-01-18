"""NIRO V2 API Routes

Endpoints for packages, remedies, recommendations, checkout, and plans.
Now with MongoDB persistence, real Razorpay, and chat integration.
"""

import os
import logging
from fastapi import APIRouter, HTTPException, Header, Query, Depends, Request
from typing import Optional, List
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field
import uuid
import jwt

from .models import (
    Topic, Branch, Urgency, DecisionOwnership, RemedyCategory,
    SituationIntake, UserPlan, UserPlanTask, UserRemedyAddon,
    PlanStatus, TaskStatus, FulfillmentStatus,
    StepAExtraction, StepBRecommendation, ChartInsight,
    ValidatedRecommendation, BirthDetails, UserContext, ChartSummary
)
from .catalog import get_catalog_service, CATALOG_VERSION
from .recommendation_engine import get_recommendation_engine, PROMPT_VERSION
from .telemetry import get_telemetry_service
from .payment_service import get_payment_service
from .storage import get_niro_v2_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["niro-v2"])

# Consultation booking URL from environment
CONSULTATION_BOOKING_URL = os.environ.get(
    'CONSULTATION_BOOKING_URL', 
    'https://calendar.app.google/GJMg3Btky7cwdaYf9'
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class IntakeRequest(BaseModel):
    topic: str
    urgency: str
    desired_outcome: str
    decision_ownership: str


class IntakeResponse(BaseModel):
    ok: bool
    intake_id: str
    session_ready: bool


class PackageListResponse(BaseModel):
    ok: bool
    packages: List[dict]
    catalog_version: str


class PackageDetailResponse(BaseModel):
    ok: bool
    package: dict
    catalog_version: str


class RemedyListResponse(BaseModel):
    ok: bool
    remedies: List[dict]
    catalog_version: str


class RemedyDetailResponse(BaseModel):
    ok: bool
    remedy: dict
    catalog_version: str


class RecommendationRequest(BaseModel):
    intake_id: Optional[str] = None
    # Or provide directly:
    topic: Optional[str] = None
    urgency: Optional[str] = None
    desired_outcome: Optional[str] = None
    decision_ownership: Optional[str] = None
    key_concerns: List[str] = []
    wants_consultation: bool = False
    # Chat integration
    use_chat: bool = False
    chat_message: Optional[str] = None


class RecommendationResponse(BaseModel):
    ok: bool
    recommendation_id: str
    situation_summary: str
    chart_insights: List[dict]
    branch: str
    primary_package: dict
    alternative_packages: List[dict]
    suggested_remedies: List[dict]
    reasoning: str
    versions: dict


class CheckoutRequest(BaseModel):
    package_id: str
    remedy_addon_ids: List[str] = []
    recommendation_id: Optional[str] = None


class CheckoutResponse(BaseModel):
    ok: bool
    order_id: str
    razorpay_order_id: str
    amount_inr: int
    breakdown: dict
    checkout_options: dict


class CheckoutVerifyRequest(BaseModel):
    order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class CheckoutVerifyResponse(BaseModel):
    ok: bool
    plan_id: str
    message: str


class TaskCompleteRequest(BaseModel):
    notes: Optional[str] = None


class ConsultBookingResponse(BaseModel):
    ok: bool
    booking_url: str
    sessions_remaining: int
    chat_sla_hours: int


class PlanResponse(BaseModel):
    ok: bool
    plan: dict
    today_tasks: List[dict]
    progress: dict
    consult_status: dict
    remedy_addons: List[dict]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_id_from_token(authorization: str = Header(None)) -> str:
    """
    Extract user_id from JWT token.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("user_id", "unknown")
        except:
            return "unknown"
    
    return "unknown"


def get_user_info_from_token(authorization: str = Header(None)) -> dict:
    """Extract user info from JWT token"""
    if not authorization:
        return {"user_id": "unknown", "email": "", "name": ""}
    
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return {
                "user_id": payload.get("user_id", "unknown"),
                "email": payload.get("email", ""),
                "name": payload.get("name", "")
            }
        except:
            pass
    
    return {"user_id": "unknown", "email": "", "name": ""}


async def get_storage(request: Request):
    """Get storage from app state"""
    storage = get_niro_v2_storage()
    if storage is None:
        # Try to get from request state
        if hasattr(request.app.state, 'niro_v2_storage'):
            return request.app.state.niro_v2_storage
        raise HTTPException(status_code=500, detail="Storage not initialized")
    return storage


# ============================================================================
# CATALOG ENDPOINTS
# ============================================================================

@router.get("/catalog/packages", response_model=PackageListResponse)
async def list_packages(
    topic: Optional[str] = None,
    branch: Optional[str] = None
):
    """List all active packages with optional filtering"""
    catalog = get_catalog_service()
    packages = catalog.get_all_packages(topic=topic, branch=branch)
    
    return PackageListResponse(
        ok=True,
        packages=[p.model_dump() for p in packages],
        catalog_version=CATALOG_VERSION
    )


@router.get("/catalog/packages/{package_id}", response_model=PackageDetailResponse)
async def get_package(package_id: str):
    """Get full package detail with resolved policy and suggested remedies"""
    catalog = get_catalog_service()
    package_data = catalog.get_package_with_policy(package_id)
    
    if not package_data:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # Add consultation booking URL if package includes consultation
    if package_data.get("includes_consultation"):
        package_data["consultation_booking_url"] = CONSULTATION_BOOKING_URL
    
    return PackageDetailResponse(
        ok=True,
        package=package_data,
        catalog_version=CATALOG_VERSION
    )


@router.get("/catalog/remedies", response_model=RemedyListResponse)
async def list_remedies(
    category: Optional[str] = None,
    topic: Optional[str] = None
):
    """List all active remedies with optional filtering"""
    catalog = get_catalog_service()
    remedies = catalog.get_all_remedies(category=category, topic=topic)
    
    return RemedyListResponse(
        ok=True,
        remedies=[r.model_dump() for r in remedies],
        catalog_version=CATALOG_VERSION
    )


@router.get("/catalog/remedies/{remedy_id}", response_model=RemedyDetailResponse)
async def get_remedy(remedy_id: str):
    """Get full remedy detail"""
    catalog = get_catalog_service()
    remedy = catalog.get_remedy(remedy_id)
    
    if not remedy:
        raise HTTPException(status_code=404, detail="Remedy not found")
    
    return RemedyDetailResponse(
        ok=True,
        remedy=remedy.model_dump(),
        catalog_version=CATALOG_VERSION
    )


# ============================================================================
# ONBOARDING ENDPOINTS
# ============================================================================

@router.post("/onboarding/intake", response_model=IntakeResponse)
async def save_intake(
    request_data: IntakeRequest,
    request: Request,
    authorization: str = Header(None)
):
    """Save situation intake from onboarding"""
    user_id = get_user_id_from_token(authorization)
    storage = await get_storage(request)
    
    try:
        intake_data = {
            "intake_id": str(uuid.uuid4()),
            "user_id": user_id,
            "topic": request_data.topic,
            "urgency": request_data.urgency,
            "desired_outcome": request_data.desired_outcome,
            "decision_ownership": request_data.decision_ownership
        }
        
        intake_id = await storage.save_intake(intake_data)
        
        # Track telemetry
        telemetry = get_telemetry_service()
        await telemetry.track_intake_completed(
            user_id=user_id,
            topic=request_data.topic,
            urgency=request_data.urgency,
            decision_ownership=request_data.decision_ownership,
            time_to_complete_seconds=0
        )
        
        return IntakeResponse(
            ok=True,
            intake_id=intake_id,
            session_ready=True
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/onboarding/status")
async def get_onboarding_status(
    request: Request,
    authorization: str = Header(None)
):
    """Check onboarding completion status"""
    user_id = get_user_id_from_token(authorization)
    storage = await get_storage(request)
    
    latest_intake = await storage.get_latest_user_intake(user_id)
    has_intake = latest_intake is not None
    
    return {
        "ok": True,
        "user_id": user_id,
        "birth_details_complete": True,
        "intake_complete": has_intake,
        "can_start_chat": has_intake,
        "latest_intake_id": latest_intake["intake_id"] if latest_intake else None
    }


# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@router.post("/recommendations/generate", response_model=RecommendationResponse)
async def generate_recommendation(
    request_data: RecommendationRequest,
    request: Request,
    authorization: str = Header(None)
):
    """
    Generate personalized recommendation.
    Can use rules-based engine or integrate with existing chat.
    """
    user_id = get_user_id_from_token(authorization)
    catalog = get_catalog_service()
    engine = get_recommendation_engine()
    telemetry = get_telemetry_service()
    storage = await get_storage(request)
    
    # Get or create intake
    intake_data = None
    if request_data.intake_id:
        intake_data = await storage.get_intake(request_data.intake_id)
    
    if not intake_data and request_data.topic:
        intake_data = {
            "intake_id": str(uuid.uuid4()),
            "user_id": user_id,
            "topic": request_data.topic,
            "urgency": request_data.urgency or "medium",
            "desired_outcome": request_data.desired_outcome or "",
            "decision_ownership": request_data.decision_ownership or "me"
        }
        await storage.save_intake(intake_data)
    
    if not intake_data:
        raise HTTPException(status_code=400, detail="Either intake_id or topic required")
    
    # Create intake model
    intake = SituationIntake(
        intake_id=intake_data["intake_id"],
        user_id=user_id,
        topic=Topic(intake_data["topic"]),
        urgency=Urgency(intake_data["urgency"]),
        desired_outcome=intake_data["desired_outcome"],
        decision_ownership=DecisionOwnership(intake_data["decision_ownership"])
    )
    
    # Create extraction from request
    extraction = StepAExtraction(
        situation_summary=f"User seeking guidance on {intake.topic.value} with {intake.urgency.value} urgency. Goal: {intake.desired_outcome}",
        topic_confirmed=intake.topic.value,
        urgency_level=intake.urgency.value,
        sentiment="determined",
        key_concerns=request_data.key_concerns or [],
        wants_consultation=request_data.wants_consultation,
        specific_needs=[]
    )
    
    # Generate recommendation using rules engine
    session_id = str(uuid.uuid4())
    recommendation = engine.generate_rules_based_recommendation(
        session_id=session_id,
        user_id=user_id,
        extraction=extraction,
        intake=intake
    )
    
    # Save recommendation to MongoDB
    recommendation_data = {
        "recommendation_id": recommendation.recommendation_id,
        "session_id": session_id,
        "user_id": user_id,
        "intake_id": intake_data["intake_id"],
        "situation": recommendation.situation.model_dump(),
        "chart_insights": [ci.model_dump() for ci in recommendation.chart_insights],
        "recommendation": recommendation.recommendation.model_dump(),
        "audit": recommendation.audit.model_dump()
    }
    await storage.save_recommendation(recommendation_data)
    
    # Get full package data
    primary_pkg = catalog.get_package_with_policy(recommendation.recommendation.primary_package_id)
    if primary_pkg and primary_pkg.get("includes_consultation"):
        primary_pkg["consultation_booking_url"] = CONSULTATION_BOOKING_URL
    
    alt_pkgs = []
    for pid in recommendation.recommendation.alternative_package_ids:
        pkg = catalog.get_package_with_policy(pid)
        if pkg:
            if pkg.get("includes_consultation"):
                pkg["consultation_booking_url"] = CONSULTATION_BOOKING_URL
            alt_pkgs.append(pkg)
    
    suggested_remedies = [
        catalog.get_remedy(rid).model_dump()
        for rid in recommendation.recommendation.suggested_remedy_ids
        if catalog.get_remedy(rid)
    ]
    
    # Track telemetry
    await telemetry.track_recommendations_validated(
        user_id=user_id,
        session_id=session_id,
        recommendation_id=recommendation.recommendation_id,
        branch=recommendation.recommendation.branch,
        primary_package_id=recommendation.recommendation.primary_package_id,
        alt_packages_count=len(recommendation.recommendation.alternative_package_ids),
        suggested_remedies_count=len(recommendation.recommendation.suggested_remedy_ids),
        retry_count=recommendation.audit.retry_count,
        prompt_version=PROMPT_VERSION,
        catalog_version=CATALOG_VERSION
    )
    
    return RecommendationResponse(
        ok=True,
        recommendation_id=recommendation.recommendation_id,
        situation_summary=recommendation.situation.situation_summary,
        chart_insights=[ci.model_dump() for ci in recommendation.chart_insights],
        branch=recommendation.recommendation.branch,
        primary_package=primary_pkg,
        alternative_packages=alt_pkgs,
        suggested_remedies=suggested_remedies,
        reasoning=recommendation.recommendation.reasoning,
        versions={
            "prompt_version": PROMPT_VERSION,
            "catalog_version": CATALOG_VERSION
        }
    )


@router.get("/recommendations/{recommendation_id}")
async def get_recommendation(
    recommendation_id: str,
    request: Request
):
    """Get a stored recommendation by ID"""
    storage = await get_storage(request)
    catalog = get_catalog_service()
    
    recommendation_data = await storage.get_recommendation(recommendation_id)
    if not recommendation_data:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    rec = recommendation_data.get("recommendation", {})
    primary_pkg = catalog.get_package_with_policy(rec.get("primary_package_id"))
    if primary_pkg and primary_pkg.get("includes_consultation"):
        primary_pkg["consultation_booking_url"] = CONSULTATION_BOOKING_URL
    
    alt_pkgs = []
    for pid in rec.get("alternative_package_ids", []):
        pkg = catalog.get_package_with_policy(pid)
        if pkg:
            if pkg.get("includes_consultation"):
                pkg["consultation_booking_url"] = CONSULTATION_BOOKING_URL
            alt_pkgs.append(pkg)
    
    suggested_remedies = [
        catalog.get_remedy(rid).model_dump()
        for rid in rec.get("suggested_remedy_ids", [])
        if catalog.get_remedy(rid)
    ]
    
    return {
        "ok": True,
        "recommendation_id": recommendation_id,
        "situation_summary": recommendation_data.get("situation", {}).get("situation_summary", ""),
        "chart_insights": recommendation_data.get("chart_insights", []),
        "branch": rec.get("branch"),
        "primary_package": primary_pkg,
        "alternative_packages": alt_pkgs,
        "suggested_remedies": suggested_remedies,
        "reasoning": rec.get("reasoning", "")
    }


# ============================================================================
# CHECKOUT ENDPOINTS
# ============================================================================

@router.post("/checkout/create-order", response_model=CheckoutResponse)
async def create_checkout_order(
    request_data: CheckoutRequest,
    request: Request,
    authorization: str = Header(None)
):
    """Create checkout order for package + optional remedy add-ons"""
    user_info = get_user_info_from_token(authorization)
    user_id = user_info["user_id"]
    catalog = get_catalog_service()
    payment_service = get_payment_service()
    telemetry = get_telemetry_service()
    storage = await get_storage(request)
    
    # Validate package
    package = catalog.get_package(request_data.package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # Validate and calculate remedy add-ons
    remedy_total = 0
    valid_remedy_ids = []
    for remedy_id in request_data.remedy_addon_ids:
        remedy = catalog.get_remedy(remedy_id)
        if remedy:
            remedy_total += remedy.price_inr
            valid_remedy_ids.append(remedy_id)
    
    total_amount = package.price_inr + remedy_total
    
    # Create order ID
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    
    # Create Razorpay order
    razorpay_order = payment_service.create_order(
        amount_inr=total_amount,
        receipt=order_id,
        notes={
            "package_id": request_data.package_id,
            "user_id": user_id,
            "remedy_count": len(valid_remedy_ids)
        }
    )
    
    # Save order to MongoDB
    order_data = {
        "order_id": order_id,
        "user_id": user_id,
        "package_id": request_data.package_id,
        "remedy_addon_ids": valid_remedy_ids,
        "package_amount": package.price_inr,
        "remedy_amount": remedy_total,
        "total_amount": total_amount,
        "recommendation_id": request_data.recommendation_id,
        "razorpay_order_id": razorpay_order["id"],
        "status": "pending"
    }
    await storage.save_order(order_data)
    
    # Get checkout options
    checkout_options = payment_service.get_checkout_options(
        order_id=razorpay_order["id"],
        amount_inr=total_amount,
        user_name=user_info.get("name", ""),
        user_email=user_info.get("email", ""),
        description=f"NIRO - {package.name}"
    )
    
    # Track telemetry
    await telemetry.track_checkout_started(
        user_id=user_id,
        package_id=request_data.package_id,
        package_price_inr=package.price_inr,
        remedy_addon_ids=valid_remedy_ids,
        remedy_addons_total_inr=remedy_total,
        total_amount_inr=total_amount,
        recommendation_id=request_data.recommendation_id
    )
    
    return CheckoutResponse(
        ok=True,
        order_id=order_id,
        razorpay_order_id=razorpay_order["id"],
        amount_inr=total_amount,
        breakdown={
            "package": package.price_inr,
            "remedies": remedy_total,
            "total": total_amount
        },
        checkout_options=checkout_options
    )


@router.post("/checkout/verify", response_model=CheckoutVerifyResponse)
async def verify_checkout(
    request_data: CheckoutVerifyRequest,
    request: Request,
    authorization: str = Header(None)
):
    """Verify payment and create plan"""
    user_id = get_user_id_from_token(authorization)
    catalog = get_catalog_service()
    payment_service = get_payment_service()
    telemetry = get_telemetry_service()
    storage = await get_storage(request)
    
    # Get order
    order = await storage.get_order(request_data.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify Razorpay signature
    is_valid = payment_service.verify_payment_signature(
        razorpay_order_id=order["razorpay_order_id"],
        razorpay_payment_id=request_data.razorpay_payment_id,
        razorpay_signature=request_data.razorpay_signature
    )
    
    if not is_valid:
        await telemetry.track_purchase_failed(
            user_id=user_id,
            order_id=request_data.order_id,
            total_amount_inr=order["total_amount"],
            failure_reason="invalid_signature",
            payment_method="razorpay"
        )
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    # Get package details
    package = catalog.get_package(order["package_id"])
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # Create plan
    plan_id = f"plan_{uuid.uuid4().hex[:12]}"
    start_date = date.today()
    end_date = start_date + timedelta(weeks=package.duration_weeks)
    
    # Calculate total tasks
    total_tasks = 0
    for item in package.self_guided_items:
        if item.schedule.is_repeating:
            days = item.schedule.day_end - item.schedule.day_start + 1
            if item.schedule.repeat_frequency == "daily":
                total_tasks += days
            elif item.schedule.repeat_frequency == "weekly":
                total_tasks += days // 7 + 1
            elif item.schedule.repeat_frequency == "twice_weekly":
                total_tasks += (days // 7 + 1) * 2
        else:
            total_tasks += 1
    
    # Get consult policy
    consult_sessions_limit = 0
    if package.includes_consultation and package.consult_policy_id:
        policy = catalog.get_consult_policy(package.consult_policy_id)
        if policy:
            consult_sessions_limit = policy.live_sessions.total_sessions_included
    
    plan_data = {
        "plan_id": plan_id,
        "user_id": user_id,
        "package_id": order["package_id"],
        "recommendation_id": order.get("recommendation_id"),
        "status": "active",
        "start_date": start_date,
        "end_date": end_date,
        "payment_id": request_data.razorpay_payment_id,
        "package_amount": order["package_amount"],
        "remedy_addons_amount": order["remedy_amount"],
        "total_amount": order["total_amount"],
        "current_week": 1,
        "tasks_completed": 0,
        "tasks_total": total_tasks,
        "consult_sessions_used": 0,
        "consult_sessions_limit": consult_sessions_limit,
        "consultation_booking_url": CONSULTATION_BOOKING_URL if package.includes_consultation else None
    }
    await storage.save_plan(plan_data)
    
    # Create tasks for the plan
    tasks = []
    task_sequence = 0
    for item in package.self_guided_items:
        if item.schedule.is_repeating:
            current_day = item.schedule.day_start
            while current_day <= item.schedule.day_end:
                task = {
                    "plan_id": plan_id,
                    "item_id": item.item_id,
                    "scheduled_date": start_date + timedelta(days=current_day - 1),
                    "day_number": current_day,
                    "sequence_order": task_sequence,
                    "name": item.name,
                    "type": item.type,
                    "description": item.description,
                    "duration_minutes": item.duration_minutes,
                    "content_type": item.content_type,
                    "status": "pending"
                }
                tasks.append(task)
                task_sequence += 1
                
                if item.schedule.repeat_frequency == "daily":
                    current_day += 1
                elif item.schedule.repeat_frequency == "weekly":
                    current_day += 7
                elif item.schedule.repeat_frequency == "twice_weekly":
                    current_day += 3
                else:
                    current_day += 1
        else:
            task = {
                "plan_id": plan_id,
                "item_id": item.item_id,
                "scheduled_date": start_date + timedelta(days=item.schedule.day_start - 1),
                "day_number": item.schedule.day_start,
                "sequence_order": task_sequence,
                "name": item.name,
                "type": item.type,
                "description": item.description,
                "duration_minutes": item.duration_minutes,
                "content_type": item.content_type,
                "status": "pending"
            }
            tasks.append(task)
            task_sequence += 1
    
    await storage.save_tasks_bulk(tasks)
    
    # Create remedy add-ons
    for remedy_id in order.get("remedy_addon_ids", []):
        remedy = catalog.get_remedy(remedy_id)
        if remedy:
            addon_data = {
                "plan_id": plan_id,
                "user_id": user_id,
                "remedy_id": remedy_id,
                "amount_paid": remedy.price_inr,
                "payment_id": request_data.razorpay_payment_id,
                "status": "pending"
            }
            await storage.save_remedy_addon(addon_data)
    
    # Update order status
    await storage.update_order_status(
        request_data.order_id, 
        "completed",
        payment_id=request_data.razorpay_payment_id,
        plan_id=plan_id
    )
    
    # Track telemetry
    await telemetry.track_purchase_completed(
        user_id=user_id,
        order_id=request_data.order_id,
        plan_id=plan_id,
        package_id=order["package_id"],
        package_topic=package.topic.value,
        package_branch=package.branch.value,
        package_price_inr=order["package_amount"],
        remedy_addon_ids=order.get("remedy_addon_ids", []),
        remedy_addons_count=len(order.get("remedy_addon_ids", [])),
        remedy_addons_total_inr=order["remedy_amount"],
        total_amount_inr=order["total_amount"],
        payment_method="razorpay"
    )
    
    await telemetry.track_plan_started(
        user_id=user_id,
        plan_id=plan_id,
        package_id=order["package_id"],
        package_topic=package.topic.value,
        package_duration_weeks=package.duration_weeks
    )
    
    return CheckoutVerifyResponse(
        ok=True,
        plan_id=plan_id,
        message="Payment verified and plan created successfully"
    )


# ============================================================================
# PLAN ENDPOINTS
# ============================================================================

@router.get("/plans")
async def list_plans(
    request: Request,
    status: Optional[str] = None,
    authorization: str = Header(None)
):
    """List user's plans"""
    user_id = get_user_id_from_token(authorization)
    storage = await get_storage(request)
    catalog = get_catalog_service()
    
    plans = await storage.get_user_plans(user_id, status=status)
    
    # Enrich with package info
    enriched_plans = []
    for plan in plans:
        package = catalog.get_package(plan.get("package_id"))
        if package:
            plan["package_name"] = package.name
            plan["package_topic"] = package.topic.value
        enriched_plans.append(plan)
    
    return {
        "ok": True,
        "plans": enriched_plans
    }


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str, 
    request: Request,
    authorization: str = Header(None)
):
    """Get full plan dashboard data"""
    user_id = get_user_id_from_token(authorization)
    catalog = get_catalog_service()
    storage = await get_storage(request)
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get package details
    package = catalog.get_package_with_policy(plan["package_id"])
    
    # Get today's tasks
    today = date.today()
    today_tasks = await storage.get_plan_tasks_for_date(plan_id, today)
    
    # Get all tasks for progress calculation
    all_tasks = await storage.get_plan_tasks(plan_id)
    completed_tasks = [t for t in all_tasks if t.get("status") == "completed"]
    progress_percent = int((len(completed_tasks) / len(all_tasks) * 100)) if all_tasks else 0
    
    # Calculate current week
    start_date = date.fromisoformat(plan["start_date"]) if isinstance(plan["start_date"], str) else plan["start_date"]
    days_elapsed = (today - start_date).days
    current_week = max(1, (days_elapsed // 7) + 1)
    
    # Get consult status
    consult_status = {
        "sessions_used": plan.get("consult_sessions_used", 0),
        "sessions_remaining": plan.get("consult_sessions_limit", 0) - plan.get("consult_sessions_used", 0),
        "sessions_total": plan.get("consult_sessions_limit", 0),
        "chat_available": True,
        "booking_url": CONSULTATION_BOOKING_URL
    }
    
    if package and package.get("consult_policy"):
        consult_status["chat_sla_hours"] = package["consult_policy"]["chat"]["sla_hours"]
    
    # Get remedy add-ons
    plan_addons = await storage.get_plan_remedy_addons(plan_id)
    addon_details = []
    for addon in plan_addons:
        remedy = catalog.get_remedy(addon.get("remedy_id"))
        if remedy:
            addon_details.append({
                **addon,
                "remedy": remedy.model_dump()
            })
    
    return PlanResponse(
        ok=True,
        plan={
            **plan,
            "package": package,
            "current_week": current_week
        },
        today_tasks=today_tasks,
        progress={
            "percent": progress_percent,
            "tasks_completed": len(completed_tasks),
            "tasks_total": len(all_tasks),
            "current_week": current_week,
            "total_weeks": package["duration_weeks"] if package else 0
        },
        consult_status=consult_status,
        remedy_addons=addon_details
    )


@router.get("/plans/{plan_id}/tasks/today")
async def get_today_tasks(
    plan_id: str, 
    request: Request,
    authorization: str = Header(None)
):
    """Get today's tasks for a plan"""
    user_id = get_user_id_from_token(authorization)
    storage = await get_storage(request)
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    today = date.today()
    tasks = await storage.get_plan_tasks_for_date(plan_id, today)
    
    return {
        "ok": True,
        "date": today.isoformat(),
        "tasks": tasks,
        "completed_count": len([t for t in tasks if t.get("status") == "completed"]),
        "total_count": len(tasks)
    }


@router.post("/plans/{plan_id}/tasks/{task_id}/complete")
async def complete_task(
    plan_id: str,
    task_id: str,
    request_data: TaskCompleteRequest,
    request: Request,
    authorization: str = Header(None)
):
    """Mark a task as completed"""
    user_id = get_user_id_from_token(authorization)
    telemetry = get_telemetry_service()
    storage = await get_storage(request)
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    task = await storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["plan_id"] != plan_id:
        raise HTTPException(status_code=400, detail="Task does not belong to this plan")
    
    # Update task
    await storage.complete_task(task_id, notes=request_data.notes)
    
    # Update plan progress
    await storage.increment_plan_tasks_completed(plan_id)
    
    # Track telemetry
    await telemetry.track_task_completed(
        user_id=user_id,
        plan_id=plan_id,
        task_id=task_id,
        task_type=task.get("type", ""),
        task_day=task.get("day_number", 0)
    )
    
    # Get updated task
    updated_task = await storage.get_task(task_id)
    updated_plan = await storage.get_plan(plan_id)
    
    return {
        "ok": True,
        "task": updated_task,
        "plan_progress": {
            "tasks_completed": updated_plan.get("tasks_completed", 0),
            "tasks_total": updated_plan.get("tasks_total", 0)
        }
    }


@router.post("/plans/{plan_id}/tasks/{task_id}/skip")
async def skip_task(
    plan_id: str,
    task_id: str,
    request: Request,
    authorization: str = Header(None)
):
    """Skip a task"""
    user_id = get_user_id_from_token(authorization)
    storage = await get_storage(request)
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    task = await storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["plan_id"] != plan_id:
        raise HTTPException(status_code=400, detail="Task does not belong to this plan")
    
    await storage.skip_task(task_id)
    updated_task = await storage.get_task(task_id)
    
    return {
        "ok": True,
        "task": updated_task
    }


# ============================================================================
# CONSULTATION ENDPOINTS
# ============================================================================

@router.get("/plans/{plan_id}/consult", response_model=ConsultBookingResponse)
async def get_consult_info(
    plan_id: str,
    request: Request,
    authorization: str = Header(None)
):
    """Get consultation booking information"""
    user_id = get_user_id_from_token(authorization)
    catalog = get_catalog_service()
    storage = await get_storage(request)
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    package = catalog.get_package_with_policy(plan["package_id"])
    
    chat_sla_hours = 12
    if package and package.get("consult_policy"):
        chat_sla_hours = package["consult_policy"]["chat"]["sla_hours"]
    
    return ConsultBookingResponse(
        ok=True,
        booking_url=CONSULTATION_BOOKING_URL,
        sessions_remaining=plan.get("consult_sessions_limit", 0) - plan.get("consult_sessions_used", 0),
        chat_sla_hours=chat_sla_hours
    )


@router.post("/plans/{plan_id}/consult/book")
async def book_consultation(
    plan_id: str,
    request: Request,
    authorization: str = Header(None)
):
    """Redirect to consultation booking"""
    user_id = get_user_id_from_token(authorization)
    storage = await get_storage(request)
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    sessions_remaining = plan.get("consult_sessions_limit", 0) - plan.get("consult_sessions_used", 0)
    
    if sessions_remaining <= 0:
        raise HTTPException(status_code=400, detail="No consultation sessions remaining")
    
    return {
        "ok": True,
        "booking_url": CONSULTATION_BOOKING_URL,
        "sessions_remaining": sessions_remaining,
        "message": "Please use the booking URL to schedule your consultation"
    }


# ============================================================================
# REMEDY ADD-ON ENDPOINTS
# ============================================================================

@router.post("/checkout/addon")
async def purchase_remedy_addon(
    plan_id: str,
    remedy_id: str,
    request: Request,
    authorization: str = Header(None)
):
    """Purchase a remedy add-on for an existing plan"""
    user_info = get_user_info_from_token(authorization)
    user_id = user_info["user_id"]
    catalog = get_catalog_service()
    payment_service = get_payment_service()
    storage = await get_storage(request)
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    remedy = catalog.get_remedy(remedy_id)
    if not remedy:
        raise HTTPException(status_code=404, detail="Remedy not found")
    
    # Create order
    order_id = f"addon_order_{uuid.uuid4().hex[:12]}"
    
    razorpay_order = payment_service.create_order(
        amount_inr=remedy.price_inr,
        receipt=order_id,
        notes={
            "type": "addon",
            "plan_id": plan_id,
            "remedy_id": remedy_id,
            "user_id": user_id
        }
    )
    
    order_data = {
        "order_id": order_id,
        "user_id": user_id,
        "plan_id": plan_id,
        "remedy_id": remedy_id,
        "total_amount": remedy.price_inr,
        "razorpay_order_id": razorpay_order["id"],
        "type": "addon",
        "status": "pending"
    }
    await storage.save_order(order_data)
    
    checkout_options = payment_service.get_checkout_options(
        order_id=razorpay_order["id"],
        amount_inr=remedy.price_inr,
        user_name=user_info.get("name", ""),
        user_email=user_info.get("email", ""),
        description=f"NIRO - {remedy.name}"
    )
    
    return {
        "ok": True,
        "order_id": order_id,
        "razorpay_order_id": razorpay_order["id"],
        "amount_inr": remedy.price_inr,
        "remedy": remedy.model_dump(),
        "checkout_options": checkout_options
    }


@router.get("/plans/{plan_id}/remedies")
async def get_plan_remedies(
    plan_id: str, 
    request: Request,
    authorization: str = Header(None)
):
    """Get all remedy add-ons for a plan"""
    user_id = get_user_id_from_token(authorization)
    catalog = get_catalog_service()
    storage = await get_storage(request)
    
    plan = await storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    plan_addons = await storage.get_plan_remedy_addons(plan_id)
    addon_details = []
    
    for addon in plan_addons:
        remedy = catalog.get_remedy(addon.get("remedy_id"))
        if remedy:
            addon_details.append({
                **addon,
                "remedy": remedy.model_dump()
            })
    
    return {
        "ok": True,
        "addons": addon_details
    }


# ============================================================================
# PROFILE & JOURNEY ENDPOINTS
# ============================================================================

@router.get("/profile/journey")
async def get_user_journey(
    request: Request,
    authorization: str = Header(None)
):
    """Get user's journey/case file"""
    user_id = get_user_id_from_token(authorization)
    storage = await get_storage(request)
    catalog = get_catalog_service()
    
    plans = await storage.get_user_plans(user_id)
    recommendations = await storage.get_user_recommendations(user_id)
    remedy_addons = await storage.get_user_remedy_addons(user_id)
    
    # Categorize plans
    active_plans = [p for p in plans if p.get("status") == "active"]
    completed_plans = [p for p in plans if p.get("status") == "completed"]
    
    # Get stats
    stats = await storage.get_user_stats(user_id)
    
    return {
        "ok": True,
        "active_plans": active_plans,
        "completed_plans": completed_plans,
        "saved_recommendations": recommendations,
        "remedy_history": remedy_addons,
        "stats": stats
    }


@router.post("/profile/save-recommendation")
async def save_recommendation_for_later(
    recommendation_id: str,
    request: Request,
    authorization: str = Header(None)
):
    """Save a recommendation for later"""
    user_id = get_user_id_from_token(authorization)
    storage = await get_storage(request)
    
    recommendation = await storage.get_recommendation(recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Mark as saved
    await storage.save_recommendation({
        **recommendation,
        "saved": True,
        "saved_at": datetime.utcnow().isoformat()
    })
    
    return {
        "ok": True,
        "saved_id": recommendation_id,
        "message": "Recommendation saved"
    }


# ============================================================================
# TELEMETRY ENDPOINT
# ============================================================================

class TelemetryEventRequest(BaseModel):
    event_name: str
    properties: dict = {}


@router.post("/telemetry/event")
async def log_telemetry_event(
    request_data: TelemetryEventRequest,
    authorization: str = Header(None)
):
    """Log a telemetry event from frontend"""
    user_id = get_user_id_from_token(authorization)
    telemetry = get_telemetry_service()
    
    await telemetry.log_event(
        event_name=request_data.event_name,
        user_id=user_id,
        properties=request_data.properties
    )
    
    return {"ok": True, "logged": True}
