"""JWT token handling"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import base64
import hmac
import hashlib

logger = logging.getLogger(__name__)


class JWTHandler:
    """Simple JWT handler for auth tokens"""
    
    def __init__(self, secret: Optional[str] = None):
        self.secret = secret or os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-prod')
    
    def encode(self, payload: Dict[str, Any], expires_in: int = 86400) -> str:
        """
        Encode a JWT token.
        
        Args:
            payload: Dictionary to encode
            expires_in: Expiry time in seconds (default 24h)
        
        Returns:
            JWT token string
        """
        # Add expiry to payload
        now = datetime.utcnow()
        payload['iat'] = int(now.timestamp())
        payload['exp'] = int((now + timedelta(seconds=expires_in)).timestamp())
        
        # Encode header and payload
        header = {'alg': 'HS256', 'typ': 'JWT'}
        header_encoded = self._base64url_encode(json.dumps(header))
        payload_encoded = self._base64url_encode(json.dumps(payload))
        
        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = self._base64url_encode(
            hmac.new(
                self.secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        )
        
        token = f"{message}.{signature}"
        logger.info(f"[AUTH] JWT token generated for user_id={payload.get('user_id')}")
        return token
    
    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and verify JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            parts = token.split('.')
            if len(parts) != 3:
                logger.warning("[AUTH] Invalid token format")
                return None
            
            header_encoded, payload_encoded, signature_provided = parts
            
            # Verify signature
            message = f"{header_encoded}.{payload_encoded}"
            expected_signature = self._base64url_encode(
                hmac.new(
                    self.secret.encode(),
                    message.encode(),
                    hashlib.sha256
                ).digest()
            )
            
            if signature_provided != expected_signature:
                logger.warning("[AUTH] Invalid token signature")
                return None
            
            # Decode payload
            payload = json.loads(self._base64url_decode(payload_encoded))
            
            # Check expiry
            if payload.get('exp', 0) < datetime.utcnow().timestamp():
                logger.warning("[AUTH] Token expired")
                return None
            
            return payload
            
        except Exception as e:
            logger.error(f"[AUTH] Token decode error: {e}")
            return None
    
    @staticmethod
    def _base64url_encode(data) -> str:
        """Base64 URL encode - handles both str and bytes"""
        if isinstance(data, str):
            data = data.encode()
        return base64.urlsafe_b64encode(data).decode().rstrip('=')
    
    @staticmethod
    def _base64url_decode(data: str) -> str:
        """Base64 URL decode"""
        # Add padding if needed
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data).decode()


# Lazy-initialized singleton
_jwt_handler = None


def get_jwt_handler() -> JWTHandler:
    """Get or create JWT handler"""
    global _jwt_handler
    if _jwt_handler is None:
        _jwt_handler = JWTHandler()
    return _jwt_handler
