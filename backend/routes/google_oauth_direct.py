"""
Direct Google OAuth Authentication Routes
Bypasses Emergent Auth for direct Google sign-in
"""
import os
import uuid
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.parse import urlencode
from fastapi import APIRouter, Request, Response, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Session configuration
SESSION_EXPIRY_DAYS = 7

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Get database from app state
async def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class TokenExchangeRequest(BaseModel):
    code: str
    redirect_uri: str


@router.get("/google/login")
async def google_login(
    request: Request,
    redirect_uri: str = Query(..., description="Frontend callback URL")
):
    """
    Initiate Google OAuth flow - redirects to Google's login page
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    # Store the redirect_uri in a state parameter for security
    state = uuid.uuid4().hex
    
    # Build Google OAuth URL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
        "prompt": "select_account"  # Always show account selector
    }
    
    google_auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    return RedirectResponse(url=google_auth_url)


@router.post("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    data: TokenExchangeRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Exchange Google auth code for tokens and create session
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": data.code,
                    "grant_type": "authorization_code",
                    "redirect_uri": data.redirect_uri
                }
            )
        
        if token_response.status_code != 200:
            error_detail = token_response.json().get('error_description', 'Token exchange failed')
            raise HTTPException(status_code=401, detail=error_detail)
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="No access token received")
        
        # Get user info from Google
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Failed to get user info")
        
        google_user = userinfo_response.json()
        google_id = google_user.get("id")
        email = google_user.get("email")
        name = google_user.get("name", "")
        picture = google_user.get("picture", "")
        
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
            "token": session_token
        }
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Google API error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


class DevLoginRequest(BaseModel):
    email: str = "dev@niro.local"
    name: str = "Dev User"


# In-memory session store for dev login (survives as long as the process runs)
_dev_sessions: dict = {}  # token -> {user_id, email, name, expires_at}
DEV_USER_ID = "user_dev_local_000"


@router.post("/dev-login")
async def dev_login(
    request: Request,
    response: Response,
    data: DevLoginRequest,
):
    """
    Dev-only login — bypasses Google OAuth AND MongoDB.
    Works entirely in-memory so it functions even when the DB is unreachable.
    Disabled in production (when GOOGLE_CLIENT_ID is set).
    """
    if GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=403, detail="Dev login disabled in production")

    session_token = f"niro_session_dev_{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)

    _dev_sessions[session_token] = {
        "user_id": DEV_USER_ID,
        "email": data.email,
        "name": data.name,
        "expires_at": expires_at,
    }

    return {
        "ok": True,
        "user": {
            "user_id": DEV_USER_ID,
            "email": data.email,
            "name": data.name,
            "picture": "",
            "dob": None,
            "tob": None,
            "pob": None,
            "profile_complete": False,
        },
        "token": session_token,
    }


@router.get("/dev-session/{token}")
async def get_dev_session(token: str):
    """Internal helper — lets other auth code validate a dev session token."""
    session = _dev_sessions.get(token)
    if not session:
        return None
    if session["expires_at"] < datetime.now(timezone.utc):
        del _dev_sessions[token]
        return None
    return session


@router.get("/me")
async def get_current_user(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current authenticated user"""
    # Try cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
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
    
    # Also check header
    if not session_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
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
