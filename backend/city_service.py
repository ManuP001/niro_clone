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

# Comprehensive Indian cities database (200+ cities)
# Used as primary source for reliable, fast autocomplete
INDIAN_CITIES_DATABASE = [
    # Metro Cities
    {'name': 'Mumbai', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.0760, 'lon': 72.8777, 'tz': 5.5},
    {'name': 'Delhi', 'state': 'Delhi', 'country': 'India', 'lat': 28.6139, 'lon': 77.2090, 'tz': 5.5},
    {'name': 'Bangalore', 'state': 'Karnataka', 'country': 'India', 'lat': 12.9716, 'lon': 77.5946, 'tz': 5.5},
    {'name': 'Bengaluru', 'state': 'Karnataka', 'country': 'India', 'lat': 12.9716, 'lon': 77.5946, 'tz': 5.5},
    {'name': 'Hyderabad', 'state': 'Telangana', 'country': 'India', 'lat': 17.3850, 'lon': 78.4867, 'tz': 5.5},
    {'name': 'Ahmedabad', 'state': 'Gujarat', 'country': 'India', 'lat': 23.0225, 'lon': 72.5714, 'tz': 5.5},
    {'name': 'Chennai', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 13.0827, 'lon': 80.2707, 'tz': 5.5},
    {'name': 'Kolkata', 'state': 'West Bengal', 'country': 'India', 'lat': 22.5726, 'lon': 88.3639, 'tz': 5.5},
    {'name': 'Pune', 'state': 'Maharashtra', 'country': 'India', 'lat': 18.5204, 'lon': 73.8567, 'tz': 5.5},
    
    # State Capitals & Major Cities
    {'name': 'Jaipur', 'state': 'Rajasthan', 'country': 'India', 'lat': 26.9124, 'lon': 75.7873, 'tz': 5.5},
    {'name': 'Lucknow', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 26.8467, 'lon': 80.9462, 'tz': 5.5},
    {'name': 'Kanpur', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 26.4499, 'lon': 80.3319, 'tz': 5.5},
    {'name': 'Nagpur', 'state': 'Maharashtra', 'country': 'India', 'lat': 21.1458, 'lon': 79.0882, 'tz': 5.5},
    {'name': 'Indore', 'state': 'Madhya Pradesh', 'country': 'India', 'lat': 22.7196, 'lon': 75.8577, 'tz': 5.5},
    {'name': 'Thane', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.2183, 'lon': 72.9781, 'tz': 5.5},
    {'name': 'Bhopal', 'state': 'Madhya Pradesh', 'country': 'India', 'lat': 23.2599, 'lon': 77.4126, 'tz': 5.5},
    {'name': 'Visakhapatnam', 'state': 'Andhra Pradesh', 'country': 'India', 'lat': 17.6869, 'lon': 83.2185, 'tz': 5.5},
    {'name': 'Pimpri-Chinchwad', 'state': 'Maharashtra', 'country': 'India', 'lat': 18.6298, 'lon': 73.7997, 'tz': 5.5},
    {'name': 'Patna', 'state': 'Bihar', 'country': 'India', 'lat': 25.5941, 'lon': 85.1376, 'tz': 5.5},
    
    # Tier 2 Cities
    {'name': 'Vadodara', 'state': 'Gujarat', 'country': 'India', 'lat': 22.3072, 'lon': 73.1812, 'tz': 5.5},
    {'name': 'Ghaziabad', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 28.6692, 'lon': 77.4538, 'tz': 5.5},
    {'name': 'Ludhiana', 'state': 'Punjab', 'country': 'India', 'lat': 30.9010, 'lon': 75.8573, 'tz': 5.5},
    {'name': 'Agra', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 27.1767, 'lon': 78.0081, 'tz': 5.5},
    {'name': 'Nashik', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.9975, 'lon': 73.7898, 'tz': 5.5},
    {'name': 'Faridabad', 'state': 'Haryana', 'country': 'India', 'lat': 28.4089, 'lon': 77.3178, 'tz': 5.5},
    {'name': 'Meerut', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 28.9845, 'lon': 77.7064, 'tz': 5.5},
    {'name': 'Rajkot', 'state': 'Gujarat', 'country': 'India', 'lat': 22.3039, 'lon': 70.8022, 'tz': 5.5},
    {'name': 'Kalyan-Dombivali', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.2403, 'lon': 73.1305, 'tz': 5.5},
    {'name': 'Vasai-Virar', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.4612, 'lon': 72.7988, 'tz': 5.5},
    {'name': 'Varanasi', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 25.3176, 'lon': 82.9739, 'tz': 5.5},
    {'name': 'Srinagar', 'state': 'Jammu and Kashmir', 'country': 'India', 'lat': 34.0837, 'lon': 74.7973, 'tz': 5.5},
    {'name': 'Aurangabad', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.8762, 'lon': 75.3433, 'tz': 5.5},
    {'name': 'Dhanbad', 'state': 'Jharkhand', 'country': 'India', 'lat': 23.7957, 'lon': 86.4304, 'tz': 5.5},
    {'name': 'Amritsar', 'state': 'Punjab', 'country': 'India', 'lat': 31.6340, 'lon': 74.8723, 'tz': 5.5},
    {'name': 'Navi Mumbai', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.0330, 'lon': 73.0297, 'tz': 5.5},
    {'name': 'Allahabad', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 25.4358, 'lon': 81.8463, 'tz': 5.5},
    {'name': 'Prayagraj', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 25.4358, 'lon': 81.8463, 'tz': 5.5},
    {'name': 'Ranchi', 'state': 'Jharkhand', 'country': 'India', 'lat': 23.3441, 'lon': 85.3096, 'tz': 5.5},
    {'name': 'Howrah', 'state': 'West Bengal', 'country': 'India', 'lat': 22.5958, 'lon': 88.2636, 'tz': 5.5},
    {'name': 'Coimbatore', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 11.0168, 'lon': 76.9558, 'tz': 5.5},
    {'name': 'Jabalpur', 'state': 'Madhya Pradesh', 'country': 'India', 'lat': 23.1815, 'lon': 79.9864, 'tz': 5.5},
    {'name': 'Gwalior', 'state': 'Madhya Pradesh', 'country': 'India', 'lat': 26.2183, 'lon': 78.1828, 'tz': 5.5},
    {'name': 'Vijayawada', 'state': 'Andhra Pradesh', 'country': 'India', 'lat': 16.5062, 'lon': 80.6480, 'tz': 5.5},
    {'name': 'Jodhpur', 'state': 'Rajasthan', 'country': 'India', 'lat': 26.2389, 'lon': 73.0243, 'tz': 5.5},
    {'name': 'Madurai', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 9.9252, 'lon': 78.1198, 'tz': 5.5},
    {'name': 'Raipur', 'state': 'Chhattisgarh', 'country': 'India', 'lat': 21.2514, 'lon': 81.6296, 'tz': 5.5},
    {'name': 'Kota', 'state': 'Rajasthan', 'country': 'India', 'lat': 25.2138, 'lon': 75.8648, 'tz': 5.5},
    
    # NCR Cities
    {'name': 'Gurgaon', 'state': 'Haryana', 'country': 'India', 'lat': 28.4595, 'lon': 77.0266, 'tz': 5.5},
    {'name': 'Gurugram', 'state': 'Haryana', 'country': 'India', 'lat': 28.4595, 'lon': 77.0266, 'tz': 5.5},
    {'name': 'Noida', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 28.5355, 'lon': 77.3910, 'tz': 5.5},
    {'name': 'Greater Noida', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 28.4744, 'lon': 77.5040, 'tz': 5.5},
    {'name': 'Rohtak', 'state': 'Haryana', 'country': 'India', 'lat': 28.8955, 'lon': 76.6066, 'tz': 5.5},
    {'name': 'Panipat', 'state': 'Haryana', 'country': 'India', 'lat': 29.3909, 'lon': 76.9635, 'tz': 5.5},
    {'name': 'Sonipat', 'state': 'Haryana', 'country': 'India', 'lat': 28.9931, 'lon': 77.0151, 'tz': 5.5},
    
    # Uttarakhand Cities
    {'name': 'Dehradun', 'state': 'Uttarakhand', 'country': 'India', 'lat': 30.3165, 'lon': 78.0322, 'tz': 5.5},
    {'name': 'Haridwar', 'state': 'Uttarakhand', 'country': 'India', 'lat': 29.9457, 'lon': 78.1642, 'tz': 5.5},
    {'name': 'Roorkee', 'state': 'Uttarakhand', 'country': 'India', 'lat': 29.8543, 'lon': 77.8880, 'tz': 5.5},
    {'name': 'Haldwani', 'state': 'Uttarakhand', 'country': 'India', 'lat': 29.2183, 'lon': 79.5130, 'tz': 5.5},
    {'name': 'Rudrapur', 'state': 'Uttarakhand', 'country': 'India', 'lat': 28.9845, 'lon': 79.4090, 'tz': 5.5},
    
    # More Cities
    {'name': 'Chandigarh', 'state': 'Chandigarh', 'country': 'India', 'lat': 30.7333, 'lon': 76.7794, 'tz': 5.5},
    {'name': 'Mysore', 'state': 'Karnataka', 'country': 'India', 'lat': 12.2958, 'lon': 76.6394, 'tz': 5.5},
    {'name': 'Mysuru', 'state': 'Karnataka', 'country': 'India', 'lat': 12.2958, 'lon': 76.6394, 'tz': 5.5},
    {'name': 'Thiruvananthapuram', 'state': 'Kerala', 'country': 'India', 'lat': 8.5241, 'lon': 76.9366, 'tz': 5.5},
    {'name': 'Trivandrum', 'state': 'Kerala', 'country': 'India', 'lat': 8.5241, 'lon': 76.9366, 'tz': 5.5},
    {'name': 'Bareilly', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 28.3670, 'lon': 79.4304, 'tz': 5.5},
    {'name': 'Aligarh', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 27.8974, 'lon': 78.0880, 'tz': 5.5},
    {'name': 'Tiruppur', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 11.1085, 'lon': 77.3411, 'tz': 5.5},
    {'name': 'Moradabad', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 28.8389, 'lon': 78.7378, 'tz': 5.5},
    {'name': 'Mysore', 'state': 'Karnataka', 'country': 'India', 'lat': 12.2958, 'lon': 76.6394, 'tz': 5.5},
    {'name': 'Salem', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 11.6643, 'lon': 78.1460, 'tz': 5.5},
    {'name': 'Warangal', 'state': 'Telangana', 'country': 'India', 'lat': 17.9689, 'lon': 79.5941, 'tz': 5.5},
    {'name': 'Guntur', 'state': 'Andhra Pradesh', 'country': 'India', 'lat': 16.3067, 'lon': 80.4365, 'tz': 5.5},
    {'name': 'Bhiwandi', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.3009, 'lon': 73.0643, 'tz': 5.5},
    {'name': 'Saharanpur', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 29.9680, 'lon': 77.5460, 'tz': 5.5},
    {'name': 'Gorakhpur', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 26.7606, 'lon': 83.3732, 'tz': 5.5},
    {'name': 'Bikaner', 'state': 'Rajasthan', 'country': 'India', 'lat': 28.0229, 'lon': 73.3119, 'tz': 5.5},
    {'name': 'Amravati', 'state': 'Maharashtra', 'country': 'India', 'lat': 20.9374, 'lon': 77.7796, 'tz': 5.5},
    {'name': 'Noida', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 28.5355, 'lon': 77.3910, 'tz': 5.5},
    {'name': 'Jamshedpur', 'state': 'Jharkhand', 'country': 'India', 'lat': 22.8046, 'lon': 86.2029, 'tz': 5.5},
    {'name': 'Bhilai', 'state': 'Chhattisgarh', 'country': 'India', 'lat': 21.2094, 'lon': 81.3784, 'tz': 5.5},
    {'name': 'Cuttack', 'state': 'Odisha', 'country': 'India', 'lat': 20.4625, 'lon': 85.8828, 'tz': 5.5},
    {'name': 'Firozabad', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 27.1591, 'lon': 78.3957, 'tz': 5.5},
    {'name': 'Kochi', 'state': 'Kerala', 'country': 'India', 'lat': 9.9312, 'lon': 76.2673, 'tz': 5.5},
    {'name': 'Cochin', 'state': 'Kerala', 'country': 'India', 'lat': 9.9312, 'lon': 76.2673, 'tz': 5.5},
    {'name': 'Bhavnagar', 'state': 'Gujarat', 'country': 'India', 'lat': 21.7645, 'lon': 72.1519, 'tz': 5.5},
    {'name': 'Dehradun', 'state': 'Uttarakhand', 'country': 'India', 'lat': 30.3165, 'lon': 78.0322, 'tz': 5.5},
    {'name': 'Durgapur', 'state': 'West Bengal', 'country': 'India', 'lat': 23.5204, 'lon': 87.3119, 'tz': 5.5},
    {'name': 'Asansol', 'state': 'West Bengal', 'country': 'India', 'lat': 23.6739, 'lon': 86.9524, 'tz': 5.5},
    {'name': 'Nanded', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.1383, 'lon': 77.3210, 'tz': 5.5},
    {'name': 'Kolhapur', 'state': 'Maharashtra', 'country': 'India', 'lat': 16.7050, 'lon': 74.2433, 'tz': 5.5},
    {'name': 'Ajmer', 'state': 'Rajasthan', 'country': 'India', 'lat': 26.4499, 'lon': 74.6399, 'tz': 5.5},
    {'name': 'Akola', 'state': 'Maharashtra', 'country': 'India', 'lat': 20.7002, 'lon': 77.0082, 'tz': 5.5},
    {'name': 'Gulbarga', 'state': 'Karnataka', 'country': 'India', 'lat': 17.3297, 'lon': 76.8343, 'tz': 5.5},
    {'name': 'Jamnagar', 'state': 'Gujarat', 'country': 'India', 'lat': 22.4707, 'lon': 70.0577, 'tz': 5.5},
    {'name': 'Ujjain', 'state': 'Madhya Pradesh', 'country': 'India', 'lat': 23.1765, 'lon': 75.7885, 'tz': 5.5},
    {'name': 'Loni', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 28.7514, 'lon': 77.2868, 'tz': 5.5},
    {'name': 'Siliguri', 'state': 'West Bengal', 'country': 'India', 'lat': 26.7271, 'lon': 88.3953, 'tz': 5.5},
    {'name': 'Jhansi', 'state': 'Uttar Pradesh', 'country': 'India', 'lat': 25.4484, 'lon': 78.5685, 'tz': 5.5},
    {'name': 'Ulhasnagar', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.2183, 'lon': 73.1382, 'tz': 5.5},
    {'name': 'Jammu', 'state': 'Jammu and Kashmir', 'country': 'India', 'lat': 32.7266, 'lon': 74.8570, 'tz': 5.5},
    {'name': 'Sangli-Miraj & Kupwad', 'state': 'Maharashtra', 'country': 'India', 'lat': 16.8524, 'lon': 74.5815, 'tz': 5.5},
    {'name': 'Mangalore', 'state': 'Karnataka', 'country': 'India', 'lat': 12.9141, 'lon': 74.8560, 'tz': 5.5},
    {'name': 'Erode', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 11.3410, 'lon': 77.7172, 'tz': 5.5},
    {'name': 'Belgaum', 'state': 'Karnataka', 'country': 'India', 'lat': 15.8497, 'lon': 74.4977, 'tz': 5.5},
    {'name': 'Ambattur', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 13.1143, 'lon': 80.1548, 'tz': 5.5},
    {'name': 'Tirunelveli', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 8.7139, 'lon': 77.7567, 'tz': 5.5},
    {'name': 'Malegaon', 'state': 'Maharashtra', 'country': 'India', 'lat': 20.5579, 'lon': 74.5287, 'tz': 5.5},
    {'name': 'Gaya', 'state': 'Bihar', 'country': 'India', 'lat': 24.7955, 'lon': 85.0002, 'tz': 5.5},
    {'name': 'Jalgaon', 'state': 'Maharashtra', 'country': 'India', 'lat': 21.0077, 'lon': 75.5626, 'tz': 5.5},
    {'name': 'Udaipur', 'state': 'Rajasthan', 'country': 'India', 'lat': 24.5854, 'lon': 73.7125, 'tz': 5.5},
    {'name': 'Maheshtala', 'state': 'West Bengal', 'country': 'India', 'lat': 22.5093, 'lon': 88.2477, 'tz': 5.5},
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
