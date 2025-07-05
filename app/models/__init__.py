from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class ZodiacSign(str, Enum):
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

class Planet(str, Enum):
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"
    URANUS = "Uranus"
    NEPTUNE = "Neptune"
    PLUTO = "Pluto"
    RAHU = "Rahu"
    KETU = "Ketu"

class HouseSystem(str, Enum):
    PLACIDUS = "Placidus"
    KOCH = "Koch"
    EQUAL = "Equal"
    WHOLE_SIGN = "Whole Sign"

class AstrologySystem(str, Enum):
    TROPICAL = "Tropical"
    SIDEREAL = "Sidereal"

class AyanamsaSystem(str, Enum):
    LAHIRI = "Lahiri"
    RAMAN = "Raman"
    KRISHNAMURTI = "Krishnamurti"
    DJWHAL_KHUL = "Djwhal Khul"
    YUKTESHWAR = "Yukteshwar"
    JN_BHASIN = "J.N. Bhasin"
    BABYLONIAN_KUGLER1 = "Babylonian/Kugler 1"
    BABYLONIAN_KUGLER2 = "Babylonian/Kugler 2"
    BABYLONIAN_KUGLER3 = "Babylonian/Kugler 3"
    BABYLONIAN_HUBER = "Babylonian/Huber"
    BABYLONIAN_MERCIER = "Babylonian/Mercier"
    ALDEBARAN_15TAU = "Aldebaran at 15 Tau"
    HIPPARCHOS = "Hipparchos"
    SASSANIAN = "Sassanian"
    GALCENT_0SAG = "Galactic Center in 0 Sag"
    J2000 = "J2000"
    J1900 = "J1900"
    B1950 = "B1950"

class PlanetPosition(BaseModel):
    planet: Planet
    longitude: float = Field(..., ge=0, le=360, description="Longitude in degrees")
    latitude: float = Field(..., description="Latitude in degrees")
    distance: float = Field(..., description="Distance from Earth")
    speed: float = Field(..., description="Speed in degrees per day")
    sign: ZodiacSign
    degree: float = Field(..., ge=0, lt=30, description="Degree within sign")
    house: int = Field(..., ge=1, le=12, description="House number")
    retrograde: bool = Field(default=False, description="Is the planet retrograde")

class House(BaseModel):
    number: int = Field(..., ge=1, le=12)
    cusp: float = Field(..., ge=0, le=360, description="House cusp in degrees")
    sign: ZodiacSign
    ruler: Planet

class Aspect(BaseModel):
    planet1: Planet
    planet2: Planet
    aspect_type: str = Field(..., description="Type of aspect (conjunction, opposition, etc.)")
    angle: float = Field(..., description="Exact angle between planets")
    orb: float = Field(..., description="Orb (difference from exact aspect)")
    applying: bool = Field(..., description="Is the aspect applying or separating")

class BirthChartRequest(BaseModel):
    name: Optional[str] = Field(None, description="Name of the person")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of birth location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of birth location")
    timezone: Optional[str] = Field(None, description="Timezone (e.g., 'UTC', 'America/New_York')")
    house_system: HouseSystem = Field(default=HouseSystem.PLACIDUS, description="House system to use")
    ayanamsa: AyanamsaSystem = Field(default=AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")

    @validator('birth_date')
    def validate_birth_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Birth date must be in YYYY-MM-DD format')

    @validator('birth_time')
    def validate_birth_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Birth time must be in HH:MM format')

class BirthChartResponse(BaseModel):
    name: Optional[str] = Field(None, description="Name of the person")
    birth_datetime: datetime = Field(..., description="Birth date and time")
    location: Dict[str, float] = Field(..., description="Birth location coordinates")
    julian_day: float = Field(..., description="Julian day number")
    house_system: HouseSystem = Field(..., description="House system used")
    ayanamsa: AyanamsaSystem = Field(..., description="Ayanamsa system used")
    ayanamsa_value: float = Field(..., description="Ayanamsa value in degrees")
    planets: List[PlanetPosition] = Field(..., description="Planetary positions")
    houses: List[House] = Field(..., description="House cusps and information")
    aspects: List[Aspect] = Field(..., description="Planetary aspects")
    chart_summary: Dict[str, Any] = Field(..., description="Chart summary and statistics")

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

# New model for detailed report request
class DetailedReportRequest(BaseModel):
    name: Optional[str] = Field(None, description="Name of the person")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of birth location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of birth location")
    timezone: Optional[str] = Field(None, description="Timezone (e.g., 'UTC', 'America/New_York')")
    house_system: HouseSystem = Field(default=HouseSystem.PLACIDUS, description="House system to use")
    ayanamsa: AyanamsaSystem = Field(default=AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")

class DetailedReportResponse(BaseModel):
    name: Optional[str] = Field(None, description="Name of the person")
    birth_chart: BirthChartResponse = Field(..., description="Complete birth chart data")
    personality_report: Dict[str, Any] = Field(..., description="Personality analysis")
    career_report: Dict[str, Any] = Field(..., description="Career and purpose analysis")
    relationship_report: Dict[str, Any] = Field(..., description="Love and relationships analysis")
    health_report: Dict[str, Any] = Field(..., description="Health and wellness analysis")
    spiritual_report: Dict[str, Any] = Field(..., description="Spiritual and karmic analysis")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")
