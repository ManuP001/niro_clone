"""Authentication API endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from .models import (
    OTPRequest,
    OTPVerify,
    AuthToken,
    UserResponse,
    ProfileResponse,
    ProfileUpdateResponse,
    UserProfileRequest
)
from .auth_service import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/identify", response_model=AuthToken)
async def identify(req: OTPRequest):
    """
    Identify user by phone or email.
    Creates user if doesn't exist, returns JWT token.
    
    Request:
    { "identifier": "<phone_or_email>" }
    
    Response:
    { "ok": true, "token": "<jwt>", "user_id": "<uuid>" }
    """
    try:
        auth_service = get_auth_service()
        
        # Get or create user
        user = auth_service.user_store.get_user_by_identifier(req.identifier)
        if not user:
            user_id = str(__import__('uuid').uuid4())
            auth_service.user_store.create_user(user_id, req.identifier)
            user = {'id': user_id, 'identifier': req.identifier}
        
        user_id = user['id']
        
        # Generate JWT token
        profile = auth_service.profile_store.get_profile(user_id)
        payload = {
            'user_id': user_id,
            'identifier': req.identifier,
            'profile_complete': profile is not None
        }
        token = auth_service.jwt_handler.encode(payload)
        
        logger.info(f"User identified: {req.identifier}, user_id={user_id}")
        
        return {
            "ok": True,
            "token": token,
            "user_id": user_id,
            "user": {
                "id": user_id,
                "identifier": req.identifier,
                "profile_complete": profile is not None
            }
        }
    except Exception as e:
        logger.error(f"Error in identify: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/request-otp")
async def request_otp(req: OTPRequest):
    """
    Request OTP for email or phone.
    
    Response:
    { "ok": true, "expires_in": 300 }
    """
    try:
        auth_service = get_auth_service()
        success, expires_in = auth_service.request_otp(req.identifier)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to generate OTP")
        
        return {
            "ok": True,
            "expires_in": expires_in
        }
    except Exception as e:
        logger.error(f"Error in request_otp: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-otp", response_model=AuthToken)
async def verify_otp(req: OTPVerify):
    """
    Verify OTP and get JWT token.
    
    Response:
    { "ok": true, "token": "<jwt>", "user_id": "<id>" }
    """
    try:
        auth_service = get_auth_service()
        result = auth_service.verify_otp(req.identifier, req.otp)
        
        if not result:
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        token, user_id = result
        return {
            "ok": True,
            "token": token,
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_otp: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Get current user info from token.
    
    Headers:
    Authorization: Bearer <token>
    
    Response:
    { "ok": true, "user": { "id": "...", "identifier": "...", "profile_complete": true/false } }
    """
    try:
        auth_service = get_auth_service()
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        # Extract token from Bearer header
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = parts[1]
        
        # Verify token
        payload = auth_service.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = payload.get('user_id')
        user_info = auth_service.get_user_info(user_id)
        
        if not user_info:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "ok": True,
            "user": user_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
