
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.models import (
    BirthChartRequest, BirthChartResponse, DetailedReportRequest, DetailedReportResponse,
    ErrorResponse, HouseSystem, AyanamsaSystem
)
from app.services.birth_chart import birth_chart_service

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/birth-chart", response_model=BirthChartResponse)
async def generate_birth_chart(request: BirthChartRequest):
    """
    Generate a comprehensive Vedic birth chart with planets, houses, and aspects.
    
    This endpoint calculates:
    - Planet positions in zodiac signs and houses (Sidereal/Vedic system)
    - House cusps using specified house system
    - Aspects between planets
    - Chart summary with dominant signs and houses
    
    Uses Vedic (Sidereal) astrology with specified ayanamsa system (default: Lahiri).
    """
    try:
        logger.info(f"Generating Vedic birth chart for {request.birth_date} {request.birth_time}")
        chart = birth_chart_service.generate_birth_chart(request)
        logger.info("Vedic birth chart generated successfully")
        return chart
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while generating birth chart")

@router.post("/detailed-report", response_model=DetailedReportResponse)
async def generate_detailed_report(request: DetailedReportRequest):
    """
    Generate a comprehensive detailed astrological report based on Vedic astrology.
    
    This endpoint provides:
    - Complete birth chart analysis
    - Personality and character analysis
    - Career and purpose insights
    - Love and relationship guidance
    - Health and wellness recommendations
    - Spiritual and karmic analysis
    
    Uses advanced AI-powered interpretations combined with traditional Vedic wisdom.
    """
    try:
        logger.info(f"Generating detailed report for {request.birth_date} {request.birth_time}")
        report = birth_chart_service.generate_detailed_report(request)
        logger.info("Detailed report generated successfully")
        return report
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while generating detailed report")

