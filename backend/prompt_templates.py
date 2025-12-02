"""Prompt templates for Astro-Trust Engine"""

# VedicAstroAPI Documentation Context
# This is injected into prompts for code generation

VEDIC_API_DOCS = """
**VedicAstroAPI Documentation**

Base URL: https://api.vedicastroapi.com/v3-json
Authentication: Use 'api_key' parameter in the request

**Available Endpoints:**

1. **Planet Details**
   Endpoint: /horoscope/planet-details
   Method: GET
   Parameters:
   - api_key (required): Your API key
   - dob (required): Date of birth in DD/MM/YYYY format (use forward slashes)
   - tob (required): Time of birth in HH:MM format (24-hour)
   - lat (required): Latitude (decimal)
   - lon (required): Longitude (decimal)
   - tz (required): Timezone offset (e.g., 5.5 for IST)
   - lang (optional): Language (default: 'en')
   
   Response: Returns {"status": 200, "response": {...planetary data...}}
   The response field contains planets, houses, and other astrological data

2. **Dasha Predictions**
   Endpoint: /horoscope/major-vdasha
   Method: GET
   Parameters: Same as planet-details
   Response: Returns Vimshottari dasha periods (Mahadasha, Antardasha, etc.)

3. **Guna Milan (Compatibility)**
   Endpoint: /matching/guna-milan
   Method: GET
   Parameters: Requires birth details for both partners (m_date, m_tob, m_lat, m_lon, f_date, f_tob, f_lat, f_lon)
   Response: Returns compatibility score (0-36) and detailed guna analysis

4. **Mangal Dosha Check**
   Endpoint: /horoscope/mangal-dosha
   Method: GET
   Parameters: Same as planet-details
   Response: Returns mangal dosha status and remedies

5. **Panchang (Daily)**
   Endpoint: /panchang/daily
   Method: GET
   Parameters: date, lat, lon, tz
   Response: Returns tithi, nakshatra, yoga, karana, sunrise, sunset, moonrise, moonset

6. **Transit Predictions**
   Endpoint: /horoscope/major-transit
   Method: GET
   Parameters: Same as planet-details + future_date
   Response: Returns impact of major transits (Saturn, Jupiter) on natal chart

**Error Handling:**
All endpoints return HTTP status codes:
- 200: Success
- 400: Bad request (invalid parameters)
- 401: Unauthorized (invalid API key)
- 500: Internal server error

**Rate Limits:**
- 100 requests per minute
- 5000 requests per day

**Best Practices:**
1. Always validate user input before making API calls
2. Cache responses when possible to reduce API calls
3. Handle errors gracefully and provide fallback options
4. Use proper date/time formatting
"""

def get_report_type_context(report_type: str) -> str:
    """Get specific context and API endpoints needed for each report type"""
    
    contexts = {
        "yearly_prediction": """
**Report Type: Yearly Prediction (The Compass)**

Required API Calls:
1. /horoscope/planet-details - Get current planetary positions and house placements

IMPORTANT: Make only ONE API call to /horoscope/planet-details endpoint. 
This endpoint returns all planetary positions, houses, and aspects needed for analysis.

Focus Areas:
- Month-by-month breakdown based on current planetary positions
- Health predictions (analyze 6th house)
- Family harmony (analyze 4th and 7th houses)
- Financial prospects (analyze 2nd and 11th houses)
- Career outlook (analyze 10th house)
- Major transits impact based on current positions
""",
        
        "love_marriage": """
**Report Type: Love & Marriage Compatibility (The Harmony)**

Required API Calls:
1. /horoscope/planet-details - Analyze 7th house, Venus, and Mars positions

IMPORTANT: Make only ONE API call to /horoscope/planet-details endpoint.
This endpoint returns all planetary positions, houses, and aspects needed for love/marriage analysis.

Focus Areas:
- 7th house lord and placement
- Venus and Mars positions and aspects
- Relationship timing and dynamics
- Compatibility factors from planetary positions
- Marriage prospects and auspicious periods
- Conflict areas and remedies
- Long-term relationship guidance
""",
        
        "career_job": """
**Report Type: Career & Job Success (The Climber)**

Required API Calls:
1. /horoscope/planet-details - Focus on 10th house (career) and planetary positions

IMPORTANT: Make only ONE API call to /horoscope/planet-details endpoint.
This endpoint returns all planetary positions, houses, and aspects needed for career analysis.

Focus Areas:
- 10th house lord and placement
- Saturn's role in career stability
- Jupiter's role in career growth
- Best time windows for job changes based on transits
- Office politics strategy (based on 6th house)
- Entrepreneurship vs. job suitability
- Career obstacles and remedies
"""
    }
    
    return contexts.get(report_type, contexts["yearly_prediction"])

def build_code_generation_prompt(report_type: str, user_data: dict) -> str:
    """Build complete prompt for code generation including API docs and context"""
    report_context = get_report_type_context(report_type)
    
    return f"""{report_context}

{VEDIC_API_DOCS}
"""
