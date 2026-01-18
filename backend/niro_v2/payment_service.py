"""NIRO V2 Payment Service

Razorpay integration for package and remedy purchases.
"""

import os
import logging
import razorpay
from typing import Optional, Dict, Any
import hmac
import hashlib

logger = logging.getLogger(__name__)


class PaymentService:
    """Razorpay payment integration service"""
    
    def __init__(self):
        self.key_id = os.environ.get('RAZORPAY_KEY_ID', '')
        self.key_secret = os.environ.get('RAZORPAY_KEY_SECRET', '')
        
        if self.key_id and self.key_secret:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            self.initialized = True
            logger.info("PaymentService initialized with Razorpay credentials")
        else:
            self.client = None
            self.initialized = False
            logger.warning("PaymentService: Razorpay credentials not found, running in mock mode")
    
    def create_order(
        self,
        amount_inr: int,
        currency: str = "INR",
        receipt: str = None,
        notes: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order.
        
        Args:
            amount_inr: Amount in INR (will be converted to paise)
            currency: Currency code (default INR)
            receipt: Receipt ID for tracking
            notes: Additional metadata
            
        Returns:
            Razorpay order object with id, amount, etc.
        """
        if not self.initialized:
            # Mock mode for testing
            import uuid
            mock_order_id = f"order_mock_{uuid.uuid4().hex[:12]}"
            logger.info(f"Mock order created: {mock_order_id}")
            return {
                "id": mock_order_id,
                "entity": "order",
                "amount": amount_inr * 100,  # Convert to paise
                "amount_paid": 0,
                "amount_due": amount_inr * 100,
                "currency": currency,
                "receipt": receipt,
                "status": "created",
                "notes": notes or {}
            }
        
        try:
            order_data = {
                "amount": amount_inr * 100,  # Razorpay expects paise
                "currency": currency,
                "receipt": receipt,
                "notes": notes or {}
            }
            
            order = self.client.order.create(data=order_data)
            logger.info(f"Razorpay order created: {order['id']} for ₹{amount_inr}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {e}")
            raise Exception(f"Payment order creation failed: {str(e)}")
    
    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature.
        
        Args:
            razorpay_order_id: Order ID from Razorpay
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature from Razorpay
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.initialized:
            # Mock mode - accept all payments
            logger.info(f"Mock payment verification: {razorpay_payment_id}")
            return True
        
        try:
            # Generate expected signature
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            expected_signature = hmac.new(
                self.key_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(expected_signature, razorpay_signature)
            
            if is_valid:
                logger.info(f"Payment signature verified: {razorpay_payment_id}")
            else:
                logger.warning(f"Invalid payment signature: {razorpay_payment_id}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def fetch_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch payment details from Razorpay.
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            Payment object or None if not found
        """
        if not self.initialized:
            return {
                "id": payment_id,
                "entity": "payment",
                "amount": 0,
                "currency": "INR",
                "status": "captured",
                "method": "mock"
            }
        
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Failed to fetch payment {payment_id}: {e}")
            return None
    
    def refund_payment(
        self,
        payment_id: str,
        amount_inr: Optional[int] = None,
        notes: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a refund for a payment.
        
        Args:
            payment_id: Razorpay payment ID
            amount_inr: Amount to refund (None for full refund)
            notes: Additional metadata
            
        Returns:
            Refund object or None if failed
        """
        if not self.initialized:
            import uuid
            return {
                "id": f"rfnd_mock_{uuid.uuid4().hex[:8]}",
                "entity": "refund",
                "payment_id": payment_id,
                "amount": amount_inr * 100 if amount_inr else 0,
                "status": "processed"
            }
        
        try:
            refund_data = {"notes": notes or {}}
            if amount_inr:
                refund_data["amount"] = amount_inr * 100
            
            refund = self.client.payment.refund(payment_id, refund_data)
            logger.info(f"Refund created for payment {payment_id}")
            return refund
            
        except Exception as e:
            logger.error(f"Failed to create refund: {e}")
            return None
    
    def get_checkout_options(
        self,
        order_id: str,
        amount_inr: int,
        user_name: str = "",
        user_email: str = "",
        user_phone: str = "",
        description: str = "NIRO Package Purchase"
    ) -> Dict[str, Any]:
        """
        Get Razorpay checkout options for frontend.
        
        Args:
            order_id: Razorpay order ID
            amount_inr: Amount in INR
            user_name: Customer name
            user_email: Customer email
            user_phone: Customer phone
            description: Payment description
            
        Returns:
            Checkout configuration for Razorpay SDK
        """
        return {
            "key": self.key_id,
            "amount": amount_inr * 100,
            "currency": "INR",
            "name": "NIRO",
            "description": description,
            "order_id": order_id,
            "prefill": {
                "name": user_name,
                "email": user_email,
                "contact": user_phone
            },
            "notes": {},
            "theme": {
                "color": "#6366f1"  # Indigo theme
            }
        }


# Singleton instance
_payment_service: Optional[PaymentService] = None


def get_payment_service() -> PaymentService:
    """Get or create payment service singleton"""
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService()
    return _payment_service
