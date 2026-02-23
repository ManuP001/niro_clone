"""
Booking routes for scheduling calls
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import os

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


# Get database connection
async def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Get database from app state"""
    return request.app.state.db


# Authentication dependency - needs Request for session token lookup
async def get_current_user(request: Request, authorization: Optional[str] = Header(None)):
    """Verify token and return user info - tries cookie first, then Authorization header"""
    try:
        # Try session cookie first (same-origin requests always send cookies; most reliable)
        token = request.cookies.get("session_token")

        # Fall back to Authorization header
        if not token:
            if not authorization:
                raise HTTPException(status_code=401, detail="Not authenticated")
            if authorization.startswith("Bearer "):
                token = authorization[7:]
            else:
                token = authorization
        
        # Check if it's a Niro session token (niro_session_*)
        if token.startswith("niro_session_"):
            db = request.app.state.db
            session = await db.user_sessions.find_one({"session_token": token})
            if not session:
                raise HTTPException(status_code=401, detail="Session expired or invalid")
            
            # Check expiry (handle timezone-naive datetimes returned by Motor)
            expires_at = session.get("expires_at")
            if expires_at:
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if expires_at < datetime.now(timezone.utc):
                    raise HTTPException(status_code=401, detail="Session expired")
            
            # Get user data
            user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            return {
                "user_id": user.get("user_id"),
                "email": user.get("email", ""),
                "name": user.get("name", ""),
            }
        
        # Try JWT verification
        import jwt
        import base64
        import json
        
        secret = os.environ.get("JWT_SECRET", "dev-secret-key-change-in-prod")
        
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            pass  # Try Google token format
        
        # Try Google OAuth token format (decode without verification)
        try:
            parts = token.split('.')
            if len(parts) >= 2:
                padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
                payload = json.loads(base64.urlsafe_b64decode(padded))
                return {
                    "user_id": payload.get("sub") or payload.get("user_id", ""),
                    "email": payload.get("email", ""),
                    "name": payload.get("name", ""),
                }
        except Exception:
            pass
        
        raise HTTPException(status_code=401, detail="Invalid token format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


class BookingCreate(BaseModel):
    scheduled_date: str  # ISO format datetime
    duration_minutes: int = 10
    call_type: str = "free_consultation"
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    notes: Optional[str] = None
    expert_id: Optional[str] = None
    topic_id: Optional[str] = None


class BookingResponse(BaseModel):
    ok: bool
    booking_id: Optional[str] = None
    message: Optional[str] = None


@router.post("/schedule", response_model=BookingResponse)
async def schedule_call(
    request: Request,
    booking: BookingCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule a new call booking.
    Requires authentication.
    """
    db = await get_db(request)
    
    try:
        # Parse the scheduled date
        scheduled_datetime = datetime.fromisoformat(booking.scheduled_date.replace('Z', '+00:00'))
        
        # Validate the date is in the future
        if scheduled_datetime < datetime.now(timezone.utc):
            return BookingResponse(ok=False, message="Cannot schedule calls in the past")
        
        # Generate booking ID
        booking_id = f"booking_{uuid.uuid4().hex[:12]}"
        
        # Create booking document
        booking_doc = {
            "booking_id": booking_id,
            "user_id": current_user.get("user_id") or current_user.get("sub"),
            "user_name": booking.user_name or current_user.get("name", "User"),
            "user_email": booking.user_email or current_user.get("email", ""),
            "scheduled_date": scheduled_datetime,
            "duration_minutes": booking.duration_minutes,
            "call_type": booking.call_type,
            "notes": booking.notes,
            "expert_id": booking.expert_id,
            "topic_id": booking.topic_id,
            "status": "scheduled",  # scheduled, completed, cancelled, no_show
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        # Insert into database
        await db.bookings.insert_one(booking_doc)
        
        return BookingResponse(
            ok=True,
            booking_id=booking_id,
            message="Call scheduled successfully"
        )
        
    except Exception as e:
        print(f"Error scheduling call: {e}")
        return BookingResponse(ok=False, message=str(e))


@router.get("/my-bookings")
async def get_my_bookings(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all bookings for the current user.
    """
    db = await get_db(request)
    
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    # Get user's bookings, sorted by scheduled date
    bookings = await db.bookings.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("scheduled_date", -1).to_list(50)
    
    # Convert datetime objects to ISO strings
    for booking in bookings:
        if isinstance(booking.get("scheduled_date"), datetime):
            booking["scheduled_date"] = booking["scheduled_date"].isoformat()
        if isinstance(booking.get("created_at"), datetime):
            booking["created_at"] = booking["created_at"].isoformat()
        if isinstance(booking.get("updated_at"), datetime):
            booking["updated_at"] = booking["updated_at"].isoformat()
    
    return {
        "ok": True,
        "bookings": bookings,
        "total": len(bookings)
    }


@router.get("/upcoming")
async def get_upcoming_bookings(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get upcoming bookings for the current user (scheduled calls in the future).
    """
    db = await get_db(request)
    
    user_id = current_user.get("user_id") or current_user.get("sub")
    now = datetime.now(timezone.utc)
    
    # Get upcoming bookings
    bookings = await db.bookings.find(
        {
            "user_id": user_id,
            "scheduled_date": {"$gte": now},
            "status": "scheduled"
        },
        {"_id": 0}
    ).sort("scheduled_date", 1).to_list(10)
    
    # Convert datetime objects to ISO strings
    for booking in bookings:
        if isinstance(booking.get("scheduled_date"), datetime):
            booking["scheduled_date"] = booking["scheduled_date"].isoformat()
        if isinstance(booking.get("created_at"), datetime):
            booking["created_at"] = booking["created_at"].isoformat()
        if isinstance(booking.get("updated_at"), datetime):
            booking["updated_at"] = booking["updated_at"].isoformat()
    
    return {
        "ok": True,
        "bookings": bookings,
        "total": len(bookings)
    }


@router.put("/{booking_id}/cancel")
async def cancel_booking(
    request: Request,
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a scheduled booking.
    """
    db = await get_db(request)
    
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    # Find and update the booking
    result = await db.bookings.update_one(
        {
            "booking_id": booking_id,
            "user_id": user_id,
            "status": "scheduled"
        },
        {
            "$set": {
                "status": "cancelled",
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.modified_count == 0:
        return {"ok": False, "message": "Booking not found or already cancelled"}
    
    return {"ok": True, "message": "Booking cancelled successfully"}
