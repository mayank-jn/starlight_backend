
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.models import (
    BirthChartRequest, BirthChartResponse, DetailedReportRequest, DetailedReportResponse,
    ErrorResponse, HouseSystem, AyanamsaSystem, CompatibilityMatchRequest, CompatibilityMatchResponse
)
from app.services.birth_chart import birth_chart_service
from app.services.compatibility_service import compatibility_service
from app.services.enhanced_compatibility_service import enhanced_compatibility_service

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

@router.post("/compatibility-match", response_model=CompatibilityMatchResponse)
async def calculate_compatibility_match(request: CompatibilityMatchRequest):
    """
    Calculate comprehensive Vedic astrology compatibility match using the traditional Ashtakoota system.
    
    This endpoint provides:
    - Complete 8-koota (Ashtakoota) analysis with individual scores
    - Dosha analysis (Manglik, Nadi, Bhakoot, Gana)
    - Overall compatibility score out of 36 points
    - Personalized recommendations and remedies
    - Detailed birth charts for both individuals
    
    The Ashtakoota system analyzes:
    1. Varna (1 point) - Spiritual compatibility
    2. Vashya (2 points) - Mutual control/attraction
    3. Tara (3 points) - Health and well-being
    4. Yoni (4 points) - Sexual compatibility
    5. Grah Maitri (5 points) - Friendship of ruling planets
    6. Gana (6 points) - Nature compatibility
    7. Bhakoot (7 points) - Emotional & material prosperity
    8. Nadi (8 points) - Health & progeny
    
    Uses authentic Vedic astrology principles with precise calculations.
    """
    try:
        logger.info(f"Calculating compatibility match between {request.person1_name} and {request.person2_name}")
        result = compatibility_service.calculate_compatibility_match(request)
        logger.info(f"Compatibility match calculated successfully: {result.total_points}/36 points")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error in compatibility calculation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while calculating compatibility match")

