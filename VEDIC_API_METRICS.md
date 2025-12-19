# VedicAstroAPI v3-json - Complete Metrics Documentation

## Overview
This document lists all available metrics from the VedicAstroAPI v3-json that can be used for the NIRO application.

## API Endpoints Currently Used

### 1. `/extended-horoscope/extended-kundli-details`
**Returns 25+ core astrological attributes:**

```json
{
  "gana": "manushya",                    // Deva/Manushya/Rakshasa
  "yoni": "snake",                       // Animal type
  "vasya": "Chatushpada",               // Control type
  "nadi": "Antya",                      // Pulse
  "varna": "Vaishya",                   // Social class
  "paya": "Silver",                     // Metal affinity
  "paya_by_nakshatra": "Iron",         // Metal by nakshatra
  "tatva": "Prithvi (Earth)",          // Element
  "life_stone": "emerald",             // Gemstone recommendations
  "lucky_stone": "blue sapphire",
  "fortune_stone": "diamond",
  "name_start": "O",                    // Auspicious name starting letter
  "ascendant_sign": "Virgo",           // Lagna/Rising sign
  "ascendant_nakshatra": "Chitra",     // Ascendant nakshatra
  "rasi": "Taurus",                    // Moon sign
  "rasi_lord": "Venus",                // Moon sign ruler
  "nakshatra": "Rohini",               // Birth nakshatra
  "nakshatra_lord": "Moon",            // Nakshatra ruler
  "nakshatra_pada": 3,                 // Quarter (1-4)
  "sun_sign": "Cancer",                // Western sun sign
  "tithi": "K.Trayodasi",             // Lunar day
  "karana": "Vanija",                  // Half of tithi
  "yoga": "Vyaghata",                  // Panchang yoga
  "ayanamsa": 23.73                    // Precession value
}
```

### 2. `/horoscope/planet-details?planet=sun`
**Returns detailed positions for ALL 10 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu, Ascendant):**

For each planet:
```json
{
  "name": "Su",                         // Short code
  "full_name": "Sun",                   // Full name
  "local_degree": 28.39,                // Degree within sign (0-30)
  "global_degree": 118.39,              // Degree in zodiac (0-360)
  "progress_in_percentage": 94.65,      // Progress through sign
  "rasi_no": 4,                         // Sign number (1-12)
  "zodiac": "Cancer",                   // Sign name
  "house": 11,                          // House placement (1-12)
  "speed_radians_per_day": 1.11e-8,    // Daily motion
  "retro": false,                       // Retrograde status
  "nakshatra": "Ashlesha",             // Current nakshatra
  "nakshatra_lord": "Mercury",         // Nakshatra ruler
  "nakshatra_pada": 4,                 // Pada (1-4)
  "nakshatra_no": 9,                   // Nakshatra number (1-27)
  "zodiac_lord": "Moon",               // Sign ruler
  "is_planet_set": false,              // Below horizon?
  "basic_avastha": "Mritya",           // Age state (Bala/Kumara/Yuva/Vriddha/Mritya)
  "lord_status": "Neutral",            // Benefic/Malefic/Yogakaraka/Maraka
  "is_combust": false                  // Combust by Sun?
}
```

**Additional Data in Planet Details Response:**
```json
{
  "birth_dasa": "Moon>Me>Ra",          // Dasha at birth (Maha>Antar>Pratyantar)
  "current_dasa": "Ju>Ke>Ve",          // Current dasha  
  "birth_dasa_time": "08/04/1983",     // When birth dasha started
  "current_dasa_time": "09/12/2025",   // Current dasha timestamp
  
  "lucky_gem": ["pearl"],              // Recommended gemstones
  "lucky_num": [2],                    // Lucky numbers
  "lucky_colors": ["white"],           // Lucky colors
  "lucky_letters": ["O", "V"],        // Lucky alphabet letters
  "lucky_name_start": ["O", "Va", "Vi", "Vu"],  // Name prefixes
  
  "rasi": "Taurus",                    // Moon sign
  "nakshatra": "Rohini",               // Birth nakshatra
  "nakshatra_pada": 3,                 // Pada
  
  "panchang": {
    "ayanamsa": 23.73,
    "ayanamsa_name": "Lahiri",
    "day_of_birth": "Wednesday",
    "day_lord": "Mercury",
    "hora_lord": "Jupiter",
    "sunrise_at_birth": "05:50:59",
    "sunset_at_birth": "20:03:00",
    "karana": "Vanija",
    "yoga": "Vyaghata",
    "tithi": "Dasami"
  },
  
  "ghatka_chakra": {                   // Timing indicator for activities
    "rasi": "Virgo",
    "tithi": ["5", "10", "15"],
    "day": "Saturday",
    "nakshatra": "Hasta",
    "tatva": "Akasha (Sky)",
    "lord": "Jupiter",
    "same_sex_lagna": "Taurus",
    "opposite_sex_lagna": "Scorpio"
  }
}
```

