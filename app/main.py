
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import logging

from app.routers import astrology

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="🌟 Starlight Astrology API",
    description="""
## Comprehensive Astrology API for Birth Chart Generation

### 🌟 Features
- **Complete Birth Chart Generation** with planets, houses, and aspects
- **Accurate Astronomical Calculations** using Swiss Ephemeris
- **Multiple House Systems** (Placidus, Koch, Equal, Whole Sign)
- **Planetary Aspects** with orbs and applying/separating analysis
- **Timezone Support** with automatic conversion
- **Chart Analysis** including dominant signs, retrograde planets, and more

### 🪐 Supported Celestial Bodies
- **Traditional Planets**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
- **Modern Planets**: Uranus, Neptune, Pluto
- **Lunar Nodes**: Rahu (North Node), Ketu (South Node)

### 🏠 House Systems
- **Placidus** (most popular, default)
- **Koch** (time-based system)
- **Equal House** (30° houses)
- **Whole Sign** (traditional Hellenistic)

### 🔄 Planetary Aspects
- **Major Aspects**: Conjunction (0°), Opposition (180°), Trine (120°), Square (90°), Sextile (60°)
- **Minor Aspects**: Quincunx (150°), Semisextile (30°), Semisquare (45°), Sesquiquadrate (135°)

### 📊 Chart Analysis
- Dominant signs and houses based on planetary distribution
- Retrograde planet identification
- Sun, Moon, and Ascendant sign determination
- Statistical breakdown of planetary placements

### 🌍 Geographic Support
- Global coordinate support (latitude: -90° to +90°, longitude: -180° to +180°)
- Timezone handling with pytz library
- Automatic UTC conversion for accurate calculations

### 🚀 API Usage
1. Use the primary `POST /api/astrology/birth-chart` endpoint for complete charts
2. Use individual endpoints for specific data (planets, houses, aspects)
3. All responses are JSON formatted and ready for frontend integration
4. Interactive documentation available at `/docs` and `/redoc`

### 📖 Example Usage
```python
import requests

data = {
    "name": "John Doe",
    "birth_date": "1990-01-15",
    "birth_time": "14:30", 
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "house_system": "Placidus"
}

response = requests.post("http://localhost:8000/api/astrology/birth-chart", json=data)
chart = response.json()
```

---
*Built with FastAPI, Swiss Ephemeris, and cosmic precision* ✨
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Starlight Astrology API",
        "url": "https://github.com/your-repo/starlight-astrology",
        "email": "support@starlight-astrology.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.starlight-astrology.com",
            "description": "Production server"
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(astrology.router, prefix="/api/astrology", tags=["🌟 Astrology"])

# Import and include chat router
from app.routers import chat
app.include_router(chat.router, prefix="/api/chat", tags=["💬 Chat"])

# Import and include panchang router
from app.routers import panchang
app.include_router(panchang.router, tags=["📅 Panchang & Muhurats"])

# Import and include profile router
from app.routers import profile
app.include_router(profile.router, prefix="/api/profile", tags=["👤 Profile Management"])

@app.get("/", tags=["📋 Root"], summary="API Information")
async def read_root():
    """
    ## Welcome to Starlight Astrology API! 🌟
    
    Get comprehensive birth chart information including:
    - Planet positions in zodiac signs and houses
    - House cusps with multiple house systems  
    - Planetary aspects with orbs
    - Chart summaries and interpretations
    
    ### Quick Start
    1. **Try it out**: Use the interactive docs at `/docs`
    2. **Generate a chart**: POST to `/api/astrology/birth-chart`
    3. **Get specific data**: Use individual endpoints for planets, houses, aspects
    
    ### Example Request
    ```json
    {
      "name": "Albert Einstein",
      "birth_date": "1879-03-14",
      "birth_time": "11:30",
      "latitude": 48.3969,
      "longitude": 9.9918,
      "timezone": "Europe/Berlin"
    }
    ```
    """
    return {
        "message": "🌟 Welcome to Starlight Astrology API",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        },
        "status": "✅ Active",
        "features": [
            "🪐 Complete planetary positions",
            "🏠 Multiple house systems", 
            "🔄 Planetary aspects",
            "📊 Chart analysis",
            "🌍 Global timezone support",
            "📱 JSON responses",
            "💬 AI-powered astrological chat",
            "🤖 Personalized birth chart consultations",
            "📅 Panchang calculations",
            "🕰️ Muhurat timings",
            "🌙 Tithi & Nakshatra calculations",
            "👤 User profile management",
            "🗄️ Supabase database integration",
            "🔐 Secure user authentication"
        ],
        "endpoints": {
            "birth_chart": "/api/astrology/birth-chart",
            "detailed_report": "/api/astrology/detailed-report",
            "planets": "/api/astrology/planets/{planet_name}",
            "houses": "/api/astrology/houses",
            "aspects": "/api/astrology/aspects",
            "chat": "/api/chat/chat",
            "suggested_questions": "/api/chat/suggested-questions",
            "panchang": "/api/panchang/calculate",
            "today_panchang": "/api/panchang/today",
            "muhurats": "/api/panchang/muhurats",
            "health": "/api/astrology/health",
            "get_profile": "/api/profile/profile/{user_id}",
            "create_profile": "/api/profile/profile",
            "update_profile": "/api/profile/profile/{user_id}",
            "delete_profile": "/api/profile/profile/{user_id}",
            "check_profile_exists": "/api/profile/profile/{user_id}/exists",
            "get_all_profiles": "/api/profile/profiles",
            "profile_health": "/api/profile/health"
        }
    }

@app.get("/health", tags=["📋 Health"], summary="Health Check")
async def health_check():
    """
    ## API Health Check 🏥
    
    Returns the current status of the API service.
    Use this endpoint to verify the API is running and responsive.
    """
    return {
        "status": "✅ Healthy",
        "service": "starlight-astrology-api",
        "version": "1.0.0",
        "uptime": "Active",
        "components": {
            "swiss_ephemeris": "✅ Loaded",
            "astrology_calculations": "✅ Ready",
            "house_systems": "✅ Available",
            "timezone_support": "✅ Active"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error", 
            "detail": "An unexpected error occurred. Please check your request and try again.",
            "type": "server_error"
        }
    )

# Enhanced OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="🌟 Starlight Astrology API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
        contact=app.contact,
        license_info=app.license_info
    )
    
    # Add custom schema enhancements
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        "altText": "Starlight Astrology API"
    }
    
    # Add tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "🌟 Astrology",
            "description": "Birth chart generation and astrological calculations",
            "externalDocs": {
                "description": "Learn more about astrology",
                "url": "https://en.wikipedia.org/wiki/Astrology"
            }
        },
        {
            "name": "💬 Chat",
            "description": "AI-powered astrological consultations and personalized guidance",
            "externalDocs": {
                "description": "Learn about AI astrology",
                "url": "https://openai.com"
            }
        },
        {
            "name": "📋 Root",
            "description": "API information and navigation endpoints"
        },
        {
            "name": "📋 Health", 
            "description": "Service health and status monitoring"
        }
    ]
    
    # Add examples to components
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    openapi_schema["components"]["examples"] = {
        "EinsteinBirthChart": {
            "summary": "Albert Einstein's Birth Chart",
            "description": "Famous physicist's birth data for testing",
            "value": {
                "name": "Albert Einstein",
                "birth_date": "1879-03-14",
                "birth_time": "11:30",
                "latitude": 48.3969,
                "longitude": 9.9918,
                "timezone": "Europe/Berlin",
                "house_system": "Placidus"
            }
        },
        "ModernBirthChart": {
            "summary": "Modern Birth Chart Example",
            "description": "Contemporary birth data example",
            "value": {
                "name": "Jane Doe",
                "birth_date": "1990-07-15",
                "birth_time": "15:30",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "timezone": "America/Los_Angeles",
                "house_system": "Koch"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
