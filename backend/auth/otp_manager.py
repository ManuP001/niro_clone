"""OTP management for authentication"""

import random
import string
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OTPManager:
    """Manages OTP generation and validation with dev-safe logging"""
    
    def __init__(self, otp_length: int = 6, expiry_seconds: int = 300):
        self.otp_length = otp_length
        self.expiry_seconds = expiry_seconds
        self.otps: Dict[str, dict] = {}  # {identifier: {otp, created_at, attempts}}
    
    def generate_otp(self, identifier: str) -> tuple[str, int]:
        """
        Generate OTP for identifier.
        Returns (otp, expires_in_seconds)
        
        In dev/local, logs OTP with [DEV_OTP] marker for easy testing.
        """
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=self.otp_length))
        
        # Store with expiry
        self.otps[identifier] = {
            'otp': otp,
            'created_at': datetime.utcnow(),
            'attempts': 0,
            'max_attempts': 5
        }
        
        # DEV LOGGING - clearly marked for local testing
        logger.info(f"[DEV_OTP] Generated OTP for {identifier}: {otp}")
        
        return otp, self.expiry_seconds
    
    def verify_otp(self, identifier: str, otp: str) -> bool:
        """Verify OTP. Returns True if valid, False otherwise."""
        if identifier not in self.otps:
            logger.warning(f"OTP verification failed: identifier {identifier} not found")
            return False
        
        record = self.otps[identifier]
        
        # Check expiry
        if datetime.utcnow() - record['created_at'] > timedelta(seconds=self.expiry_seconds):
            logger.warning(f"OTP verification failed: OTP expired for {identifier}")
            del self.otps[identifier]
            return False
        
        # Check OTP first
        if record['otp'] == otp:
            del self.otps[identifier]
            logger.info(f"[DEV_OTP] OTP verified successfully for {identifier}")
            return True
        
        # Increment attempts on wrong OTP
        record['attempts'] += 1
        
        # Check if max attempts exceeded
        if record['attempts'] >= record['max_attempts']:
            logger.warning(f"OTP verification failed: max attempts exceeded for {identifier}")
            del self.otps[identifier]
            return False
        
        logger.warning(f"OTP verification failed: invalid OTP for {identifier} (attempt {record['attempts']})")
        return False
    
    def clear_expired(self):
        """Clean up expired OTPs (housekeeping)"""
        now = datetime.utcnow()
        expired = [
            ident for ident, record in self.otps.items()
            if now - record['created_at'] > timedelta(seconds=self.expiry_seconds)
        ]
        for ident in expired:
            del self.otps[ident]


# Lazy-initialized singleton
_otp_manager = None


def get_otp_manager() -> OTPManager:
    """Get or create OTP manager"""
    global _otp_manager
    if _otp_manager is None:
        _otp_manager = OTPManager()
    return _otp_manager
