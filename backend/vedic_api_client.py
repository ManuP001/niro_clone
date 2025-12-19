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
    def get_chart(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict[str, Any]:
        """
        Get complete birth chart data from VedicAstroAPI.
        
        This is the main method used by astro_compute_engine for full profile computation.
        Fetches planets, houses, ascendant, and other astrological data.
        
        Args:
            dob: Date of birth (DD-MM-YYYY format will be converted to DD/MM/YYYY)
            tob: Time of birth (HH:MM format)
            lat: Latitude
            lon: Longitude
            tz: Timezone offset (default 5.5 for IST)
        
        Returns:
            Dict containing:
            {
                "success": bool,
                "data": {
                    "planets": [...],
                    "houses": [...],
                    "ascendant": str,
                    "sun_sign": str,
                    "moon_sign": str,
                    ...
                },
                "remaining_calls": int (if success),
                "error": str (if failure)
            }
        """
        # Convert DD-MM-YYYY to DD/MM/YYYY
        dob_formatted = dob.replace('-', '/')
        
        try:
            # Call extended-kundli-details endpoint for complete chart data
            response = requests.get(
                f"{self.base_url}/extended-horoscope/extended-kundli-details",
                params={
                    'api_key': self.api_key,
                    'dob': dob_formatted,
                    'tob': tob,
                    'lat': lat,
                    'lon': lon,
                    'tz': tz,
                    'lang': 'en'
                },
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 200:
                response_data = data.get('response', {})
                
                # Extract key chart data
                planets = response_data.get('planets', [])
                houses = response_data.get('houses', [])
                ascendant = response_data.get('ascendant', {}).get('name', 'Unknown')
                sun_sign = response_data.get('sun_sign', {}).get('name', 'Unknown')
                moon_sign = response_data.get('moon_sign', {}).get('name', 'Unknown')
                
                return {
                    "success": True,
                    "data": {
                        "planets": planets,
                        "houses": houses,
                        "ascendant": ascendant,
                        "sun_sign": sun_sign,
                        "moon_sign": moon_sign,
                        "raw_response": response_data
                    },
                    "remaining_calls": data.get('remaining_api_calls', 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {data.get('status')}: {data.get('message', 'Unknown error')}"
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