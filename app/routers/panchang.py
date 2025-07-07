"""
Panchang and Muhurat API Router
Provides endpoints for Vedic calendar calculations
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Dict, Any
import pytz

from app.services.panchang_service import PanchangService

router = APIRouter(prefix="/api/panchang", tags=["panchang"])

# Initialize service
panchang_service = PanchangService()

# Request models
class PanchangRequest(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    timezone: Optional[str] = Field("UTC", description="Timezone (e.g., 'America/New_York')")
    ayanamsa: Optional[str] = Field("Lahiri", description="Ayanamsa type")

class MuhuratRequest(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    timezone: Optional[str] = Field("UTC", description="Timezone")

# Response models
class TithiResponse(BaseModel):
    tithi_number: int
    tithi_name: str
    paksha: str
    progress_percent: float
    longitude_diff: float

class NakshatraResponse(BaseModel):
    nakshatra_number: int
    nakshatra_name: str
    pada: int
    progress_percent: float
    longitude: float

class YogaResponse(BaseModel):
    yoga_number: int
    yoga_name: str
    progress_percent: float
    longitude_sum: float

class KaranaResponse(BaseModel):
    karana_number: int
    karana_name: str
    progress_percent: float

class MuhuratResponse(BaseModel):
    rahu_kaal: Dict[str, Any]
    abhijit: Dict[str, Any]

class PanchangResponse(BaseModel):
    date: str
    location: Dict[str, float]
    weekday: str
    ayanamsa: Dict[str, Any]
    tithi: TithiResponse
    nakshatra: NakshatraResponse
    yoga: YogaResponse
    karana: KaranaResponse
    planetary_positions: Dict[str, float]
    muhurats: MuhuratResponse
    timestamp: str

@router.get("/health")
async def health_check():
    """Health check for Panchang service"""
    return {
        "status": "healthy",
        "service": "Panchang & Muhurat Service",
        "features": [
            "Tithi Calculation",
            "Nakshatra Calculation", 
            "Yoga Calculation",
            "Karana Calculation",
            "Rahu Kaal Timing",
            "Abhijit Muhurat",
            "Complete Panchang"
        ],
        "ayanamsa_types": ["Lahiri", "Raman", "KP", "Yukteshwar"]
    }

@router.post("/calculate", response_model=PanchangResponse)
async def calculate_panchang(request: PanchangRequest):
    """
    Calculate complete Panchang for a given date and location
    
    This endpoint calculates:
    - Tithi (Lunar Day)
    - Nakshatra (Constellation)
    - Yoga (Astronomical combination)
    - Karana (Half Tithi)
    - Rahu Kaal timing
    - Abhijit Muhurat
    - Planetary positions
    """
    try:
        # Parse date
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        
        # Handle timezone
        if request.timezone and request.timezone != "UTC":
            try:
                tz = pytz.timezone(request.timezone)
                date_obj = tz.localize(date_obj)
            except pytz.exceptions.UnknownTimeZoneError:
                raise HTTPException(status_code=400, detail=f"Unknown timezone: {request.timezone}")
        else:
            date_obj = date_obj.replace(tzinfo=pytz.UTC)
        
        # Calculate Panchang
        panchang_data = panchang_service.get_panchang(
            date=date_obj,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_type=request.ayanamsa
        )
        
        return panchang_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Panchang: {e}")

@router.post("/tithi")
async def calculate_tithi_only(request: PanchangRequest):
    """Calculate only Tithi for a given date"""
    try:
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        
        if request.timezone and request.timezone != "UTC":
            tz = pytz.timezone(request.timezone)
            date_obj = tz.localize(date_obj)
        else:
            date_obj = date_obj.replace(tzinfo=pytz.UTC)
        
        panchang_data = panchang_service.get_panchang(
            date=date_obj,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_type=request.ayanamsa
        )
        
        return {
            "date": request.date,
            "tithi": panchang_data["tithi"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Tithi: {e}")

@router.post("/nakshatra")
async def calculate_nakshatra_only(request: PanchangRequest):
    """Calculate only Nakshatra for a given date"""
    try:
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        
        if request.timezone and request.timezone != "UTC":
            tz = pytz.timezone(request.timezone)
            date_obj = tz.localize(date_obj)
        else:
            date_obj = date_obj.replace(tzinfo=pytz.UTC)
        
        panchang_data = panchang_service.get_panchang(
            date=date_obj,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_type=request.ayanamsa
        )
        
        return {
            "date": request.date,
            "nakshatra": panchang_data["nakshatra"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Nakshatra: {e}")

@router.post("/muhurats")
async def calculate_muhurats(request: MuhuratRequest):
    """
    Calculate auspicious and inauspicious timings for a date
    
    Returns:
    - Rahu Kaal (inauspicious time)
    - Abhijit Muhurat (most auspicious time)
    - Sunrise and sunset times
    """
    try:
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        
        if request.timezone and request.timezone != "UTC":
            tz = pytz.timezone(request.timezone)
            date_obj = tz.localize(date_obj)
        else:
            date_obj = date_obj.replace(tzinfo=pytz.UTC)
        
        # Calculate muhurats
        rahu_kaal = panchang_service.calculate_rahu_kaal(
            date=date_obj, 
            latitude=request.latitude, 
            longitude=request.longitude
        )
        
        abhijit = panchang_service.calculate_abhijit_muhurat(
            date=date_obj,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        return {
            "date": request.date,
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "muhurats": {
                "rahu_kaal": rahu_kaal,
                "abhijit_muhurat": abhijit
            },
            "recommendations": {
                "avoid_during_rahu_kaal": "Avoid starting new ventures, traveling, or important decisions",
                "use_abhijit_muhurat": "Best time for new beginnings, important meetings, and auspicious activities"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Muhurats: {e}")

@router.get("/today")
async def get_today_panchang(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in degrees"),
    timezone: str = Query("UTC", description="Timezone"),
    ayanamsa: str = Query("Lahiri", description="Ayanamsa type")
):
    """Get today's Panchang for a location"""
    try:
        # Get current date in the specified timezone
        if timezone != "UTC":
            tz = pytz.timezone(timezone)
            current_date = datetime.now(tz).date()
        else:
            current_date = datetime.now(pytz.UTC).date()
        
        # Create request
        request = PanchangRequest(
            date=current_date.strftime("%Y-%m-%d"),
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            ayanamsa=ayanamsa
        )
        
        return await calculate_panchang(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting today's Panchang: {e}")

@router.get("/nakshatras")
async def get_nakshatra_list():
    """Get list of all 27 Nakshatras"""
    return {
        "nakshatras": panchang_service.nakshatras,
        "total_count": len(panchang_service.nakshatras),
        "description": "The 27 Nakshatras (constellations) in Vedic astrology"
    }

@router.get("/tithis")
async def get_tithi_list():
    """Get list of all Tithis"""
    return {
        "tithis": panchang_service.tithis,
        "total_count": len(panchang_service.tithis),
        "description": "The 15 Tithis (lunar days) in each paksha"
    }

@router.get("/yogas")
async def get_yoga_list():
    """Get list of all 27 Yogas"""
    return {
        "yogas": panchang_service.yogas,
        "total_count": len(panchang_service.yogas),
        "description": "The 27 Yogas in Vedic astrology"
    } 