@router.get("/compatibility-match", response_model=CompatibilityMatchResponse)
async def get_compatibility_match_legacy(
    # Person 1 details
    person1_name: Optional[str] = Query(None, description="Name of person 1"),
    person1_birth_date: str = Query(..., description="Birth date of person 1 in YYYY-MM-DD format"),
    person1_birth_time: str = Query(..., description="Birth time of person 1 in HH:MM format"),
    person1_latitude: float = Query(..., ge=-90, le=90, description="Latitude of person 1's birth location"),
    person1_longitude: float = Query(..., ge=-180, le=180, description="Longitude of person 1's birth location"),
    person1_timezone: Optional[str] = Query(None, description="Timezone for person 1"),
    
    # Person 2 details
    person2_name: Optional[str] = Query(None, description="Name of person 2"),
    person2_birth_date: str = Query(..., description="Birth date of person 2 in YYYY-MM-DD format"),
    person2_birth_time: str = Query(..., description="Birth time of person 2 in HH:MM format"),
    person2_latitude: float = Query(..., ge=-90, le=90, description="Latitude of person 2's birth location"),
    person2_longitude: float = Query(..., ge=-180, le=180, description="Longitude of person 2's birth location"),
    person2_timezone: Optional[str] = Query(None, description="Timezone for person 2"),
    
    # Calculation settings
    house_system: HouseSystem = Query(HouseSystem.PLACIDUS, description="House system to use"),
    ayanamsa: AyanamsaSystem = Query(AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
):
    """
    Legacy endpoint for backward compatibility.
    Calculate Vedic astrology compatibility match using query parameters.
    
    Uses the traditional Ashtakoota system with all 8 kootas and dosha analysis.
    """
    try:
        request = CompatibilityMatchRequest(
            person1_name=person1_name,
            person1_birth_date=person1_birth_date,
            person1_birth_time=person1_birth_time,
            person1_latitude=person1_latitude,
            person1_longitude=person1_longitude,
            person1_timezone=person1_timezone,
            person2_name=person2_name,
            person2_birth_date=person2_birth_date,
            person2_birth_time=person2_birth_time,
            person2_latitude=person2_latitude,
            person2_longitude=person2_longitude,
            person2_timezone=person2_timezone,
            house_system=house_system,
            ayanamsa=ayanamsa
        )
        
        result = compatibility_service.calculate_compatibility_match(request)
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while calculating compatibility match")

@router.get("/compatibility-info")
async def get_compatibility_info():
    """
    Get information about the Vedic astrology compatibility matching system.
    """
    return {
        "system": "Ashtakoota (8-fold compatibility)",
        "total_points": 36,
        "kootas": [
            {
                "name": "Varna",
                "points": 1,
                "description": "Spiritual compatibility based on caste system"
            },
            {
                "name": "Vashya",
                "points": 2,
                "description": "Mutual control and attraction"
            },
            {
                "name": "Tara",
                "points": 3,
                "description": "Health and well-being compatibility"
            },
            {
                "name": "Yoni",
                "points": 4,
                "description": "Sexual and physical compatibility"
            },
            {
                "name": "Grah Maitri",
                "points": 5,
                "description": "Friendship of ruling planets"
            },
            {
                "name": "Gana",
                "points": 6,
                "description": "Nature and temperament compatibility"
            },
            {
                "name": "Bhakoot",
                "points": 7,
                "description": "Emotional and material prosperity"
            },
            {
                "name": "Nadi",
                "points": 8,
                "description": "Health and progeny compatibility"
            }
        ],
        "interpretation": {
            "30-36": "Excellent match",
            "24-29": "Very good match",
            "18-23": "Good match",
            "12-17": "Average match",
            "6-11": "Below average match",
            "0-5": "Poor match"
        },
        "doshas": [
            {
                "name": "Manglik Dosha",
                "description": "Mars placement in specific houses causing relationship challenges"
            },
            {
                "name": "Nadi Dosha",
                "description": "Same Nadi causing health and progeny issues"
            },
            {
                "name": "Bhakoot Dosha",
                "description": "Specific moon sign combinations causing emotional issues"
            },
            {
                "name": "Gana Dosha",
                "description": "Temperament mismatch causing friction"
            }
        ]
    }

@router.get("/manglik-check")
async def check_manglik_dosha(
    birth_date: str = Query(..., description="Birth date in YYYY-MM-DD format"),
    birth_time: str = Query(..., description="Birth time in HH:MM format"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude of birth location"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude of birth location"),
    timezone: Optional[str] = Query(None, description="Timezone"),
    house_system: HouseSystem = Query(HouseSystem.PLACIDUS, description="House system to use"),
    ayanamsa: AyanamsaSystem = Query(AyanamsaSystem.LAHIRI, description="Ayanamsa system for Vedic calculations")
):
    """
    Check for Manglik Dosha (Mars dosha) in a birth chart.
    
    Manglik Dosha occurs when Mars is placed in 1st, 2nd, 4th, 7th, 8th, or 12th house.
    """
    try:
        request = BirthChartRequest(
            birth_date=birth_date,
            birth_time=birth_time,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            house_system=house_system,
            ayanamsa=ayanamsa
        )
        
        chart = birth_chart_service.generate_birth_chart(request)
        manglik_info = compatibility_service.calculate_manglik_dosha(chart)
        
        return {
            "is_manglik": manglik_info["is_manglik"],
            "mars_house": manglik_info["mars_house"],
            "severity": manglik_info["severity"],
            "description": manglik_info["description"],
            "remedies": [
                "Perform Mangal Shanti Puja",
                "Recite Hanuman Chalisa daily",
                "Wear red coral gemstone (after consultation)",
                "Fast on Tuesdays",
                "Worship Lord Hanuman",
                "Donate red items on Tuesdays"
            ] if manglik_info["is_manglik"] else []
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while checking Manglik dosha")

@router.post("/enhanced-compatibility-match")
async def calculate_enhanced_compatibility_match(request: CompatibilityMatchRequest):
    """
    🌟 WORLD-CLASS Enhanced Vedic Astrology Compatibility Analysis 🌟
    
    This advanced endpoint implements sophisticated Vedic astrology techniques including:
    
    ✨ **Traditional Ashtakoota System** (40% weight)
    - All 8 kootas with precise degree-based calculations
    - Enhanced nakshatra pada analysis
    - Sophisticated animal yoni compatibility
    
    🏠 **Navamsa Chart Analysis** (25% weight)
    - D-9 divisional chart for marriage compatibility
    - Ascendant and 7th house compatibility
    - Venus-Mars positioning analysis
    
    🌌 **Planetary Aspects Synastry** (15% weight)  
    - Venus-Mars attraction analysis
    - Sun-Moon ego-emotion harmony
    - Mercury communication compatibility
    - Jupiter wisdom and growth factors
    
    ⏰ **Dasha Period Compatibility** (10% weight)
    - Current planetary periods analysis
    - Favorable timing for relationship milestones
    - Challenging periods identification
    
    🔮 **Enhanced Dosha Analysis** (10% weight)
    - 10+ dosha types with advanced cancellation rules
    - Severity levels and regional variations
    - Comprehensive remedy recommendations
    
    📊 **Statistical Success Rate Integration**
    - Age difference modifiers
    - Education and background compatibility
    - Historical success rate analysis
    
    **Scoring System:** 100-point weighted system (vs traditional 36-point)
    
    Returns comprehensive analysis with:
    - Detailed compatibility breakdown
    - Timing guidance for relationship milestones
    - Personalized remedies and recommendations
    - Advanced astrological insights
    """
    try:
        logger.info(f"Calculating ENHANCED compatibility match between {request.person1_name} and {request.person2_name}")
        
        # Calculate enhanced compatibility analysis
        result = enhanced_compatibility_service.calculate_enhanced_compatibility_match(request)
        
        logger.info(f"Enhanced compatibility analysis completed: {result['percentage']:.1f}% compatibility")
        
        return JSONResponse(content={
            "status": "success",
            "analysis_type": "enhanced_vedic_compatibility",
            "version": "2.0",
            "person1_name": request.person1_name,
            "person2_name": request.person2_name,
            "final_score": result["final_score"],
            "percentage": result["percentage"],
            "compatibility_level": result["compatibility_level"],
            "traditional_ashtakoota": {
                "score": result["traditional_ashtakoota"],
                "weight": "40%",
                "description": "Traditional 8-fold compatibility system"
            },
            "navamsa_analysis": {
                "score": result["navamsa_analysis"]["navamsa_score"],
                "weight": "25%",
                "description": "D-9 divisional chart for marriage compatibility",
                "details": result["navamsa_analysis"]
            },
            "synastry_analysis": {
                "score": result["synastry_analysis"]["synastry_score"],
                "weight": "15%",
                "description": "Planetary aspects between charts",
                "details": result["synastry_analysis"]
            },
            "dasha_analysis": {
                "score": result["dasha_analysis"]["current_compatibility"],
                "weight": "10%",
                "description": "Current planetary periods compatibility",
                "details": result["dasha_analysis"]
            },
            "dosha_analysis": {
                "weight": "10%",
                "description": "Enhanced dosha system with 10+ types",
                "active_doshas": result["dosha_analysis"],
                "remedies": result["remedies"]
            },
            "comprehensive_recommendations": result["recommendations"],
            "timing_guidance": result["timing_guidance"],
            "advanced_insights": {
                "methodology": "Classical Vedic texts + Modern research",
                "precision": "Degree-based calculations",
                "factors_analyzed": "50+ compatibility factors",
                "success_rate": f"{result['percentage']:.1f}% based on statistical analysis"
            }
        })
    
    except ValueError as e:
        logger.error(f"Validation error in enhanced compatibility: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error in enhanced compatibility calculation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while calculating enhanced compatibility match")
