"""User profile API endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional
from datetime import datetime, timezone

from backend.auth.auth_service import get_auth_service
from backend.auth.models import (
    ProfileResponse,
    ProfileUpdateResponse,
    UserProfileRequest,
    UserProfile
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Reference to MongoDB - will be set by server.py
_db = None

def set_db(db):
    """Set the MongoDB database reference"""
    global _db
    _db = db


async def _extract_user_id_with_session(authorization: Optional[str], request: Request = None) -> Optional[str]:
    """Helper to extract user_id from Bearer token or session cookie"""
    global _db
    
    # Try session-based auth first (Google OAuth)
    session_token = None
    if request:
        session_token = request.cookies.get("session_token")
    
    # Check Authorization header
    if not session_token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            session_token = parts[1]
    
    if session_token and _db is not None:
        # Try new session-based auth
        session_doc = await _db.user_sessions.find_one(
            {"session_token": session_token},
            {"_id": 0}
        )
        
        if session_doc:
            expires_at = session_doc.get("expires_at")
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if expires_at > datetime.now(timezone.utc):
                return session_doc["user_id"]
    
    # Fallback to old JWT auth
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
            auth_service = get_auth_service()
            payload = auth_service.verify_token(token)
            if payload:
                return payload.get('user_id')
    
    return None


def _extract_user_id(authorization: Optional[str]) -> Optional[str]:
    """Legacy helper to extract user_id from Bearer token (for sync contexts)"""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    token = parts[1]
    auth_service = get_auth_service()
    payload = auth_service.verify_token(token)
    
    if not payload:
        return None
    
    return payload.get('user_id')


@router.get("/")
async def get_profile(request: Request, authorization: Optional[str] = Header(None)):
    """
    Get current user's profile.
    
    Headers:
    Authorization: Bearer <token>
    
    Response:
    {
      "ok": true,
      "profile": {
        "name": "Sharad",
        "dob": "1986-01-24",
        "tob": "06:32",
        "location": "Rohtak, Haryana"
      }
    }
    """
    global _db
    try:
        user_id = await _extract_user_id_with_session(authorization, request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Try new MongoDB users collection first
        if _db is not None:
            user_doc = await _db.users.find_one({"user_id": user_id}, {"_id": 0})
            if user_doc:
                return {
                    "ok": True,
                    "profile": {
                        "name": user_doc.get("name"),
                        "dob": user_doc.get("dob"),
                        "tob": user_doc.get("tob"),
                        "location": user_doc.get("pob") or user_doc.get("location"),
                        "gender": user_doc.get("gender"),
                        "marital_status": user_doc.get("marital_status")
                    }
                }
        
        # Fallback to old auth service
        auth_service = get_auth_service()
        profile = auth_service.get_profile(user_id)
        
        return {
            "ok": True,
            "profile": profile
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/")
async def update_profile(
    req: UserProfileRequest,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Create or update user profile.
    
    Headers:
    Authorization: Bearer <token>
    
    Request:
    {
      "name": "Sharad",
      "dob": "1986-01-24",
      "tob": "06:32",
      "location": "Rohtak, Haryana"
    }
    
    Response:
    { "ok": true, "profile_complete": true }
    """
    global _db
    try:
        user_id = await _extract_user_id_with_session(authorization, request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Validate dates
        try:
            # Basic validation: can parse as ISO date
            year, month, day = req.dob.split('-')
            int(year), int(month), int(day)
            
            # Basic validation: can parse as time
            hour, minute = req.tob.split(':')
            int(hour), int(minute)
        except (ValueError, AttributeError):
            raise HTTPException(status_code=400, detail="Invalid date or time format")
        
        # Try to save to new MongoDB users collection first
        if _db is not None:
            update_data = {
                'name': req.name,
                'dob': req.dob,
                'tob': req.tob,
                'pob': req.location,
                'location': req.location,
                'birth_place_lat': req.birth_place_lat,
                'birth_place_lon': req.birth_place_lon,
                'birth_place_tz': req.birth_place_tz,
                'profile_complete': True,
                'updated_at': datetime.now(timezone.utc)
            }
            
            # Add gender and marital status if provided
            if hasattr(req, 'gender') and req.gender:
                update_data['gender'] = req.gender
            if hasattr(req, 'marital_status') and req.marital_status:
                update_data['marital_status'] = req.marital_status
            
            result = await _db.users.update_one(
                {"user_id": user_id},
                {"$set": update_data},
                upsert=True
            )
            
            if result.modified_count > 0 or result.upserted_id:
                logger.info(f"Profile saved to MongoDB for user {user_id}")
                return {
                    "ok": True,
                    "profile_complete": True
                }
        
        # Fallback to old auth service
        auth_service = get_auth_service()
        success = auth_service.save_profile(user_id, {
            'name': req.name,
            'dob': req.dob,
            'tob': req.tob,
            'location': req.location,
            'birth_place_lat': req.birth_place_lat,
            'birth_place_lon': req.birth_place_lon,
            'birth_place_tz': req.birth_place_tz,
        })
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to save profile")
        
        return {
            "ok": True,
            "profile_complete": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/welcome")
async def get_welcome_message(authorization: Optional[str] = Header(None)):
    """
    Generate high-trust, chart-anchored, confidence-aware personalized welcome.
    
    This is a single-message experience shown immediately after onboarding.
    Uses dedicated WelcomeMessageBuilder (NOT the normal chat flow).
    
    Content Structure:
    A. Introduction (fixed): "Welcome, {name}. I'm Niro, a trained AI astrologer."
    B. Personality Insight: Based on Moon sign + Ascendant + Lagna lord
    C. Past Pattern: Only if confidence >= threshold (currently skipped)
    D. Current Life Phase: Mahadasha/Antardasha insight (actionable)
    E. Closing Prompt: "What would you like to explore today?"
    
    Confidence Guardrails:
    - Sections are SKIPPED if confidence is low
    - Silence is better than generic astrology
    
    Headers:
    Authorization: Bearer <token>
    
    Response:
    {
      "ok": true,
      "welcome_message": "Welcome, Sharad. I'm Niro, a trained AI astrologer...",
      "suggested_questions": [...],
      "confidence_map": {
        "personality": "high" | "medium" | null,
        "past_theme": "high" | null,
        "current_phase": "high" | "medium" | null
      },
      "word_count": 150,
      "sections_included": ["introduction", "personality", "current_phase", "closing"]
    }
    """
    try:
        user_id = _extract_user_id(authorization)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Get user profile
        auth_service = get_auth_service()
        profile = auth_service.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Import dependencies
        from backend.astro_client.models import BirthDetails
        from backend.astro_client.vedic_api import vedic_api_client
        from backend.conversation.welcome_builder import generate_welcome_message as build_welcome
        import datetime
        
        name = profile.get('name', 'Friend')
        first_name = name.split()[0] if name else 'Friend'
        
        # Initialize astro_profile dict for WelcomeMessageBuilder
        astro_profile = {
            'moon_sign': None,
            'ascendant': None,
            'current_mahadasha': {},
            'current_antardasha': {}
        }
        
        # Fetch FULL astro profile for comprehensive welcome message
        try:
            # Build birth details from profile
            birth = BirthDetails(
                dob=datetime.datetime.strptime(profile['dob'], '%Y-%m-%d').date(),
                tob=profile['tob'],
                location=profile['location'],
                latitude=profile.get('birth_place_lat'),
                longitude=profile.get('birth_place_lon'),
                timezone=profile.get('birth_place_tz', 5.5)
            )
            
            # Fetch FULL profile (includes dasha data) for welcome message
            # This gives us moon_sign, ascendant, AND current_mahadasha for phase insights
            full_profile = await vedic_api_client.fetch_full_profile(birth, user_id=user_id)
            
            if full_profile:
                # Convert AstroProfile to dict for the builder
                if hasattr(full_profile, 'model_dump'):
                    astro_profile = full_profile.model_dump()
                elif hasattr(full_profile, 'dict'):
                    astro_profile = full_profile.dict()
                else:
                    astro_profile = {
                        'moon_sign': getattr(full_profile, 'moon_sign', None),
                        'ascendant': getattr(full_profile, 'ascendant', None),
                        'current_mahadasha': getattr(full_profile, 'current_mahadasha', {}),
                        'current_antardasha': getattr(full_profile, 'current_antardasha', {})
                    }
                
                logger.info(f"[WELCOME] Fetched full profile: moon={astro_profile.get('moon_sign')}, "
                           f"asc={astro_profile.get('ascendant')}, "
                           f"dasha={astro_profile.get('current_mahadasha', {}).get('planet', 'N/A')}")
        except Exception as e:
            logger.warning(f"[WELCOME] Could not fetch full astro profile: {e}")
            # Continue with empty astro_profile - builder handles gracefully
        
        # Generate welcome message using dedicated WelcomeMessageBuilder
        logger.info(f"[WELCOME] Building personalized welcome for user {user_id}")
        welcome_result = await build_welcome(
            first_name=first_name,
            astro_profile=astro_profile,
            signals=None  # Future: pass reading_pack signals for past theme detection
        )
        
        # Generate context-aware suggested questions
        suggested_questions = _generate_suggested_questions(astro_profile)
        
        return {
            "ok": True,
            "welcome_message": welcome_result['welcome_message'],
            "suggested_questions": suggested_questions,
            "confidence_map": welcome_result['confidence_map'],
            "word_count": welcome_result['word_count'],
            "sections_included": welcome_result['sections_included']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_welcome_message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


def _generate_suggested_questions(astro_profile: dict) -> list:
    """Generate context-aware suggested questions based on astro profile."""
    
    # Base questions that work for everyone
    questions = [
        "What career path aligns with my chart?",
        "What about my relationships?",
        "What should I focus on right now?"
    ]
    
    # Add phase-specific question if we have dasha data
    mahadasha = astro_profile.get('current_mahadasha', {})
    if hasattr(mahadasha, 'model_dump'):
        mahadasha = mahadasha.model_dump()
    
    dasha_planet = mahadasha.get('planet', '') if mahadasha else ''
    
    if dasha_planet:
        # Add a question relevant to their current dasha
        dasha_questions = {
            'Sun': "How can I step into more leadership this year?",
            'Moon': "How can I better honor my emotional needs?",
            'Mars': "Where should I channel my drive right now?",
            'Mercury': "What skills should I develop now?",
            'Jupiter': "What growth opportunities should I pursue?",
            'Venus': "How can I improve my relationships?",
            'Saturn': "What foundations should I focus on building?",
            'Rahu': "What new directions are calling me?",
            'Ketu': "What should I let go of?"
        }
        if dasha_planet in dasha_questions:
            questions.insert(1, dasha_questions[dasha_planet])
    
    # Add timing question
    questions.append("When is a good time for new ventures?")
    
    return questions[:5]  # Return max 5 questions

