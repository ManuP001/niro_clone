"""
City Autocomplete Service
Integrates with GeoNames API for comprehensive city search with lat/long
"""
import os
import requests
import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class CityService:
    """
    City search and geolocation service using GeoNames API
    Free tier: 2000 requests per hour
    """
    
    def __init__(self):
        # GeoNames free API - register at https://www.geonames.org/login
        # For now, using demo account (limited)
        self.username = os.environ.get('GEONAMES_USERNAME', 'demo')
        self.base_url = 'http://api.geonames.org'
    
    @lru_cache(maxsize=1000)
    def search_cities(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search cities with autocomplete
        
        Args:
            query: Search query (min 3 characters)
            max_results: Maximum number of results to return
        
        Returns:
            List of city dictionaries with name, country, lat, lon
        """
        
        if len(query) < 3:
            return []
        
        try:
            # GeoNames search endpoint with cities filter
            params = {
                'name_startsWith': query,
                'maxRows': max_results,
                'username': self.username,
                'featureClass': 'P',  # P = cities, towns, villages
                'orderby': 'population',  # Order by population (most relevant first)
                'type': 'json',
                'style': 'MEDIUM'
            }
            
            response = requests.get(
                f'{self.base_url}/searchJSON',
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                cities = []
                for item in data.get('geonames', []):
                    city_data = {
                        'id': item.get('geonameId'),
                        'name': item.get('name'),
                        'country': item.get('countryName'),
                        'country_code': item.get('countryCode'),
                        'state': item.get('adminName1', ''),
                        'lat': float(item.get('lat')),
                        'lon': float(item.get('lng')),
                        'population': item.get('population', 0),
                        'timezone': item.get('timezone', {}).get('timeZoneId', 'UTC'),
                        'display_name': self._format_display_name(item)
                    }
                    cities.append(city_data)
                
                logger.info(f"Found {len(cities)} cities for query: {query}")
                return cities
            else:
                logger.error(f"GeoNames API error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in city search: {str(e)}")
            return []
    
    def _format_display_name(self, item: Dict[str, Any]) -> str:
        """Format city display name with location context"""
        name = item.get('name', '')
        admin1 = item.get('adminName1', '')
        country = item.get('countryName', '')
        
        # Format: "City, State, Country" or "City, Country" if no state
        parts = [name]
        if admin1 and admin1 != name:
            parts.append(admin1)
        if country:
            parts.append(country)
        
        return ', '.join(parts)
    
    def get_city_by_id(self, geoname_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed city information by GeoNames ID
        
        Args:
            geoname_id: GeoNames unique ID
        
        Returns:
            City dictionary or None if not found
        """
        try:
            params = {
                'geonameId': geoname_id,
                'username': self.username,
                'type': 'json'
            }
            
            response = requests.get(
                f'{self.base_url}/getJSON',
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                item = response.json()
                return {
                    'id': item.get('geonameId'),
                    'name': item.get('name'),
                    'country': item.get('countryName'),
                    'country_code': item.get('countryCode'),
                    'state': item.get('adminName1', ''),
                    'lat': float(item.get('lat')),
                    'lon': float(item.get('lng')),
                    'timezone': item.get('timezone', {}).get('timeZoneId', 'UTC'),
                    'display_name': self._format_display_name(item)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching city by ID: {str(e)}")
            return None
    
    def get_timezone_offset(self, lat: float, lon: float) -> float:
        """
        Get timezone offset for given coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Timezone offset in hours (e.g., 5.5 for IST)
        """
        try:
            params = {
                'lat': lat,
                'lng': lon,
                'username': self.username
            }
            
            response = requests.get(
                f'{self.base_url}/timezoneJSON',
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # Raw offset in hours
                return float(data.get('rawOffset', 0))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error fetching timezone: {str(e)}")
            return 0.0

# Fallback: In-memory city database for common Indian cities
# Used when GeoNames API is unavailable or for demo purposes
INDIAN_CITIES_FALLBACK = [
    {'name': 'Mumbai', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.0760, 'lon': 72.8777, 'tz': 5.5},
    {'name': 'Delhi', 'state': 'Delhi', 'country': 'India', 'lat': 28.6139, 'lon': 77.2090, 'tz': 5.5},
    {'name': 'Bangalore', 'state': 'Karnataka', 'country': 'India', 'lat': 12.9716, 'lon': 77.5946, 'tz': 5.5},
    {'name': 'Hyderabad', 'state': 'Telangana', 'country': 'India', 'lat': 17.3850, 'lon': 78.4867, 'tz': 5.5},
    {'name': 'Ahmedabad', 'state': 'Gujarat', 'country': 'India', 'lat': 23.0225, 'lon': 72.5714, 'tz': 5.5},
    {'name': 'Chennai', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 13.0827, 'lon': 80.2707, 'tz': 5.5},
    {'name': 'Kolkata', 'state': 'West Bengal', 'country': 'India', 'lat': 22.5726, 'lon': 88.3639, 'tz': 5.5},
    {'name': 'Pune', 'state': 'Maharashtra', 'country': 'India', 'lat': 18.5204, 'lon': 73.8567, 'tz': 5.5},
    {'name': 'Jaipur', 'state': 'Rajasthan', 'country': 'India', 'lat': 26.9124, 'lon': 75.7873, 'tz': 5.5},
    {'name': 'Lucknow', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 26.8467, 'lon': 80.9462, 'tz': 5.5},
]

class FallbackCityService:
    """Fallback city service using in-memory database"""
    
    def search_cities(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search cities in fallback database"""
        query_lower = query.lower()
        
        results = []
        for city in INDIAN_CITIES_FALLBACK:
            if city['name'].lower().startswith(query_lower):
                results.append({
                    'id': f"fallback_{city['name'].lower()}",
                    'name': city['name'],
                    'country': city['country'],
                    'country_code': 'IN',
                    'state': city['state'],
                    'lat': city['lat'],
                    'lon': city['lon'],
                    'timezone': 'Asia/Kolkata',
                    'display_name': f"{city['name']}, {city['state']}, {city['country']}"
                })
                
                if len(results) >= max_results:
                    break
        
        return results
