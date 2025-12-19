"""
AI Provider Router
Routes requests to OpenAI (default) first, falls back to Gemini when needed
"""

import logging
from typing import Dict, Any, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class Provider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


class ProviderRouter:
    """
    Routes AI requests to providers with intelligent fallback
    - Primary: OpenAI GPT-4o-mini (default)
    - Fallback: Gemini Flash (when OpenAI fails)
    """
    
    def __init__(self, gemini_agent, openai_agent, default_provider: Provider = Provider.GEMINI):
        self.gemini_agent = gemini_agent
        self.openai_agent = openai_agent
        self.default_provider = default_provider
        self.metrics = {
            'gemini_calls': 0,
            'openai_calls': 0,
            'gemini_errors': 0,
            'openai_errors': 0,
            'fallbacks': 0
        }
    
    def route(
        self,
        operation: str,
        openai_func: Callable,
        gemini_func: Callable,
        *args,
        **kwargs
    ) -> tuple[Any, Provider]:
        """
        Execute operation with automatic fallback
        
        Args:
            operation: Name of the operation (for logging)
            openai_func: Function to call on OpenAI agent
            gemini_func: Function to call on Gemini agent
            *args, **kwargs: Arguments to pass to the functions
            
        Returns:
            Tuple of (result, provider_used)
        """
        # Try OpenAI first
        try:
            logger.info(f"{operation}: Attempting with OpenAI")
            self.metrics['openai_calls'] += 1
            result = openai_func(*args, **kwargs)
            logger.info(f"{operation}: OpenAI succeeded")
            return result, Provider.OPENAI
            
        except Exception as e:
            error_msg = str(e).lower()
            self.metrics['openai_errors'] += 1
            
            # Check if it's a quota/rate limit error
            is_quota_error = any(keyword in error_msg for keyword in [
                'quota', 'rate limit', 'resource exhausted', '429', 'exceeded'
            ])
            
            if is_quota_error:
                logger.warning(f"{operation}: OpenAI quota exceeded, falling back to Gemini")
            else:
                logger.warning(f"{operation}: OpenAI failed ({str(e)}), falling back to Gemini")
            
            # Fallback to Gemini
            try:
                self.metrics['fallbacks'] += 1
                self.metrics['gemini_calls'] += 1
                logger.info(f"{operation}: Attempting with Gemini")
                result = gemini_func(*args, **kwargs)
                logger.info(f"{operation}: Gemini succeeded")
                return result, Provider.GEMINI
                
            except Exception as gemini_error:
                self.metrics['gemini_errors'] += 1
                logger.error(f"{operation}: Both providers failed. OpenAI: {str(e)}, Gemini: {str(gemini_error)}")
                raise Exception(f"All providers failed. Last error: {str(gemini_error)}")
    
    def call_with_fallback(
        self,
        operation: str,
        gemini_func: Callable,
        openai_func: Callable,
        *args,
        **kwargs
    ) -> tuple[Any, Provider]:
        """
        Execute operation with automatic fallback (legacy method, redirects to route)
        
        Args:
            operation: Name of the operation (for logging)
            gemini_func: Function to call on Gemini agent
            openai_func: Function to call on OpenAI agent
            *args, **kwargs: Arguments to pass to the functions
            
        Returns:
            Tuple of (result, provider_used)
        """
        # Redirect to route with OpenAI first
        return self.route(operation, openai_func, gemini_func, *args, **kwargs)
    
    def extract_json(self, prompt: str) -> tuple[Dict[str, Any], Provider]:
        """Extract JSON with fallback - OpenAI first, Gemini fallback"""
        return self.route(
            "extract_json",
            self.openai_agent.extract_json,
            self.gemini_agent.extract_json,
            prompt
        )
    
    def generate_text(self, prompt: str, temperature: float = 0.7) -> tuple[str, Provider]:
        """Generate text with fallback - OpenAI first, Gemini fallback"""
        return self.route(
            "generate_text",
            self.openai_agent.generate_text,
            lambda p, t: self.gemini_agent._call_model(
                self.gemini_agent.flash_model, p, temperature=t
            ),
            prompt,
            temperature
        )
    
    def get_metrics(self) -> Dict[str, int]:
        """Get usage metrics"""
        return self.metrics.copy()
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        return {
            'gemini': self.gemini_agent.health_check() if hasattr(self.gemini_agent, 'health_check') else True,
            'openai': self.openai_agent.health_check() if hasattr(self.openai_agent, 'health_check') else True
        }
