"""
World cities dataset for place of birth autocomplete.
Contains major cities globally with coordinates and timezone info.
"""

WORLD_CITIES = [
    # India - Major cities
    {"label": "Rohtak, Haryana, India", "city": "Rohtak", "region": "Haryana", "country": "India", "lat": 28.8955, "lon": 76.5660, "tz": 5.5},
    {"label": "Delhi, India", "city": "Delhi", "region": "Delhi", "country": "India", "lat": 28.6139, "lon": 77.2090, "tz": 5.5},
    {"label": "Mumbai, Maharashtra, India", "city": "Mumbai", "region": "Maharashtra", "country": "India", "lat": 19.0760, "lon": 72.8777, "tz": 5.5},
    {"label": "Bangalore, Karnataka, India", "city": "Bangalore", "region": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946, "tz": 5.5},
    {"label": "Hyderabad, Telangana, India", "city": "Hyderabad", "region": "Telangana", "country": "India", "lat": 17.3850, "lon": 78.4867, "tz": 5.5},
    {"label": "Chennai, Tamil Nadu, India", "city": "Chennai", "region": "Tamil Nadu", "country": "India", "lat": 13.0827, "lon": 80.2707, "tz": 5.5},
    {"label": "Kolkata, West Bengal, India", "city": "Kolkata", "region": "West Bengal", "country": "India", "lat": 22.5726, "lon": 88.3639, "tz": 5.5},
    {"label": "Pune, Maharashtra, India", "city": "Pune", "region": "Maharashtra", "country": "India", "lat": 18.5204, "lon": 73.8567, "tz": 5.5},
    {"label": "Ahmedabad, Gujarat, India", "city": "Ahmedabad", "region": "Gujarat", "country": "India", "lat": 23.0225, "lon": 72.5714, "tz": 5.5},
    {"label": "Jaipur, Rajasthan, India", "city": "Jaipur", "region": "Rajasthan", "country": "India", "lat": 26.9124, "lon": 75.7873, "tz": 5.5},
    {"label": "Lucknow, Uttar Pradesh, India", "city": "Lucknow", "region": "Uttar Pradesh", "country": "India", "lat": 26.8467, "lon": 80.9462, "tz": 5.5},
    {"label": "Chandigarh, India", "city": "Chandigarh", "region": "Chandigarh", "country": "India", "lat": 30.7333, "lon": 76.7794, "tz": 5.5},
    {"label": "Goa, India", "city": "Goa", "region": "Goa", "country": "India", "lat": 15.2993, "lon": 73.8243, "tz": 5.5},
    
    # USA - Major cities
    {"label": "New York, NY, USA", "city": "New York", "region": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060, "tz": -5.0},
    {"label": "Los Angeles, CA, USA", "city": "Los Angeles", "region": "California", "country": "USA", "lat": 34.0522, "lon": -118.2437, "tz": -8.0},
    {"label": "Chicago, IL, USA", "city": "Chicago", "region": "Illinois", "country": "USA", "lat": 41.8781, "lon": -87.6298, "tz": -6.0},
    {"label": "Houston, TX, USA", "city": "Houston", "region": "Texas", "country": "USA", "lat": 29.7604, "lon": -95.3698, "tz": -6.0},
    {"label": "Phoenix, AZ, USA", "city": "Phoenix", "region": "Arizona", "country": "USA", "lat": 33.4484, "lon": -112.0742, "tz": -7.0},
    {"label": "Philadelphia, PA, USA", "city": "Philadelphia", "region": "Pennsylvania", "country": "USA", "lat": 39.9526, "lon": -75.1652, "tz": -5.0},
    {"label": "San Francisco, CA, USA", "city": "San Francisco", "region": "California", "country": "USA", "lat": 37.7749, "lon": -122.4194, "tz": -8.0},
    {"label": "Boston, MA, USA", "city": "Boston", "region": "Massachusetts", "country": "USA", "lat": 42.3601, "lon": -71.0589, "tz": -5.0},
    {"label": "Seattle, WA, USA", "city": "Seattle", "region": "Washington", "country": "USA", "lat": 47.6062, "lon": -122.3321, "tz": -8.0},
    {"label": "Miami, FL, USA", "city": "Miami", "region": "Florida", "country": "USA", "lat": 25.7617, "lon": -80.1918, "tz": -5.0},
    
    # UK
    {"label": "London, England, UK", "city": "London", "region": "England", "country": "UK", "lat": 51.5074, "lon": -0.1278, "tz": 0.0},
    {"label": "Manchester, England, UK", "city": "Manchester", "region": "England", "country": "UK", "lat": 53.4808, "lon": -2.2426, "tz": 0.0},
    {"label": "Birmingham, England, UK", "city": "Birmingham", "region": "England", "country": "UK", "lat": 52.5086, "lon": -1.8755, "tz": 0.0},
    
    # Canada
    {"label": "Toronto, Ontario, Canada", "city": "Toronto", "region": "Ontario", "country": "Canada", "lat": 43.6532, "lon": -79.3832, "tz": -5.0},
    {"label": "Vancouver, BC, Canada", "city": "Vancouver", "region": "British Columbia", "country": "Canada", "lat": 49.2827, "lon": -123.1207, "tz": -8.0},
    
    # Australia
    {"label": "Sydney, NSW, Australia", "city": "Sydney", "region": "New South Wales", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "tz": 10.0},
    {"label": "Melbourne, Victoria, Australia", "city": "Melbourne", "region": "Victoria", "country": "Australia", "lat": -37.8136, "lon": 144.9631, "tz": 10.0},
    
    # Japan
    {"label": "Tokyo, Japan", "city": "Tokyo", "region": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "tz": 9.0},
    
    # China
    {"label": "Shanghai, China", "city": "Shanghai", "region": "Shanghai", "country": "China", "lat": 31.2304, "lon": 121.4737, "tz": 8.0},
    {"label": "Beijing, China", "city": "Beijing", "region": "Beijing", "country": "China", "lat": 39.9042, "lon": 116.4074, "tz": 8.0},
    
    # Singapore
    {"label": "Singapore", "city": "Singapore", "region": "Singapore", "country": "Singapore", "lat": 1.3521, "lon": 103.8198, "tz": 8.0},
    
    # Dubai
    {"label": "Dubai, UAE", "city": "Dubai", "region": "Dubai", "country": "UAE", "lat": 25.2048, "lon": 55.2708, "tz": 4.0},
    
    # France
    {"label": "Paris, France", "city": "Paris", "region": "Île-de-France", "country": "France", "lat": 48.8566, "lon": 2.3522, "tz": 1.0},
    
    # Germany
    {"label": "Berlin, Germany", "city": "Berlin", "region": "Berlin", "country": "Germany", "lat": 52.5200, "lon": 13.4050, "tz": 1.0},
    
    # Brazil
    {"label": "São Paulo, Brazil", "city": "São Paulo", "region": "São Paulo", "country": "Brazil", "lat": -23.5505, "lon": -46.6333, "tz": -3.0},
]

def search_places(query: str, limit: int = 10) -> list:
    """
    Search for places by name.
    
    Args:
        query: Search query (city name, region, or country)
        limit: Maximum number of results
        
    Returns:
        List of matching places with normalized response format
    """
    if not query or len(query) < 2:
        return []
    
    query_lower = query.lower()
    matches = []
    
    for place in WORLD_CITIES:
        # Check if query matches city, region, or country
        if (query_lower in place["city"].lower() or 
            query_lower in place["region"].lower() or 
            query_lower in place["country"].lower()):
            matches.append({
                "label": place["label"],
                "place_id": place["label"],
                "lat": place["lat"],
                "lon": place["lon"],
                "tz": place["tz"]
            })
    
    # Sort by relevance (exact prefix match first)
    matches.sort(key=lambda x: x["label"].lower().find(query_lower))
    
    return matches[:limit]
