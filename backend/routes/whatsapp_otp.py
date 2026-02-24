"""
WhatsApp OTP routes — send and verify phone number via WhatsApp.
"""
import random
import string
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends, Header
from pydantic import BaseModel

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


# ── Auth (same pattern as bookings.py) ─────────────────────────────────────

async def get_current_user(request: Request, authorization: Optional[str] = Header(None)):
    """Verify session token (cookie or Authorization header)."""
    try:
        token = request.cookies.get("session_token")
        if not token:
            if not authorization:
                raise HTTPException(status_code=401, detail="Not authenticated")
            token = authorization[7:] if authorization.startswith("Bearer ") else authorization

        if token.startswith("niro_session_dev_"):
            from backend.routes.google_oauth_direct import _dev_sessions
            session = _dev_sessions.get(token)
            if not session:
                raise HTTPException(status_code=401, detail="Dev session expired or invalid")
            return {"user_id": session["user_id"], "email": session["email"], "name": session["name"]}

        if token.startswith("niro_session_"):
            db = request.app.state.db
            session = await db.user_sessions.find_one({"session_token": token})
            if not session:
                raise HTTPException(status_code=401, detail="Session expired or invalid")
            expires_at = session.get("expires_at")
            if expires_at:
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if expires_at < datetime.now(timezone.utc):
                    raise HTTPException(status_code=401, detail="Session expired")
            user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return {"user_id": user.get("user_id"), "email": user.get("email", ""), "name": user.get("name", "")}

        import jwt, os
        secret = os.environ.get("JWT_SECRET", "dev-secret-key-change-in-prod")
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            pass

        import base64, json
        parts = token.split('.')
        if len(parts) >= 2:
            padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded))
            return {
                "user_id": payload.get("sub") or payload.get("user_id", ""),
                "email": payload.get("email", ""),
                "name": payload.get("name", ""),
            }

        raise HTTPException(status_code=401, detail="Invalid token format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


# ── Models ──────────────────────────────────────────────────────────────────

class SendOTPRequest(BaseModel):
    phone: str  # E.164 format, e.g. "+919876543210"


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


# ── Helpers ─────────────────────────────────────────────────────────────────

def _generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/send-otp")
async def send_otp(
    request: Request,
    body: SendOTPRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a 6-digit OTP and send it via WhatsApp to the given phone number.
    Stores the OTP in the otp_codes collection with a 5-minute expiry.
    """
    db = request.app.state.db
    phone = body.phone.strip()

    if not phone.startswith('+'):
        raise HTTPException(status_code=400, detail="Phone must be in E.164 format, e.g. +919876543210")

    otp = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # Upsert the OTP record
    await db.otp_codes.update_one(
        {"phone": phone},
        {
            "$set": {
                "phone": phone,
                "otp": otp,
                "expires_at": expires_at,
                "verified": False,
                "user_id": current_user.get("user_id"),
            }
        },
        upsert=True,
    )

    # Send via WhatsApp (or log in dev mode)
    from backend.services.whatsapp_service import send_whatsapp_otp
    result = await send_whatsapp_otp(phone, otp)

    return {"ok": True, "status": result.get("status"), "message": "OTP sent"}


@router.post("/verify-otp")
async def verify_otp(
    request: Request,
    body: VerifyOTPRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Verify the OTP entered by the user.
    On success, saves the phone number to the user's profile.
    """
    db = request.app.state.db
    phone = body.phone.strip()
    otp = body.otp.strip()

    # Find matching, unexpired, unverified OTP
    record = await db.otp_codes.find_one({
        "phone": phone,
        "otp": otp,
        "verified": False,
        "expires_at": {"$gt": datetime.now(timezone.utc)},
    })

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Mark as verified
    await db.otp_codes.update_one(
        {"_id": record["_id"]},
        {"$set": {"verified": True}},
    )

    # Save phone to user profile
    user_id = current_user.get("user_id")
    if user_id:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"phone": phone}},
        )

    return {"ok": True, "verified": True, "phone": phone}
