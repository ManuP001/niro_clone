"""User profile API endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from backend.auth.auth_service import get_auth_service
from backend.auth.models import (
    ProfileResponse,
    ProfileUpdateResponse,
    UserProfileRequest,
    UserProfile
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _extract_user_id(authorization: Optional[str]) -> Optional[str]:
    """Helper to extract user_id from Bearer token"""
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
async def get_profile(authorization: Optional[str] = Header(None)):
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
    try:
        user_id = _extract_user_id(authorization)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
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
    try:
        user_id = _extract_user_id(authorization)
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
        
        # Save profile
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
    Generate personalized welcome message after onboarding.
    
    Uses user's birth chart data (ascendant, moon, sun) to generate
    3 personalized strengths based on Vedic astrology traits.
    
    Returns NEW response format with welcome_message (string) + suggested_questions (list).
    
    Headers:
    Authorization: Bearer <token>
    
    Response:
    {
      "ok": true,
      "welcome_message": "Hey Sharad. I've looked at your chart. You come across as...",
      "suggested_questions": [
        "What career path aligns with my chart?",
        "What about my relationships?",
        "When is a good time for new ventures?",
        "How can I leverage my strengths?",
        "What should I focus on in the next 30 days?"
      ]
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
        
        # Try to fetch astro profile for chart data
        from backend.astro_client.models import BirthDetails
        from backend.astro_client.vedic_api import vedic_api_client
        from backend.welcome_traits import create_welcome_message
        from backend.niro_logging.pipeline_logger import get_pipeline_logger
        
        name = profile.get('name', 'Friend')
        ascendant = None
        moon_sign = None
        sun_sign = None
        
        # Try to get chart data from Vedic API using birth details
        # Using lightweight fetch_basic_chart_info (single API call) instead of full profile
        try:
            # Build birth details from profile
            birth = BirthDetails(
                dob=__import__('datetime').datetime.strptime(profile['dob'], '%Y-%m-%d').date(),
                tob=profile['tob'],
                location=profile['location'],
                latitude=profile.get('birth_place_lat'),
                longitude=profile.get('birth_place_lon'),
                timezone=profile.get('birth_place_tz', 5.5)
            )
            
            # Fetch BASIC chart info (single API call) for welcome message
            chart_info = await vedic_api_client.fetch_basic_chart_info(birth)
            
            if chart_info:
                ascendant = chart_info.get('ascendant')
                moon_sign = chart_info.get('moon_sign')
                sun_sign = chart_info.get('sun_sign')
                logger.info(f"Fetched basic chart for welcome: ascendant={ascendant}, moon={moon_sign}, sun={sun_sign}")
        except Exception as e:
            logger.debug(f"Could not fetch chart info for welcome message: {e}")
            # Continue without chart data - will use defaults
        
        # Log welcome generation
        try:
            pipeline_logger = get_pipeline_logger()
            pipeline_logger.log_event({
                "event_type": "WELCOME",
                "user_id": user_id,
                "ascendant": ascendant,
                "moon": moon_sign,
                "sun": sun_sign
            })
        except Exception as e:
            logger.debug(f"Could not log welcome event: {e}")
        
        # Generate welcome message with actual kundli data
        welcome = create_welcome_message(name, ascendant, moon_sign, sun_sign)
        
        # Extract the warm message text (without legacy fields)
        welcome_message = welcome.get('message', f"Welcome, {name}! Your chart is ready.")
        
        # Generate suggested questions based on chart
        suggested_questions = [
            "What does my Sun sign reveal about my core essence?",
            "How can I leverage my Moon sign strengths in relationships?",
            "What career path aligns with my chart?",
            "When is a good time for new ventures?",
            "What should I focus on in the next 30 days?"
        ]
        
        return {
            "ok": True,
            "welcome_message": welcome_message,
            "suggested_questions": suggested_questions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_welcome_message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

