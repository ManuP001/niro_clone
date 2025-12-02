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
   - date (required): Date in DD-MM-YYYY format
   - tob (required): Time of birth in HH:MM format (24-hour)
   - lat (required): Latitude (decimal)
   - lon (required): Longitude (decimal)
   - tz (required): Timezone offset (e.g., 5.5 for IST)
   - lang (optional): Language (default: 'en')
   
   Response: Returns planetary positions, house placements, and aspects
   Example response:
   {
     "planets": [
       {"name": "Sun", "sign": "Aries", "degree": 15.23, "house": 1},
       {"name": "Moon", "sign": "Taurus", "degree": 22.45, "house": 2}
     ],
     "houses": [...],
     "aspects": [...]
   }

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
1. /horoscope/planet-details - Get current planetary positions
2. /horoscope/major-vdasha - Get dasha periods for the year
3. /horoscope/major-transit - Get Saturn and Jupiter transits for next 12 months
4. /panchang/daily - Get important dates for each month

Focus Areas:
- Month-by-month breakdown of events
- Health predictions (focus on 6th house)
- Family harmony (focus on 4th and 7th houses)
- Financial prospects (focus on 2nd and 11th houses)
- Career changes (focus on 10th house)
- Major transits impact
""",
        
        "love_marriage": """
**Report Type: Love & Marriage Compatibility (The Harmony)**

Required API Calls:
1. /matching/guna-milan - Get compatibility score (both partners' details needed)
2. /horoscope/mangal-dosha - Check mangal dosha for both
3. /horoscope/planet-details - Analyze 7th house for both partners
4. /horoscope/vimshottari-dasha - Find marriage timing

Focus Areas:
- Guna Milan score and interpretation
- 7th house lord and placement
- Venus and Mars positions
- Mangal dosha presence and remedies
- Relationship dynamics and conflict areas
- Auspicious marriage dates
- Long-term compatibility factors
""",
        
        "career_job": """
**Report Type: Career & Job Success (The Climber)**

Required API Calls:
1. /horoscope/planet-details - Focus on 10th house (career)
2. /horoscope/vimshottari-dasha - Current dasha impact on career
3. /horoscope/major-transit - Jupiter and Saturn influence on 10th house
4. /panchang/daily - Find auspicious dates for interviews/job changes

Focus Areas:
- 10th house lord and placement
- Saturn's role in career stability
- Jupiter's role in career growth
- Current dasha period's career impact
- Best time windows for job changes
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