@router.get("/birth-chart", response_model=BirthChartResponse)
async def get_birth_chart_legacy(
    date: str = Query(..., description="Birth date in YYYY-MM-DD format"),
    time: str = Query(..., description="Birth time in HH:MM format"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude of birth location"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude of birth location"),
    name: Optional[str] = Query(None, description="Name of the person"),
    timezone: Optional[str] = Query(None, description="Timezone (e.g., 'UTC', 'America/New_York')"),
    house_system: HouseSystem = Query(HouseSystem.PLACIDUS, description="House system to use"),
    ayanamsa: AyanamsaSystem = Query(AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
):
    """
    Legacy endpoint for backward compatibility.
    Generate a Vedic birth chart using query parameters.
    
    Uses Vedic (Sidereal) astrology with specified ayanamsa system.
    """
    try:
        request = BirthChartRequest(
            name=name,
            birth_date=date,
            birth_time=time,
            latitude=lat,
            longitude=lon,
            timezone=timezone,
            house_system=house_system,
            ayanamsa=ayanamsa
        )
        
        chart = birth_chart_service.generate_birth_chart(request)
        return chart
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while generating birth chart")

@router.get("/detailed-report", response_model=DetailedReportResponse)
async def get_detailed_report_legacy(
    date: str = Query(..., description="Birth date in YYYY-MM-DD format"),
    time: str = Query(..., description="Birth time in HH:MM format"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude of birth location"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude of birth location"),
    name: Optional[str] = Query(None, description="Name of the person"),
    timezone: Optional[str] = Query(None, description="Timezone (e.g., 'UTC', 'America/New_York')"),
    house_system: HouseSystem = Query(HouseSystem.PLACIDUS, description="House system to use"),
    ayanamsa: AyanamsaSystem = Query(AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
):
    """
    Legacy endpoint for backward compatibility.
    Generate a detailed astrological report using query parameters.
    
    Uses Vedic (Sidereal) astrology with specified ayanamsa system.
    """
    try:
        request = DetailedReportRequest(
            name=name,
            birth_date=date,
            birth_time=time,
            latitude=lat,
            longitude=lon,
            timezone=timezone,
            house_system=house_system,
            ayanamsa=ayanamsa
        )
        
        report = birth_chart_service.generate_detailed_report(request)
        return report
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while generating detailed report")

@router.get("/planets/{planet_name}")
async def get_planet_position(
    planet_name: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query(..., description="Time in HH:MM format"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    timezone: Optional[str] = Query(None, description="Timezone"),
    ayanamsa: AyanamsaSystem = Query(AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
):
    """
    Get position of a specific planet for a given date, time, and location using Vedic astrology.
    """
    try:
        request = BirthChartRequest(
            birth_date=date,
            birth_time=time,
            latitude=lat,
            longitude=lon,
            timezone=timezone,
            ayanamsa=ayanamsa
        )
        
        chart = birth_chart_service.generate_birth_chart(request)
        
        # Find the requested planet
        planet = next((p for p in chart.planets if p.planet.value.lower() == planet_name.lower()), None)
        
        if not planet:
            raise HTTPException(status_code=404, detail=f"Planet '{planet_name}' not found")
        
        return planet
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/houses")
async def get_houses(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query(..., description="Time in HH:MM format"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    timezone: Optional[str] = Query(None, description="Timezone"),
    house_system: HouseSystem = Query(HouseSystem.PLACIDUS, description="House system to use"),
    ayanamsa: AyanamsaSystem = Query(AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
):
    """
    Get house cusps for a given date, time, and location using Vedic astrology.
    """
    try:
        request = BirthChartRequest(
            birth_date=date,
            birth_time=time,
            latitude=lat,
            longitude=lon,
            timezone=timezone,
            house_system=house_system,
            ayanamsa=ayanamsa
        )
        
        chart = birth_chart_service.generate_birth_chart(request)
        return {"houses": chart.houses, "house_system": chart.house_system}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/aspects")
async def get_aspects(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query(..., description="Time in HH:MM format"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    timezone: Optional[str] = Query(None, description="Timezone"),
    ayanamsa: AyanamsaSystem = Query(AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
):
    """
    Get planetary aspects for a given date, time, and location using Vedic astrology.
    """
    try:
        request = BirthChartRequest(
            birth_date=date,
            birth_time=time,
            latitude=lat,
            longitude=lon,
            timezone=timezone,
            ayanamsa=ayanamsa
        )
        
        chart = birth_chart_service.generate_birth_chart(request)
        return {"aspects": chart.aspects}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chart-summary")
async def get_chart_summary(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query(..., description="Time in HH:MM format"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    timezone: Optional[str] = Query(None, description="Timezone"),
    ayanamsa: AyanamsaSystem = Query(AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
):
    """
    Get a summary of the birth chart including dominant signs and houses using Vedic astrology.
    """
    try:
        request = BirthChartRequest(
            birth_date=date,
            birth_time=time,
            latitude=lat,
            longitude=lon,
            timezone=timezone,
            ayanamsa=ayanamsa
        )
        
        chart = birth_chart_service.generate_birth_chart(request)
        return chart.chart_summary
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the astrology service is running.
    """
    return {
        "status": "healthy",
        "service": "Vedic Astrology API",
        "version": "2.0.0",
        "features": [
            "Vedic Birth Charts",
            "Detailed Reports",
            "Planetary Positions",
            "House Calculations",
            "Aspect Analysis",
            "Chart Summaries"
        ]
    }

@router.get("/supported-planets")
async def get_supported_planets():
    """Get list of supported planets."""
    from app.models import Planet
    return {"planets": [planet.value for planet in Planet]}

@router.get("/supported-house-systems")
async def get_supported_house_systems():
    """Get list of supported house systems."""
    from app.models import HouseSystem
    return {"house_systems": [system.value for system in HouseSystem]}

@router.get("/supported-astrology-systems")
async def get_supported_astrology_systems():
    """Get list of supported astrology systems."""
    from app.models import AstrologySystem
    return {"astrology_systems": [system.value for system in AstrologySystem]}

@router.get("/supported-ayanamsa-systems")
async def get_supported_ayanamsa_systems():
    """Get list of supported ayanamsa systems for Sidereal calculations."""
    from app.models import AyanamsaSystem
    return {"ayanamsa_systems": [system.value for system in AyanamsaSystem]}

@router.get("/zodiac-signs")
async def get_zodiac_signs():
    """Get list of zodiac signs."""
    from app.models import ZodiacSign
    return {"signs": [sign.value for sign in ZodiacSign]}
