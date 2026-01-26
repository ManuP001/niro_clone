"""
Google OAuth Authentication Routes - Emergent Auth Integration
REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
"""
import os
import uuid
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

# Get database from app state
async def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Emergent Auth endpoint
EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"

# Session configuration
SESSION_EXPIRY_DAYS = 7


class SessionRequest(BaseModel):
    session_id: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    google_id: Optional[str] = None
    dob: Optional[str] = None
    tob: Optional[str] = None
    pob: Optional[str] = None
    created_at: Optional[str] = None


async def get_user_from_session(request: Request, db: AsyncIOMotorDatabase) -> Optional[dict]:
    """Extract user from session token (cookie or header)"""
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
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        return None
    
    # Check expiry with timezone awareness
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        return None
    
    # Get user
    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    return user_doc


@router.post("/session")
async def exchange_session(
    request: Request,
    response: Response,
    session_data: SessionRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Exchange Emergent session_id for our session_token"""
    try:
        # Call Emergent Auth to get user data
        async with httpx.AsyncClient() as client:
            auth_response = await client.get(
                EMERGENT_AUTH_URL,
                headers={"X-Session-ID": session_data.session_id}
            )
        
        if auth_response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail="Invalid session ID"
            )
        
        auth_data = auth_response.json()
        google_id = auth_data.get("id")
        email = auth_data.get("email")
        name = auth_data.get("name", "")
        picture = auth_data.get("picture", "")
        emergent_session_token = auth_data.get("session_token")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user exists by email (to link existing accounts)
        existing_user = await db.users.find_one({"email": email}, {"_id": 0})
        
        if existing_user:
            # Update existing user with Google data
            user_id = existing_user["user_id"]
            await db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "google_id": google_id,
                        "name": name or existing_user.get("name", ""),
                        "picture": picture,
                        "last_login": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
        else:
            # Create new user
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user_doc = {
                "user_id": user_id,
                "google_id": google_id,
                "email": email,
                "name": name,
                "picture": picture,
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
                "profile_complete": False
            }
            await db.users.insert_one(user_doc)
        
        # Create session
        session_token = f"niro_session_{uuid.uuid4().hex}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)
        
        session_doc = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        }
        
        # Remove old sessions for this user
        await db.user_sessions.delete_many({"user_id": user_id})
        await db.user_sessions.insert_one(session_doc)
        
        # Get updated user data
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        
        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=SESSION_EXPIRY_DAYS * 24 * 60 * 60
        )
        
        return {
            "ok": True,
            "user": {
                "user_id": user_id,
                "email": email,
                "name": user.get("name", name),
                "picture": user.get("picture", picture),
                "dob": user.get("dob"),
                "tob": user.get("tob"),
                "pob": user.get("pob"),
                "profile_complete": user.get("profile_complete", False)
            },
            "token": session_token  # Also return token for localStorage backup
        }
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Auth service error: {str(e)}")


@router.get("/me")
async def get_current_user(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current authenticated user"""
    user = await get_user_from_session(request, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "ok": True,
        "user": {
            "user_id": user.get("user_id"),
            "email": user.get("email"),
            "name": user.get("name"),
            "picture": user.get("picture"),
            "dob": user.get("dob"),
            "tob": user.get("tob"),
            "pob": user.get("pob"),
            "profile_complete": user.get("profile_complete", False)
        }
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Logout and clear session"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    # Clear cookie
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=True,
        samesite="none"
    )
    
    return {"ok": True, "message": "Logged out successfully"}


# Helper function for other routes to get current user
async def get_current_user_dependency(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Dependency for protected routes"""
    user = await get_user_from_session(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
