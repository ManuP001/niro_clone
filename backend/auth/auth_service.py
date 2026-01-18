"""Authentication service"""

import uuid
import logging
from typing import Optional, Dict, Any

from .otp_manager import get_otp_manager
from .jwt_handler import get_jwt_handler
from .store import get_user_store_instance, get_profile_store_instance
from .models import User, UserProfile

logger = logging.getLogger(__name__)


class AuthService:
    """Main authentication service"""
    
    def __init__(self):
        self.otp_manager = get_otp_manager()
        self.jwt_handler = get_jwt_handler()
        self.user_store = get_user_store_instance()
        self.profile_store = get_profile_store_instance()
    
    def request_otp(self, identifier: str) -> tuple[bool, int]:
        """
        Request OTP for identifier.
        Returns (success, expires_in_seconds)
        """
        try:
            # Check or create user
            existing_user = self.user_store.get_user_by_identifier(identifier)
            if not existing_user:
                user_id = str(uuid.uuid4())
                self.user_store.create_user(user_id, identifier)
            
            # Generate OTP
            otp, expires_in = self.otp_manager.generate_otp(identifier)
            logger.info(f"OTP requested for {identifier}")
            return True, expires_in
        except Exception as e:
            logger.error(f"Error requesting OTP: {e}")
            return False, 0
    
    def verify_otp(self, identifier: str, otp: str) -> Optional[tuple[str, str]]:
        """
        Verify OTP and return (token, user_id) if valid, None otherwise.
        """
        try:
            # Verify OTP
            if not self.otp_manager.verify_otp(identifier, otp):
                return None
            
            # Get or create user
            user = self.user_store.get_user_by_identifier(identifier)
            if not user:
                user_id = str(uuid.uuid4())
                self.user_store.create_user(user_id, identifier)
                user = {'id': user_id, 'identifier': identifier}
            
            user_id = user['id']
            
            # Generate JWT token
            profile = self.profile_store.get_profile(user_id)
            payload = {
                'user_id': user_id,
                'identifier': identifier,
                'profile_complete': profile is not None
            }
            token = self.jwt_handler.encode(payload)
            
            logger.info(f"OTP verified successfully for {identifier}, user_id={user_id}")
            return token, user_id
        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload if valid.
        """
        try:
            payload = self.jwt_handler.decode(token)
            return payload
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user info including profile status.
        """
        try:
            user = self.user_store.get_user(user_id)
            if not user:
                return None
            
            profile = self.profile_store.get_profile(user_id)
            
            return {
                'id': user['id'],
                'identifier': user['identifier'],
                'profile_complete': profile is not None
            }
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def save_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Save user profile.
        """
        try:
            # Validate profile data
            required_fields = ['name', 'dob', 'tob', 'location']
            if not all(field in profile_data for field in required_fields):
                logger.warning(f"Missing required profile fields for user {user_id}")
                return False
            
            # Save profile (include optional lat/lon/tz if provided)
            profile_to_save = {
                field: profile_data[field] for field in required_fields
            }
            # Add optional fields
            if 'birth_place_lat' in profile_data:
                profile_to_save['birth_place_lat'] = profile_data['birth_place_lat']
            if 'birth_place_lon' in profile_data:
                profile_to_save['birth_place_lon'] = profile_data['birth_place_lon']
            if 'birth_place_tz' in profile_data:
                profile_to_save['birth_place_tz'] = profile_data['birth_place_tz']
            else:
                profile_to_save['birth_place_tz'] = 5.5  # Default to IST
            
            # Add gender and marital_status (new fields)
            if 'gender' in profile_data:
                profile_to_save['gender'] = profile_data['gender']
            if 'marital_status' in profile_data:
                profile_to_save['marital_status'] = profile_data['marital_status']
            
            success = self.profile_store.save_profile(user_id, profile_to_save)
            
            if success:
                logger.info(f"Profile saved successfully for user {user_id}")
            return success
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            return False
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile.
        """
        try:
            return self.profile_store.get_profile(user_id)
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None


# Lazy-initialized singleton
_auth_service = None


def get_auth_service() -> AuthService:
    """Get or create auth service"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
