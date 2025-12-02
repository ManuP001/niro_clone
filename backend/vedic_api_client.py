"""
Simple VedicAstroAPI client - Pre-written code for reliable API calls
This bypasses the AI code generation for MVP to ensure reliability
"""
import os
import requests
from typing import Dict, Any

class VedicAstroClient:
    def __init__(self):
        self.api_key = os.environ.get('VEDIC_API_KEY')
        self.base_url = os.environ.get('VEDIC_API_BASE_URL')
        
    def get_planet_details(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict[str, Any]:
        """
        Get planetary details from VedicAstroAPI
        
        Args:
            dob: Date of birth (DD-MM-YYYY format will be converted to DD/MM/YYYY)
            tob: Time of birth (HH:MM format)
            lat: Latitude
            lon: Longitude
            tz: Timezone offset (default 5.5 for IST)
        
        Returns:
            Dict containing planetary data
        """
        # Convert DD-MM-YYYY to DD/MM/YYYY
        dob_formatted = dob.replace('-', '/')
        
        try:
            response = requests.get(
                f"{self.base_url}/horoscope/planet-details",
                params={
                    'api_key': self.api_key,
                    'dob': dob_formatted,
                    'tob': tob,
                    'lat': lat,
                    'lon': lon,
                    'tz': tz
                },
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 200:
                return {
                    "success": True, 
                    "data": data.get('response', {}),
                    "remaining_calls": data.get('remaining_api_calls', 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {data.get('status')}: {data.get('response', 'Unknown error')}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
