from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import base64

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
    SUN = "SUN"
    MOON = "MOON"
    MERCURY = "MERCURY"
    VENUS = "VENUS"
    MARS = "MARS"
    JUPITER = "JUPITER"
    SATURN = "SATURN"
    URANUS = "URANUS"
    NEPTUNE = "NEPTUNE"
    PLUTO = "PLUTO"
    RAHU = "RAHU"
    KETU = "KETU"
    ASCENDANT = "ASCENDANT"

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
    timezone: Optional[str] = Field(default="Asia/Kolkata", description="Timezone (e.g., 'Asia/Kolkata', 'America/New_York')")
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
    timezone: Optional[str] = Field(default="Asia/Kolkata", description="Timezone (e.g., 'Asia/Kolkata', 'America/New_York')")
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

# Compatibility Matching Models
class CompatibilityLevel(str, Enum):
    EXCELLENT = "Excellent"
    VERY_GOOD = "Very Good"
    GOOD = "Good"
    AVERAGE = "Average"
    BELOW_AVERAGE = "Below Average"
    POOR = "Poor"

class DoshaType(str, Enum):
    NADI = "Nadi"
    MANGLIK = "Manglik"
    BHAKOOT = "Bhakoot"
    GANA = "Gana"

class KootaType(str, Enum):
    VARNA = "Varna"
    VASHYA = "Vashya"
    TARA = "Tara"
    YONI = "Yoni"
    GRAH_MAITRI = "Grah Maitri"
    GANA = "Gana"
    BHAKOOT = "Bhakoot"
    NADI = "Nadi"

class KootaScore(BaseModel):
    koota_type: KootaType
    points_earned: float = Field(..., ge=0, description="Points earned for this koota")
    max_points: float = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Percentage score")
    compatibility_level: CompatibilityLevel
    description: str = Field(..., description="Detailed description of this koota")
    factors: Dict[str, Any] = Field(default_factory=dict, description="Factors considered in calculation")

class DoshaInfo(BaseModel):
    dosha_type: DoshaType
    person1_affected: bool = Field(..., description="Is person 1 affected by this dosha")
    person2_affected: bool = Field(..., description="Is person 2 affected by this dosha")
    severity: str = Field(..., description="Severity level (Low, Medium, High)")
    cancelled: bool = Field(default=False, description="Is the dosha cancelled")
    cancellation_reason: Optional[str] = Field(None, description="Reason for dosha cancellation")
    remedies: List[str] = Field(default_factory=list, description="Suggested remedies")
    description: str = Field(..., description="Detailed description of the dosha")

