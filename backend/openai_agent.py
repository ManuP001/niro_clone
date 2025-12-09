"""
OpenAI Provider Agent
Handles OpenAI API calls for chat extraction and interpretation
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OpenAIAgent:
    """Wrapper for OpenAI API calls"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OpenAI API key not found")
        
        self.model = "gpt-4o-mini"  # Fast, cost-effective model
        self.base_url = "https://api.openai.com/v1"
    
    def _call_openai(self, prompt: str, temperature: float = 0.1) -> str:
        """
        Call OpenAI API with the given prompt
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            
        Returns:
            The model's response text
        """
        import requests
        
        if not self.api_key:
            raise Exception("OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request failed: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def extract_json(self, prompt: str) -> Dict[str, Any]:
        """
        Call OpenAI and extract JSON from response
        
        Args:
            prompt: Prompt requesting JSON output
            
        Returns:
            Parsed JSON dictionary
        """
        response_text = self._call_openai(prompt, temperature=0.1)
        
        # Extract JSON from response
        try:
            # Try to find JSON in markdown blocks first
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenAI: {e}")
            logger.error(f"Response was: {response_text}")
            raise Exception("Failed to parse OpenAI JSON response")
    
    def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text using OpenAI
        
        Args:
            prompt: The prompt
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        return self._call_openai(prompt, temperature=temperature)
    
    def health_check(self) -> bool:
        """Check if OpenAI API is accessible"""
        if not self.api_key:
            return False
        
        try:
            import requests
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