### 3. `/dashas/maha-dasha`
**Returns Vimshottari Mahadasha timeline (120 year cycle):**

```json
{
  "mahadasha": [
    "Moon", "Mars", "Rahu", "Jupiter", 
    "Saturn", "Mercury", "Ketu", "Venus", "Sun"
  ],
  "mahadasha_order": [
    "Wed Dec 15 1993",  // End dates for each mahadasha
    "Fri Dec 15 2000",
    "Sat Dec 15 2018",
    "Fri Dec 15 2034",
    "Mon Dec 15 2053",
    "Mon Dec 15 2070",
    "Wed Dec 15 2077",
    "Sun Dec 15 2097",
    "Sat Dec 15 2103"
  ],
  "start_year": 1983,
  "dasha_start_date": "Thu Dec 15 1983",
  "dasha_remaining_at_birth": "3 years 4 months 0 days"
}
```

### 4. `/extended-horoscope/find-ascendant`
```json
{
  "ascendant": "Virgo",
  "bot_response": "You are a Virgo ascendant",
  "prediction": "Ruled by Mercury, Virgos tend to be perfectionists..."
}
```

### 5. `/extended-horoscope/find-sun-sign`
```json
{
  "sun_sign": "Leo",
  "prediction": "Leos are the royals of the zodiac...",
  "bot_response": "Your sun sign is Leo"
}
```

### 6. `/extended-horoscope/find-moon-sign`
```json
{
  "moon_sign": "Taurus",
  "bot_response": "Your moon sign is Taurus",
  "prediction": "Taurus natives are known for being dependable..."
}
```

---

## Summary of Available Data

### ✅ Currently Integrated (5 endpoints)
1. **Basic Chart Info**: Ascendant, Sun sign, Moon sign
2. **Nakshatra Details**: Birth nakshatra, pada, nakshatra lord
3. **Mahadasha Timeline**: 120-year Vimshottari cycle with current period
4. **Extended Kundli**: 25+ attributes (gana, yoni, nadi, tatva, etc.)
5. **Gemstone Recommendations**: Life stone, lucky stone, fortune stone

### 📊 Total Metrics Available
- **100+ data points** per birth chart
- **10 planets** with full details each (15+ attributes per planet)
- **12 houses** (derived from planetary positions)
- **27 nakshatras** with pada information
- **9 mahadashas** with precise timing
- **5 avastha states** for planetary ages
- **Panchang data**: Tithi, karana, yoga, day lord, hora lord
- **Ghatka Chakra**: Timing indicators
- **Lucky attributes**: Gems, numbers, colors, letters

### ⚠️ Available But Not Yet Integrated
1. **Precise Planetary Degrees**: Exact positions (local & global degrees)
2. **Planetary Speeds**: Radians per day for each planet
3. **Retrograde Status**: For all applicable planets
4. **Combustion Status**: Planets too close to Sun
5. **Avastha (Age)**: Bala/Kumara/Yuva/Vriddha/Mritya for each planet
6. **Lord Status**: Benefic/Malefic/Yogakaraka/Maraka classification
7. **Current Antardasha**: Detailed sub-period information
8. **Panchang Details**: Sunrise/sunset times, hora lord
9. **Ghatka Chakra**: Complete timing system data
10. **House Lords**: Ruler of each house

---

## Integration Status

### Backend Code Location
- **File**: `/app/backend/astro_client/vedic_api.py`
- **Current Implementation**: Fetches data from endpoints 1, 3, 4, 5, 6
- **Data Models**: Properly mapped to `AstroProfile`, `PlanetPosition`, `HouseData`, `DashaInfo` models

### Next Enhancement Opportunity
Add `/horoscope/planet-details` endpoint to get:
- Precise planetary positions with degrees
- Retrograde and combustion status
- Avastha and lord status
- Lucky attributes and current antardasha

This would eliminate all remaining "stub" data and provide 100% real astrological calculations.

---

## Sample Full Response
See `/tmp/api_response.json` for a complete sample response from the planet-details endpoint.

**API Calls Remaining**: Updated in each response
**Authentication**: API key via query parameter
**Rate Limit**: Varies by subscription plan
**Base URL**: `https://api.vedicastroapi.com/v3-json`