class CompatibilityMatchRequest(BaseModel):
    # Person 1 details
    person1_name: Optional[str] = Field(None, description="Name of person 1")
    person1_birth_date: str = Field(..., description="Birth date of person 1 in YYYY-MM-DD format")
    person1_birth_time: str = Field(..., description="Birth time of person 1 in HH:MM format")
    person1_latitude: float = Field(..., ge=-90, le=90, description="Latitude of person 1's birth location")
    person1_longitude: float = Field(..., ge=-180, le=180, description="Longitude of person 1's birth location")
    person1_timezone: Optional[str] = Field(None, description="Timezone for person 1")
    
    # Person 2 details
    person2_name: Optional[str] = Field(None, description="Name of person 2")
    person2_birth_date: str = Field(..., description="Birth date of person 2 in YYYY-MM-DD format")
    person2_birth_time: str = Field(..., description="Birth time of person 2 in HH:MM format")
    person2_latitude: float = Field(..., ge=-90, le=90, description="Latitude of person 2's birth location")
    person2_longitude: float = Field(..., ge=-180, le=180, description="Longitude of person 2's birth location")
    person2_timezone: Optional[str] = Field(None, description="Timezone for person 2")
    
    # Calculation settings
    house_system: HouseSystem = Field(default=HouseSystem.PLACIDUS, description="House system to use")
    ayanamsa: AyanamsaSystem = Field(default=AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")

class CompatibilityMatchResponse(BaseModel):
    # Basic info
    person1_name: Optional[str] = Field(None, description="Name of person 1")
    person2_name: Optional[str] = Field(None, description="Name of person 2")
    
    # Overall compatibility
    total_points: float = Field(..., description="Total Ashtakoota points (out of 36)")
    total_percentage: float = Field(..., ge=0, le=100, description="Overall compatibility percentage")
    compatibility_level: CompatibilityLevel = Field(..., description="Overall compatibility level")
    
    # Detailed koota scores
    koota_scores: List[KootaScore] = Field(..., description="Individual koota scores")
    
    # Dosha analysis
    doshas: List[DoshaInfo] = Field(..., description="Dosha analysis for both persons")
    
    # Summary and recommendations
    match_summary: str = Field(..., description="Overall compatibility summary")
    recommendations: List[str] = Field(..., description="Recommendations for the couple")
    
    # Birth chart data for reference
    person1_chart: BirthChartResponse = Field(..., description="Person 1's birth chart")
    person2_chart: BirthChartResponse = Field(..., description="Person 2's birth chart")
    
    # Calculation metadata
    calculation_method: str = Field(default="Ashtakoota", description="Matching method used")
    calculated_at: datetime = Field(default_factory=datetime.now, description="Calculation timestamp")

# Chat models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message/question")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of birth location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of birth location")
    timezone: Optional[str] = Field(default="Asia/Kolkata", description="Timezone (e.g., 'Asia/Kolkata', 'America/New_York')")
    house_system: HouseSystem = Field(default=HouseSystem.PLACIDUS, description="House system to use")
    ayanamsa: AyanamsaSystem = Field(default=AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for maintaining context")
    user_name: Optional[str] = Field(None, description="User's name for personalization")

class ChatResponse(BaseModel):
    success: bool = Field(..., description="Whether the chat was successful")
    response: str = Field(..., description="Assistant's response")
    conversation_id: str = Field(..., description="Conversation ID")
    user_message: str = Field(..., description="Original user message")
    timestamp: datetime = Field(..., description="Response timestamp")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    error: Optional[str] = Field(None, description="Error message if failed")

class ConversationHistoryResponse(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    birth_chart_summary: Dict[str, Any] = Field(..., description="Associated birth chart summary")
    user_name: Optional[str] = Field(None, description="User's name")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    message_count: int = Field(..., description="Total number of messages")

class SuggestedQuestionsResponse(BaseModel):
    questions: List[str] = Field(..., description="List of suggested questions")
    birth_chart_summary: Dict[str, Any] = Field(..., description="Birth chart summary used for suggestions")

# Profile models for Supabase integration
class UserProfile(BaseModel):
    id: Optional[str] = Field(None, description="Profile ID")
    user_id: str = Field(..., description="User ID from Supabase Auth")
    name: Optional[str] = Field(None, description="User's full name")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of birth location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of birth location")
    timezone: Optional[str] = Field(default="Asia/Kolkata", description="Timezone (e.g., 'Asia/Kolkata', 'America/New_York')")
    city: Optional[str] = Field(None, description="Birth city")
    state: Optional[str] = Field(None, description="Birth state/province")
    country: Optional[str] = Field(None, description="Birth country")
    created_at: Optional[datetime] = Field(None, description="Profile creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Profile update timestamp")
    
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
            # Try HH:MM format first
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            try:
                # If HH:MM fails, try HH:MM:SS and convert to HH:MM
                dt = datetime.strptime(v, '%H:%M:%S')
                return dt.strftime('%H:%M')
            except ValueError:
                raise ValueError('Birth time must be in HH:MM format')

class ProfileCreateRequest(BaseModel):
    user_id: str = Field(..., description="User ID from Supabase Auth")
    name: Optional[str] = Field(None, description="User's full name")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of birth location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of birth location")
    timezone: Optional[str] = Field(default="Asia/Kolkata", description="Timezone (e.g., 'Asia/Kolkata', 'America/New_York')")
    city: Optional[str] = Field(None, description="Birth city")
    state: Optional[str] = Field(None, description="Birth state/province")
    country: Optional[str] = Field(None, description="Birth country")
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Birth date must be in YYYY-MM-DD format')

    @validator('birth_time')
    def validate_birth_time(cls, v):
        if v is not None:
            try:
                # Try HH:MM format first
                datetime.strptime(v, '%H:%M')
                return v
            except ValueError:
                try:
                    # If HH:MM fails, try HH:MM:SS and convert to HH:MM
                    dt = datetime.strptime(v, '%H:%M:%S')
                    return dt.strftime('%H:%M')
                except ValueError:
                    raise ValueError('Birth time must be in HH:MM format')
        return v

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="User's full name")
    birth_date: Optional[str] = Field(None, description="Birth date in YYYY-MM-DD format")
    birth_time: Optional[str] = Field(None, description="Birth time in HH:MM format")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude of birth location")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude of birth location")
    timezone: Optional[str] = Field(None, description="Timezone (e.g., 'Asia/Kolkata', 'America/New_York')")
    city: Optional[str] = Field(None, description="Birth city")
    state: Optional[str] = Field(None, description="Birth state/province")
    country: Optional[str] = Field(None, description="Birth country")
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Birth date must be in YYYY-MM-DD format')
        return v

    @validator('birth_time')
    def validate_birth_time(cls, v):
        if v is not None:
            try:
                # Try HH:MM format first
                datetime.strptime(v, '%H:%M')
                return v
            except ValueError:
                try:
                    # If HH:MM fails, try HH:MM:SS and convert to HH:MM
                    dt = datetime.strptime(v, '%H:%M:%S')
                    return dt.strftime('%H:%M')
                except ValueError:
                    raise ValueError('Birth time must be in HH:MM format')
        return v

class ProfileResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    profile: Optional[UserProfile] = Field(None, description="User profile data")
    message: Optional[str] = Field(None, description="Success or error message")
    error: Optional[str] = Field(None, description="Error message if failed")

class BirthChartDetails(BaseModel):
    id: Optional[str] = Field(None, description="Chart details ID")
    user_id: str = Field(..., description="User ID from Supabase Auth")
    planet_positions: List[Dict[str, Any]] = Field(..., description="Array of planet positions")
    chart_image: bytes = Field(..., description="Binary data of the birth chart image")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        json_encoders = {
            bytes: lambda v: base64.b64encode(v).decode('utf-8')
        }

class BirthChartWithUserRequest(BirthChartRequest):
    user_id: str = Field(..., description="User ID from Supabase Auth")
    city: Optional[str] = Field(None, description="Birth city")
    state: Optional[str] = Field(None, description="Birth state/province")
    country: Optional[str] = Field(None, description="Birth country")

class BirthChartDetailsResponse(BaseModel):
    """Response model for birth chart details with essential fields"""
    name: Optional[str] = Field(None, description="Name of the person")
    birth_datetime: datetime = Field(..., description="Birth date and time")
    location: Dict[str, float] = Field(..., description="Birth location coordinates")
    planets: List[Dict[str, Any]] = Field(..., description="Array of planet positions")
    chart_summary: Dict[str, Any] = Field(..., description="Chart summary and statistics")
    vedic_chart_svg: Optional[str] = Field(None, description="SVG data for the Vedic chart")

    class Config:
        json_encoders = {
            bytes: lambda v: base64.b64encode(v).decode('utf-8')
        }
