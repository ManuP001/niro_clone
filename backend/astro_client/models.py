"""
Astro Client Models

Pydantic models for birth details, astro profiles, and transits.
Designed to be vendor-agnostic - adapt field mappings for real Vedic API later.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from enum import Enum
import uuid


class Planet(str, Enum):
    """Vedic planets (Grahas)"""
    SUN = "Sun"
    MOON = "Moon"
    MARS = "Mars"
    MERCURY = "Mercury"
    JUPITER = "Jupiter"
    VENUS = "Venus"
    SATURN = "Saturn"
    RAHU = "Rahu"
    KETU = "Ketu"


class ZodiacSign(str, Enum):
    """Vedic zodiac signs (Rashis)"""
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"


class BirthDetails(BaseModel):
    """Birth details for astrological calculations"""
    dob: date = Field(..., description="Date of birth (normalized)")
    tob: str = Field(..., description="Time of birth in HH:MM 24h format")
    location: str = Field(..., description="Birth location (City, Country or location ID)")
    latitude: Optional[float] = Field(None, description="Latitude of birth place")
    longitude: Optional[float] = Field(None, description="Longitude of birth place")
    timezone: float = Field(default=5.5, description="Timezone offset from UTC")

    def to_api_format(self) -> Dict[str, Any]:
        """Convert to format expected by Vedic API"""
        return {
            "dob": self.dob.strftime("%d/%m/%Y"),
            "tob": self.tob,
            "lat": self.latitude,
            "lon": self.longitude,
            "tz": self.timezone
        }


class PlanetPosition(BaseModel):
    """Position of a planet in the chart"""
    planet: str
    sign: str
    sign_num: int = Field(ge=1, le=12)
    degree: float = Field(ge=0, lt=30)
    house: int = Field(ge=1, le=12)
    nakshatra: str
    nakshatra_lord: str
    nakshatra_pada: int = Field(ge=1, le=4)
    is_retrograde: bool = False
    is_combust: bool = False
    is_exalted: bool = False
    is_debilitated: bool = False
    dignity: Optional[str] = None  # own, friendly, neutral, enemy, exalted, debilitated
    strength_score: float = Field(default=0.5, ge=0, le=1)


class HouseData(BaseModel):
    """Data for a house (Bhava)"""
    house_num: int = Field(ge=1, le=12)
    sign: str
    sign_lord: str
    planets: List[str] = Field(default_factory=list)
    aspects_from: List[str] = Field(default_factory=list)  # Planets aspecting this house


class DashaInfo(BaseModel):
    """Mahadasha/Antardasha information"""
    level: str  # "mahadasha", "antardasha", "pratyantardasha"
    planet: str
    start_date: date
    end_date: date
    years_total: float
    years_elapsed: float
    years_remaining: float
    sub_periods: List['DashaInfo'] = Field(default_factory=list)


class YogaInfo(BaseModel):
    """Yoga combination in the chart"""
    name: str
    category: str  # "raja", "dhana", "arishta", "sannyasa", etc.
    planets_involved: List[str]
    houses_involved: List[int]
    strength: str  # "strong", "medium", "weak"
    effects: str
    is_active: bool = True


class TransitEvent(BaseModel):
    """A transit event"""
    event_type: str  # "ingress", "retrograde_start", "retrograde_end", "aspect", "conjunction"
    planet: str
    from_sign: Optional[str] = None
    to_sign: Optional[str] = None
    affected_house: Optional[int] = None
    aspect_to: Optional[str] = None  # planet or house being aspected
    start_date: date
    end_date: Optional[date] = None
    strength: str = "medium"  # "strong", "medium", "weak"
    nature: str = "neutral"  # "benefic", "malefic", "neutral"
    description: str = ""


class AstroProfile(BaseModel):
    """
    Complete astrological profile for a user.
    Built ONCE from Vedic API and stored for reuse.
    """
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    birth_details: BirthDetails
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Raw vendor blob (store for debugging/future use)
    base_chart_raw: Dict[str, Any] = Field(default_factory=dict)
    dashas_raw: Dict[str, Any] = Field(default_factory=dict)

    # Parsed chart data
    ascendant: str = ""  # Lagna sign
    ascendant_degree: float = 0.0
    ascendant_nakshatra: str = ""
    moon_sign: str = ""
    moon_nakshatra: str = ""
    sun_sign: str = ""

    # Detailed positions
    planets: List[PlanetPosition] = Field(default_factory=list)
    houses: List[HouseData] = Field(default_factory=list)

    # Dasha timeline
    current_mahadasha: Optional[DashaInfo] = None
    current_antardasha: Optional[DashaInfo] = None
    dasha_timeline: List[DashaInfo] = Field(default_factory=list)

    # Yogas and strengths
    yogas: List[YogaInfo] = Field(default_factory=list)
    planetary_strengths: List[Dict[str, Any]] = Field(default_factory=list)

    # Divisional charts (for advanced analysis)
    navamsa: Dict[str, Any] = Field(default_factory=dict)  # D9
    dasamsa: Dict[str, Any] = Field(default_factory=dict)  # D10

    def get_planet(self, planet_name: str) -> Optional[PlanetPosition]:
        """Get planet position by name"""
        for p in self.planets:
            if p.planet.lower() == planet_name.lower():
                return p
        return None

    def get_house(self, house_num: int) -> Optional[HouseData]:
        """Get house data by number"""
        for h in self.houses:
            if h.house_num == house_num:
                return h
        return None

    def get_house_lord(self, house_num: int) -> Optional[str]:
        """Get the lord of a house"""
        house = self.get_house(house_num)
        return house.sign_lord if house else None

    def get_planets_in_house(self, house_num: int) -> List[str]:
        """Get all planets in a house"""
        house = self.get_house(house_num)
        return house.planets if house else []


class AstroTransits(BaseModel):
    """
    Transit data for a time window.
    Refreshed periodically (e.g., every 24 hours).
    """
    user_id: str
    from_date: date
    to_date: date
    computed_at: datetime = Field(default_factory=datetime.utcnow)

    # Raw vendor blob
    transits_raw: Dict[str, Any] = Field(default_factory=dict)

    # Parsed transit events
    events: List[TransitEvent] = Field(default_factory=list)

    # Current planetary positions (as of computed_at)
    current_positions: List[Dict[str, Any]] = Field(default_factory=list)

    # Significant upcoming dates
    key_dates: List[Dict[str, Any]] = Field(default_factory=list)

    def get_events_for_house(self, house_num: int) -> List[TransitEvent]:
        """Get transit events affecting a specific house"""
        return [e for e in self.events if e.affected_house == house_num]

    def get_events_for_planet(self, planet: str) -> List[TransitEvent]:
        """Get transit events involving a specific planet"""
        return [e for e in self.events if e.planet.lower() == planet.lower()]

    def get_events_in_range(self, start: date, end: date) -> List[TransitEvent]:
        """Get transit events within a date range"""
        return [
            e for e in self.events
            if e.start_date >= start and (e.end_date is None or e.end_date <= end)
        ]
