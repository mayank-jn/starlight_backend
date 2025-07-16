"""
Prokerala API Service for Vedic Astrology Calculations
"""

import os
import base64
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from app.models import (
    BirthChartRequest, BirthChartResponse, PlanetPosition, House, Aspect,
    Planet, ZodiacSign, HouseSystem, AyanamsaSystem
)

# Load environment variables
load_dotenv()

class ProkeralaService:
    """Service for interacting with Prokerala's Astrology API"""
    
    def __init__(self):
        self.client_id = os.getenv("PROKERALA_CLIENT_ID")
        self.client_secret = os.getenv("PROKERALA_CLIENT_SECRET")
        self.debug = True  # Force debug mode on
        self.base_url = "https://api.prokerala.com/v2/astrology"
        self.access_token = None
        
    def _get_access_token(self) -> str:
        """Get OAuth access token from Prokerala"""
        if not self.access_token:
            auth_url = "https://api.prokerala.com/token"
            
            # Create base64 encoded credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}"
            }
            
            if self.debug:
                print("\n=== DEBUG: Token Request ===")
                print(f"Token Request URL: {auth_url}")
                print(f"Token Request Headers:")
                for key, value in headers.items():
                    print(f"  {key}: {value}")
                print("Token Request Data:")
                print(f"  grant_type=client_credentials")
                print("=== END Token Request ===\n")
            
            response = requests.post(auth_url, headers=headers, data={
                "grant_type": "client_credentials"
            })
            
            if self.debug:
                print("\n=== DEBUG: Token Response ===")
                print(f"Response Status: {response.status_code}")
                print(f"Response Headers:")
                for key, value in response.headers.items():
                    print(f"  {key}: {value}")
                print(f"Response Body: {response.text}")
                print("=== END Token Response ===\n")
            
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
        return self.access_token
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to Prokerala API"""
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        if self.debug:
            print("\n=== DEBUG: API Request ===")
            print(f"URL: {url}")
            print("Headers:")
            for key, value in headers.items():
                print(f"  {key}: {value}")
            print("Parameters:")
            for key, value in params.items():
                print(f"  {key}: {value}")
            print("=== END API Request ===\n")
        
        response = requests.get(url, headers=headers, params=params)
        
        if self.debug:
            print("\n=== DEBUG: API Response ===")
            print(f"Full URL: {response.url}")
            print(f"Status Code: {response.status_code}")
            print("Response Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            print(f"Response Body: {response.text}")
            print("=== END API Response ===\n")
        
        # Handle token expiration
        if response.status_code == 401:
            print("Token expired, refreshing...")
            self.access_token = None  # Clear the cached token
            # Retry with fresh token
            headers["Authorization"] = f"Bearer {self._get_access_token()}"
            response = requests.get(url, headers=headers, params=params)
            
            if self.debug:
                print("\n=== DEBUG: Retry API Response ===")
                print(f"Status Code: {response.status_code}")
                print(f"Response Body: {response.text}")
                print("=== END Retry API Response ===\n")
        
        response.raise_for_status()
        return response.json()
    
    def _convert_planet_position(self, planet_data: Dict[str, Any]) -> PlanetPosition:
        """Convert Prokerala planet data to our PlanetPosition model"""
        # Map Vedic rasi names to our zodiac signs
        rasi_map = {
            "Mesha": "ARIES",
            "Vrishabha": "TAURUS",
            "Mithuna": "GEMINI",
            "Karka": "CANCER",
            "Simha": "LEO",
            "Kanya": "VIRGO",
            "Tula": "LIBRA",
            "Vrischika": "SCORPIO",
            "Dhanu": "SAGITTARIUS",
            "Makara": "CAPRICORN",
            "Kumbha": "AQUARIUS",
            "Meena": "PISCES"
        }
        
        # Get rasi (zodiac sign) data
        rasi_data = planet_data.get("rasi", {})
        rasi_name = rasi_data.get("name", "Mesha")
        zodiac_name = rasi_map.get(rasi_name, "ARIES")
        
        # Map planet name using our mapping
        planet_name = planet_data.get("name", "").upper()
        
        if self.debug:
            print(f"Converting planet: {planet_data.get('name')} -> {planet_name}")
            print(f"Converting rasi: {rasi_name} -> {zodiac_name}")
            print(f"Full planet data: {planet_data}")
        
        try:
            return PlanetPosition(
                planet=Planet[planet_name],
                longitude=float(planet_data.get("longitude", 0)),
                latitude=0.0,  # Not provided in API
                distance=0.0,  # Not provided in API
                speed=0.0,  # Not provided in API
                sign=ZodiacSign[zodiac_name],
                degree=float(planet_data.get("degree", 0)),
                house=int(planet_data.get("position", 1)),
                retrograde=planet_data.get("is_retrograde", False)
            )
        except KeyError as e:
            if self.debug:
                print(f"Error converting planet position: {e}")
                print(f"Available Planet enums: {[p.name for p in Planet]}")
                print(f"Available ZodiacSign enums: {[z.name for z in ZodiacSign]}")
            raise ValueError(f"Error mapping planet or zodiac sign: {e}")
    
    def _convert_house(self, house_data: Dict[str, Any]) -> House:
        """Convert Prokerala house data to our House model"""
        return House(
            number=int(house_data["number"]),
            cusp=float(house_data["cusp"]),
            sign=ZodiacSign[house_data["sign"].upper()],
            ruler=Planet[house_data["ruler"].upper()]
        )
    
    def _convert_aspect(self, aspect_data: Dict[str, Any]) -> Aspect:
        """Convert Prokerala aspect data to our Aspect model"""
        return Aspect(
            planet1=Planet[aspect_data["planet1"].upper()],
            planet2=Planet[aspect_data["planet2"].upper()],
            aspect_type=aspect_data["type"],
            angle=float(aspect_data["angle"]),
            orb=float(aspect_data.get("orb", 0)),
            applying=aspect_data.get("applying", False)
        )
    
    async def generate_birth_chart(self, request: BirthChartRequest) -> BirthChartResponse:
        """Generate birth chart using Prokerala API"""
        try:
            # Convert datetime to ISO format with timezone
            birth_datetime = datetime.strptime(
                f"{request.birth_date} {request.birth_time}", 
                "%Y-%m-%d %H:%M"
            )
            
            # Format datetime with timezone
            formatted_datetime = birth_datetime.strftime("%Y-%m-%dT%H:%M:%S+05:30")
            
            # Prepare API parameters
            params = {
                "datetime": formatted_datetime,
                "coordinates": f"{request.latitude},{request.longitude}",
                "ayanamsa": "1",  # 1 for Lahiri
                "planets": "0,1,2,3,4,5,6,7,8,9,100,101,102",  # All planets including nodes
                "la": "en"  # English language
            }
            
            # Enable debug mode for troubleshooting
            self.debug = True
            
            # Make API request
            response = self._make_request("planet-position", params)
            
            if self.debug:
                print(f"Chart Request Params: {params}")
                print(f"Response Data: {response}")
            
            # Extract data
            chart_data = response.get("data", {})
            planet_data = chart_data.get("planet_position", [])
            
            # Convert planets
            planets = [
                self._convert_planet_position(planet)
                for planet in planet_data
            ]
            
            # Create chart summary with focus on sun, moon and ascendant signs
            sun_planet = next((p for p in planets if p.planet == Planet.SUN), None)
            moon_planet = next((p for p in planets if p.planet == Planet.MOON), None)
            ascendant_planet = next((p for p in planets if p.planet == Planet.ASCENDANT), None)
            
            # Group planets by sign
            planets_by_sign = {}
            for planet in planets:
                sign_name = planet.sign.name
                if sign_name not in planets_by_sign:
                    planets_by_sign[sign_name] = []
                planets_by_sign[sign_name].append(planet.planet.name)
            
            # Group planets by house
            planets_by_house = {}
            for planet in planets:
                house_num = str(planet.house)
                if house_num not in planets_by_house:
                    planets_by_house[house_num] = []
                planets_by_house[house_num].append(planet.planet.name)
            
            chart_summary = {
                "sun_sign": sun_planet.sign if sun_planet else None,
                "moon_sign": moon_planet.sign if moon_planet else None,
                "ascendant_sign": ascendant_planet.sign if ascendant_planet else None,
                "retrograde_planets": [p.planet.name for p in planets if p.retrograde],
                "planets_by_sign": planets_by_sign,
                "planets_by_house": planets_by_house
            }
            
            return BirthChartResponse(
                name=request.name,
                birth_datetime=birth_datetime,
                location={"latitude": request.latitude, "longitude": request.longitude},
                julian_day=0,  # Not provided in planet-position endpoint
                house_system=request.house_system,
                ayanamsa=request.ayanamsa,
                ayanamsa_value=0,  # Not provided in planet-position endpoint
                planets=planets,
                houses=[],  # Not provided in planet-position endpoint
                aspects=[],  # Not provided in planet-position endpoint
                chart_summary=chart_summary
            )
            
        except Exception as e:
            if self.debug:
                import traceback
                print(f"Error details: {traceback.format_exc()}")
            raise ValueError(f"Error generating birth chart with Prokerala API: {str(e)}")

    async def get_birth_chart_image(self, request: BirthChartRequest) -> str:
        """Get birth chart image data from Prokerala API"""
        try:
            # Convert datetime to ISO format with timezone
            birth_datetime = datetime.strptime(
                f"{request.birth_date} {request.birth_time}", 
                "%Y-%m-%d %H:%M"
            )
            
            # Format datetime with timezone
            formatted_datetime = birth_datetime.strftime("%Y-%m-%dT%H:%M:%S+05:30")
            
            # Prepare API parameters
            params = {
                "datetime": formatted_datetime,
                "coordinates": f"{request.latitude},{request.longitude}",
                "ayanamsa": "1",  # 1 for Lahiri
                "chart_style": "north-indian",  # North Indian style chart
                "chart_type": "rasi",  # Rasi (sign) based chart
                "chart_language": "en",  # English language
                "width": "600",  # Larger chart size
                "height": "600"  # Larger chart size
            }
            
            # Get access token
            headers = {
                "Authorization": f"Bearer {self._get_access_token()}",
                "Accept": "image/svg+xml"  # Request SVG format
            }
            
            # Make direct API request since we're expecting SVG, not JSON
            url = f"{self.base_url}/chart"
            response = requests.get(url, headers=headers, params=params)
            
            if self.debug:
                print("\n=== DEBUG: Chart Image Request ===")
                print(f"URL: {url}")
                print("Headers:")
                for key, value in headers.items():
                    print(f"  {key}: {value}")
                print("Parameters:")
                for key, value in params.items():
                    print(f"  {key}: {value}")
                print(f"Response Status: {response.status_code}")
                print("=== END Chart Image Request ===\n")
            
            response.raise_for_status()
            return response.text  # Return SVG content
            
        except Exception as e:
            if self.debug:
                import traceback
                print(f"Error details: {traceback.format_exc()}")
            raise ValueError(f"Error getting birth chart image: {str(e)}")

# Create service instance
prokerala_service = ProkeralaService() 