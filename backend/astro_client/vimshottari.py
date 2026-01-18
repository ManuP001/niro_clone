"""
Local Vimshottari Dasha Calculator

Calculates Mahadasha and Antardasha periods from natal Moon's nakshatra.
Used as fallback when Vedic API doesn't return proper dasha dates.

Reference: Traditional Vimshottari Dasha system (120 years cycle)
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Vimshottari Dasha sequence and periods (in years)
# Order: Ketu -> Venus -> Sun -> Moon -> Mars -> Rahu -> Jupiter -> Saturn -> Mercury
DASHA_SEQUENCE = [
    ("Ketu", 7),
    ("Venus", 20),
    ("Sun", 6),
    ("Moon", 10),
    ("Mars", 7),
    ("Rahu", 18),
    ("Jupiter", 16),
    ("Saturn", 19),
    ("Mercury", 17),
]

# Total cycle = 120 years
TOTAL_CYCLE_YEARS = sum(d[1] for d in DASHA_SEQUENCE)  # 120

# Nakshatra to starting Dasha planet mapping
# Each nakshatra's lord determines which Mahadasha the person is born into
NAKSHATRA_LORDS = {
    # Ketu nakshatras
    "Ashwini": "Ketu",
    "Magha": "Ketu",
    "Mula": "Ketu",
    "Moola": "Ketu",  # Alternate spelling
    
    # Venus nakshatras
    "Bharani": "Venus",
    "Purva Phalguni": "Venus",
    "PurvaPhalguni": "Venus",
    "Purva Ashadha": "Venus",
    "PurvaAshadha": "Venus",
    "PoorvaShadha": "Venus",
    
    # Sun nakshatras
    "Krittika": "Sun",
    "Kritika": "Sun",
    "Uttara Phalguni": "Venus",  # Fixed - Sun rules 2nd part
    "UttaraPhalguni": "Sun",
    "Uttara Ashadha": "Sun",
    "UttaraAshadha": "Sun",
    "UttraShadha": "Sun",
    
    # Moon nakshatras
    "Rohini": "Moon",
    "Hasta": "Moon",
    "Shravana": "Moon",
    "Sravana": "Moon",
    
    # Mars nakshatras
    "Mrigashira": "Mars",
    "Mrigasira": "Mars",
    "Chitra": "Mars",
    "Dhanishta": "Mars",
    "Dhanishtha": "Mars",
    
    # Rahu nakshatras
    "Ardra": "Rahu",
    "Swati": "Rahu",
    "Shatabhisha": "Rahu",
    "Satabhisha": "Rahu",
    
    # Jupiter nakshatras
    "Punarvasu": "Jupiter",
    "Vishakha": "Jupiter",
    "Purva Bhadrapada": "Jupiter",
    "PurvaBhadrapada": "Jupiter",
    "PoorvaBhadra": "Jupiter",
    
    # Saturn nakshatras
    "Pushya": "Saturn",
    "Anuradha": "Saturn",
    "Uttara Bhadrapada": "Saturn",
    "UttaraBhadrapada": "Saturn",
    "UttaraBhadra": "Saturn",
    
    # Mercury nakshatras
    "Ashlesha": "Mercury",
    "Jyeshtha": "Mercury",
    "Revati": "Mercury",
}

# Nakshatra order (0-26) for pada calculation
NAKSHATRA_ORDER = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]


def get_nakshatra_lord(nakshatra: str) -> str:
    """Get the ruling planet of a nakshatra."""
    # Try exact match first
    if nakshatra in NAKSHATRA_LORDS:
        return NAKSHATRA_LORDS[nakshatra]
    
    # Try case-insensitive match
    nakshatra_lower = nakshatra.lower().replace(" ", "").replace("_", "")
    for nak, lord in NAKSHATRA_LORDS.items():
        if nak.lower().replace(" ", "").replace("_", "") == nakshatra_lower:
            return lord
    
    # Default to Ketu if unknown
    logger.warning(f"[VIMSHOTTARI] Unknown nakshatra '{nakshatra}', defaulting to Ketu")
    return "Ketu"


def get_dasha_index(planet: str) -> int:
    """Get the index of a planet in the dasha sequence."""
    for i, (p, _) in enumerate(DASHA_SEQUENCE):
        if p == planet:
            return i
    return 0


def calculate_birth_dasha_balance(
    nakshatra: str,
    moon_degree: Optional[float] = None,
    nakshatra_pada: Optional[int] = None
) -> Tuple[str, float]:
    """
    Calculate the starting Mahadasha and remaining years at birth.
    
    Args:
        nakshatra: Moon's nakshatra at birth
        moon_degree: Moon's degree within the nakshatra (0-13.33°)
        nakshatra_pada: Pada (quarter) 1-4 of the nakshatra
        
    Returns:
        (planet, remaining_years) - The Mahadasha planet and years remaining at birth
    """
    lord = get_nakshatra_lord(nakshatra)
    total_years = next((y for p, y in DASHA_SEQUENCE if p == lord), 10)
    
    # Calculate proportion elapsed based on pada or degree
    if moon_degree is not None and 0 <= moon_degree <= 13.33:
        # Each nakshatra spans ~13.33 degrees
        proportion_elapsed = moon_degree / 13.33
    elif nakshatra_pada and 1 <= nakshatra_pada <= 4:
        # Each pada is 1/4 of the nakshatra
        # Pada 1 = 0-25% elapsed, Pada 2 = 25-50%, etc.
        proportion_elapsed = (nakshatra_pada - 0.5) / 4  # Center of pada
    else:
        # Default to middle of dasha period
        proportion_elapsed = 0.5
    
    remaining_years = total_years * (1 - proportion_elapsed)
    
    logger.debug(f"[VIMSHOTTARI] Birth dasha: {lord} with {remaining_years:.2f} years remaining")
    return lord, remaining_years


def calculate_dasha_timeline(
    dob: date,
    moon_nakshatra: str,
    moon_degree: Optional[float] = None,
    nakshatra_pada: Optional[int] = None
) -> List[Dict]:
    """
    Calculate full Vimshottari Mahadasha timeline from birth.
    
    Returns list of dasha periods with start/end dates.
    """
    # Get starting dasha and balance
    start_planet, balance_years = calculate_birth_dasha_balance(
        moon_nakshatra, moon_degree, nakshatra_pada
    )
    
    start_idx = get_dasha_index(start_planet)
    timeline = []
    current_date = dob
    
    # First period (partial)
    first_end = current_date + timedelta(days=int(balance_years * 365.25))
    timeline.append({
        "planet": start_planet,
        "start_date": current_date,
        "end_date": first_end,
        "years_total": next((y for p, y in DASHA_SEQUENCE if p == start_planet), 10),
        "years_elapsed": next((y for p, y in DASHA_SEQUENCE if p == start_planet), 10) - balance_years,
        "years_remaining": balance_years
    })
    current_date = first_end
    
    # Subsequent full periods (at least 2 cycles = 240 years)
    for cycle in range(3):  # 3 cycles to ensure we cover 150+ years from birth
        for i in range(9):  # 9 dashas in sequence
            idx = (start_idx + 1 + i) % 9
            if cycle == 0 and i == 8:
                # Skip first occurrence of start_planet (already added as partial)
                continue
            
            planet, years = DASHA_SEQUENCE[idx]
            
            # Skip if this is the partial dasha we already added
            if cycle == 0 and planet == start_planet and i < 8:
                continue
                
            end_date = current_date + timedelta(days=int(years * 365.25))
            
            # Only add if end date is in reasonable range
            if end_date.year <= dob.year + 150:
                timeline.append({
                    "planet": planet,
                    "start_date": current_date,
                    "end_date": end_date,
                    "years_total": years,
                    "years_elapsed": 0,
                    "years_remaining": years
                })
            current_date = end_date
    
    return timeline


def calculate_antardasha_timeline(
    mahadasha_planet: str,
    maha_start: date,
    maha_end: date
) -> List[Dict]:
    """
    Calculate Antardasha (Bhukti) periods within a Mahadasha.
    
    Antardashas follow the same sequence starting from the Mahadasha lord.
    Each Antardasha's duration is proportional to both planets' dasha years.
    """
    maha_years = next((y for p, y in DASHA_SEQUENCE if p == mahadasha_planet), 10)
    start_idx = get_dasha_index(mahadasha_planet)
    
    antardashas = []
    current_date = maha_start
    
    for i in range(9):
        idx = (start_idx + i) % 9
        antar_planet, antar_years = DASHA_SEQUENCE[idx]
        
        # Antardasha duration = (maha_years * antar_years) / 120 years
        antar_duration_years = (maha_years * antar_years) / TOTAL_CYCLE_YEARS
        antar_end = current_date + timedelta(days=int(antar_duration_years * 365.25))
        
        # Don't exceed mahadasha end
        if antar_end > maha_end:
            antar_end = maha_end
        
        antardashas.append({
            "planet": antar_planet,
            "start_date": current_date,
            "end_date": antar_end,
            "years_total": antar_duration_years,
            "years_elapsed": 0,
            "years_remaining": antar_duration_years,
            "is_current": False
        })
        
        current_date = antar_end
        if current_date >= maha_end:
            break
    
    return antardashas


def get_current_dasha_periods(
    dob: date,
    moon_nakshatra: str,
    target_date: Optional[date] = None,
    moon_degree: Optional[float] = None,
    nakshatra_pada: Optional[int] = None
) -> Dict:
    """
    Get current Mahadasha and Antardasha for a given date.
    
    Args:
        dob: Date of birth
        moon_nakshatra: Moon's nakshatra at birth
        target_date: Date to check (default: today)
        moon_degree: Moon's degree in nakshatra (optional, for precision)
        nakshatra_pada: Nakshatra pada 1-4 (optional, for precision)
        
    Returns:
        {
            "current_mahadasha": {...},
            "current_antardasha": {...},
            "mahadasha_timeline": [...]
        }
    """
    if target_date is None:
        target_date = date.today()
    
    # Calculate full timeline
    timeline = calculate_dasha_timeline(dob, moon_nakshatra, moon_degree, nakshatra_pada)
    
    # Find current Mahadasha
    current_maha = None
    for period in timeline:
        if period["start_date"] <= target_date <= period["end_date"]:
            current_maha = period
            break
    
    if not current_maha:
        # Fallback: use last period in timeline
        current_maha = timeline[-1] if timeline else {
            "planet": "Jupiter",
            "start_date": dob,
            "end_date": dob + timedelta(days=16*365),
            "years_total": 16,
            "years_elapsed": 0,
            "years_remaining": 16
        }
    
    # Update elapsed/remaining for current date
    days_elapsed = (target_date - current_maha["start_date"]).days
    total_days = (current_maha["end_date"] - current_maha["start_date"]).days
    years_elapsed = days_elapsed / 365.25
    years_remaining = max(0, current_maha["years_total"] - years_elapsed)
    
    current_maha = {
        **current_maha,
        "years_elapsed": round(years_elapsed, 2),
        "years_remaining": round(years_remaining, 2)
    }
    
    # Calculate Antardashas for current Mahadasha
    antardashas = calculate_antardasha_timeline(
        current_maha["planet"],
        current_maha["start_date"],
        current_maha["end_date"]
    )
    
    # Find current Antardasha
    current_antar = None
    for antar in antardashas:
        if antar["start_date"] <= target_date <= antar["end_date"]:
            antar["is_current"] = True
            current_antar = antar
            break
    
    if not current_antar and antardashas:
        current_antar = antardashas[0]
        current_antar["is_current"] = True
    
    # Update antardasha elapsed/remaining
    if current_antar:
        antar_days_elapsed = (target_date - current_antar["start_date"]).days
        antar_years_elapsed = antar_days_elapsed / 365.25
        current_antar["years_elapsed"] = round(antar_years_elapsed, 2)
        current_antar["years_remaining"] = round(
            max(0, current_antar["years_total"] - antar_years_elapsed), 2
        )
    
    logger.info(
        f"[VIMSHOTTARI] DOB={dob}, nakshatra={moon_nakshatra} → "
        f"Mahadasha={current_maha['planet']} ({current_maha['start_date']} to {current_maha['end_date']}), "
        f"Antardasha={current_antar['planet'] if current_antar else 'N/A'}"
    )
    
    return {
        "current_mahadasha": current_maha,
        "current_antardasha": current_antar,
        "antardashas": antardashas,
        "mahadasha_timeline": timeline[:12]  # Return first 12 periods (~120 years)
    }


# Convenience function for integration
def calculate_vimshottari_dashas(
    dob: date,
    moon_nakshatra: str,
    moon_degree: Optional[float] = None,
    nakshatra_pada: Optional[int] = None
) -> Dict:
    """
    Main entry point for Vimshottari Dasha calculation.
    
    Args:
        dob: Date of birth
        moon_nakshatra: Moon's birth nakshatra
        moon_degree: Moon's degree within nakshatra (optional)
        nakshatra_pada: Pada 1-4 (optional)
        
    Returns:
        Dict with current_mahadasha, current_antardasha, mahadasha_timeline
    """
    return get_current_dasha_periods(
        dob=dob,
        moon_nakshatra=moon_nakshatra,
        target_date=date.today(),
        moon_degree=moon_degree,
        nakshatra_pada=nakshatra_pada
    )
