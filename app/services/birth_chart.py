
import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any
import math
import pytz
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from app.models import (
    BirthChartRequest, BirthChartResponse, PlanetPosition, House, Aspect,
    Planet, ZodiacSign, HouseSystem, AyanamsaSystem, DetailedReportRequest, DetailedReportResponse
)

# Load environment variables
load_dotenv()

# Swiss Ephemeris planet constants
PLANET_CONSTANTS = {
    Planet.SUN: swe.SUN,
    Planet.MOON: swe.MOON,
    Planet.MERCURY: swe.MERCURY,
    Planet.VENUS: swe.VENUS,
    Planet.MARS: swe.MARS,
    Planet.JUPITER: swe.JUPITER,
    Planet.SATURN: swe.SATURN,
    Planet.URANUS: swe.URANUS,
    Planet.NEPTUNE: swe.NEPTUNE,
    Planet.PLUTO: swe.PLUTO,
    Planet.RAHU: swe.TRUE_NODE,
}

# House system constants
HOUSE_SYSTEMS = {
    HouseSystem.PLACIDUS: b'P',
    HouseSystem.KOCH: b'K',
    HouseSystem.EQUAL: b'E',
    HouseSystem.WHOLE_SIGN: b'W',
}

# Ayanamsa constants mapping
AYANAMSA_CONSTANTS = {
    AyanamsaSystem.LAHIRI: swe.SIDM_LAHIRI,
    AyanamsaSystem.RAMAN: swe.SIDM_RAMAN,
    AyanamsaSystem.KRISHNAMURTI: swe.SIDM_KRISHNAMURTI,
    AyanamsaSystem.DJWHAL_KHUL: swe.SIDM_DJWHAL_KHUL,
    AyanamsaSystem.YUKTESHWAR: swe.SIDM_YUKTESHWAR,
    AyanamsaSystem.JN_BHASIN: swe.SIDM_JN_BHASIN,
    AyanamsaSystem.BABYLONIAN_KUGLER1: swe.SIDM_BABYL_KUGLER1,
    AyanamsaSystem.BABYLONIAN_KUGLER2: swe.SIDM_BABYL_KUGLER2,
    AyanamsaSystem.BABYLONIAN_KUGLER3: swe.SIDM_BABYL_KUGLER3,
    AyanamsaSystem.BABYLONIAN_HUBER: swe.SIDM_BABYL_HUBER,
    AyanamsaSystem.BABYLONIAN_MERCIER: swe.SIDM_BABYL_ETPSC,  # Using ETPSC as closest alternative
    AyanamsaSystem.ALDEBARAN_15TAU: swe.SIDM_ALDEBARAN_15TAU,
    AyanamsaSystem.HIPPARCHOS: swe.SIDM_HIPPARCHOS,
    AyanamsaSystem.SASSANIAN: swe.SIDM_SASSANIAN,
    AyanamsaSystem.GALCENT_0SAG: swe.SIDM_GALCENT_0SAG,
    AyanamsaSystem.J2000: swe.SIDM_J2000,
    AyanamsaSystem.J1900: swe.SIDM_J1900,
    AyanamsaSystem.B1950: swe.SIDM_B1950,
}

# Zodiac signs
ZODIAC_SIGNS = [
    ZodiacSign.ARIES, ZodiacSign.TAURUS, ZodiacSign.GEMINI, ZodiacSign.CANCER,
    ZodiacSign.LEO, ZodiacSign.VIRGO, ZodiacSign.LIBRA, ZodiacSign.SCORPIO,
    ZodiacSign.SAGITTARIUS, ZodiacSign.CAPRICORN, ZodiacSign.AQUARIUS, ZodiacSign.PISCES
]

# Traditional rulers for houses
HOUSE_RULERS = {
    ZodiacSign.ARIES: Planet.MARS,
    ZodiacSign.TAURUS: Planet.VENUS,
    ZodiacSign.GEMINI: Planet.MERCURY,
    ZodiacSign.CANCER: Planet.MOON,
    ZodiacSign.LEO: Planet.SUN,
    ZodiacSign.VIRGO: Planet.MERCURY,
    ZodiacSign.LIBRA: Planet.VENUS,
    ZodiacSign.SCORPIO: Planet.MARS,
    ZodiacSign.SAGITTARIUS: Planet.JUPITER,
    ZodiacSign.CAPRICORN: Planet.SATURN,
    ZodiacSign.AQUARIUS: Planet.SATURN,
    ZodiacSign.PISCES: Planet.JUPITER,
}

# Aspect definitions (name, angle, orb)
ASPECTS = [
    ("Conjunction", 0, 8),
    ("Sextile", 60, 6),
    ("Square", 90, 8),
    ("Trine", 120, 8),
    ("Opposition", 180, 8),
    ("Quincunx", 150, 3),
    ("Semisextile", 30, 2),
    ("Semisquare", 45, 2),
    ("Sesquiquadrate", 135, 2),
]

class OpenAIService:
    """Service class for OpenAI integration for astrological report generation."""
    
    def __init__(self):
        self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.use_ai_reports = os.getenv("USE_AI_REPORTS", "true").lower() == "true"
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            self.client = OpenAI(api_key=api_key)
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available and configured."""
        return self.client is not None and self.use_ai_reports
    
    def generate_astrological_report(self, report_type: str, birth_chart_data: Dict[str, Any], 
                                   person_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate a personalized astrological report using OpenAI."""
        if not self.is_available():
            return self._get_fallback_report(report_type, birth_chart_data)
        
        try:
            # Prepare the birth chart data for AI analysis
            chart_summary = self._prepare_chart_data(birth_chart_data, person_name)
            
            # Generate the report based on type
            prompt = self._get_prompt_for_report_type(report_type, chart_summary)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Parse the response
            content = response.choices[0].message.content
            return self._parse_ai_response(content, report_type)
            
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return self._get_fallback_report(report_type, birth_chart_data)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the OpenAI assistant."""
        return """You are an expert Vedic astrologer with deep knowledge of traditional Indian astrology. 
        You specialize in creating personalized, insightful, and practical astrological reports.
        
        Your expertise includes:
        - Vedic astrology principles and techniques
        - Planetary influences and their meanings
        - House significations and their implications
        - Yogas and combinations in birth charts
        - Dasha periods and timing
        - Ayurvedic constitution and health
        - Karmic patterns and spiritual insights
        
        Always provide:
        - Accurate and traditional interpretations
        - Practical guidance and recommendations
        - Compassionate and empowering language
        - Specific insights based on the birth chart data
        - Cultural sensitivity to Vedic traditions
        
        CRITICAL: Format your response as a flat JSON object with multiple sections, each containing "title" and "description" fields.
        Example format:
        {
          "section1": {
            "title": "Section Title",
            "description": "Detailed description here..."
          },
          "section2": {
            "title": "Another Section Title", 
            "description": "Another detailed description..."
          }
        }
        
        Do NOT nest sections under other keys. Keep the structure flat and simple."""
    
    def _prepare_chart_data(self, birth_chart_data: Dict[str, Any], person_name: Optional[str]) -> str:
        """Prepare birth chart data for AI analysis."""
        name = person_name or "the individual"
        
        # Extract key information
        chart_info = f"Birth Chart Analysis for {name}:\n\n"
        
        # Add planetary positions
        if 'planets' in birth_chart_data:
            chart_info += "Planetary Positions:\n"
            for planet in birth_chart_data['planets']:
                chart_info += f"- {planet['planet']}: {planet['degree']:.1f}° {planet['sign']} in House {planet['house']}"
                if planet.get('retrograde'):
                    chart_info += " (Retrograde)"
                chart_info += "\n"
        
        # Add house information
        if 'houses' in birth_chart_data:
            chart_info += "\nHouse Cusps:\n"
            for house in birth_chart_data['houses'][:4]:  # Show first 4 houses
                chart_info += f"- House {house['number']}: {house['cusp']:.1f}° {house['sign']} (Ruler: {house['ruler']})\n"
        
        # Add birth details
        if 'birth_datetime' in birth_chart_data:
            chart_info += f"\nBirth Details:\n"
            chart_info += f"- Date & Time: {birth_chart_data['birth_datetime']}\n"
            chart_info += f"- Location: {birth_chart_data.get('location', 'Unknown')}\n"
            chart_info += f"- Ayanamsa: {birth_chart_data.get('ayanamsa_value', 'Unknown'):.2f}°\n"
        
        # Add chart summary
        if 'chart_summary' in birth_chart_data:
            summary = birth_chart_data['chart_summary']
            chart_info += f"\nChart Summary:\n"
            chart_info += f"- Sun Sign: {summary.get('sun_sign', 'Unknown')}\n"
            chart_info += f"- Moon Sign: {summary.get('moon_sign', 'Unknown')}\n"
            chart_info += f"- Ascendant: {summary.get('ascendant_sign', 'Unknown')}\n"
            chart_info += f"- Dominant Sign: {summary.get('dominant_sign', 'Unknown')}\n"
        
        return chart_info
    
    def _get_prompt_for_report_type(self, report_type: str, chart_summary: str) -> str:
        """Get the appropriate prompt for the report type."""
        base_prompt = f"{chart_summary}\n\n"
        
        if report_type == "personality":
            return base_prompt + """Based on this Vedic birth chart, provide a detailed personality analysis in the following JSON format:

            {
              "core_personality": {
                "title": "Core Personality Traits",
                "description": "Detailed analysis of core personality characteristics based on Sun, Moon, and Ascendant..."
              },
              "strengths": {
                "title": "Key Strengths and Natural Talents",
                "description": "Analysis of natural abilities, talents, and positive qualities..."
              },
              "growth_areas": {
                "title": "Areas for Personal Growth",
                "description": "Areas where personal development and growth would be beneficial..."
              },
              "life_purpose": {
                "title": "Life Purpose and Dharma",
                "description": "Analysis of life purpose, spiritual calling, and dharmic path..."
              }
            }
            
            Focus on how the Sun, Moon, and Ascendant interact to create the individual's core nature."""
        
        elif report_type == "career":
            return base_prompt + """Based on this Vedic birth chart, provide a comprehensive career analysis in the following JSON format:

            {
              "ideal_career_paths": {
                "title": "Ideal Career Paths and Professional Directions",
                "description": "Detailed analysis of suitable career paths based on 10th house, Sun placement, and planetary influences..."
              },
              "work_style": {
                "title": "Work Style and Professional Approach",
                "description": "Analysis of how the person approaches work, their professional style, and workplace preferences..."
              },
              "financial_prospects": {
                "title": "Financial Prospects and Wealth Potential",
                "description": "Analysis of earning potential, financial growth opportunities, and wealth-building strategies..."
              },
              "business_opportunities": {
                "title": "Business and Entrepreneurship Opportunities",
                "description": "Analysis of entrepreneurial potential, business ventures, and self-employment suitability..."
              }
            }
            
            Pay special attention to the 10th house, Sun placement, and Jupiter's influence. Provide specific, actionable insights."""
        
        elif report_type == "relationship":
            return base_prompt + """Based on this Vedic birth chart, provide a detailed relationship analysis in the following JSON format:

            {
              "love_nature": {
                "title": "Love Nature and Expression Style",
                "description": "Analysis of how the person expresses love and affection, their romantic nature..."
              },
              "relationship_patterns": {
                "title": "Relationship Patterns and Tendencies",
                "description": "Analysis of recurring patterns in relationships, behavioral tendencies..."
              },
              "compatibility": {
                "title": "Compatibility Insights and Partnership Needs",
                "description": "Analysis of what the person needs in a partner and compatibility factors..."
              },
              "marriage_timing": {
                "title": "Marriage and Commitment Patterns",
                "description": "Analysis of marriage timing, commitment readiness, and partnership dynamics..."
              }
            }
            
            Focus on Venus, Mars, and 7th house influences."""
        
        elif report_type == "health":
            return base_prompt + """Based on this Vedic birth chart, provide a health and wellness analysis in the following JSON format:

            {
              "constitution": {
                "title": "Ayurvedic Constitution and Body Type",
                "description": "Analysis of constitutional type (Vata, Pitta, Kapha) and body characteristics..."
              },
              "health_strengths": {
                "title": "Health Strengths and Vitality Areas",
                "description": "Analysis of areas of natural health strength and vitality..."
              },
              "health_challenges": {
                "title": "Potential Health Challenges",
                "description": "Analysis of potential health vulnerabilities and areas of concern..."
              },
              "wellness_recommendations": {
                "title": "Wellness Recommendations and Lifestyle Guidance",
                "description": "Specific recommendations for maintaining health and wellness..."
              }
            }
            
            Consider the 6th house, Sun, Moon, and overall planetary balance."""
        
        elif report_type == "spiritual":
            return base_prompt + """Based on this Vedic birth chart, provide a spiritual analysis in the following JSON format:

            {
              "spiritual_path": {
                "title": "Spiritual Path and Dharmic Direction",
                "description": "Analysis of the person's spiritual calling and dharmic path..."
              },
              "karmic_lessons": {
                "title": "Karmic Lessons and Soul Purpose",
                "description": "Analysis of karmic lessons to learn and soul's purpose in this lifetime..."
              },
              "spiritual_practices": {
                "title": "Recommended Spiritual Practices",
                "description": "Specific spiritual practices, meditation techniques, and rituals that benefit the person..."
              },
              "past_life_influences": {
                "title": "Past Life Influences and Karmic Patterns",
                "description": "Analysis of past life influences and recurring karmic patterns..."
              }
            }
            
            Focus on the 9th and 12th houses, and the Rahu-Ketu axis."""
        
        else:
            return base_prompt + f"Provide a comprehensive {report_type} analysis based on this birth chart."
    
    def _parse_ai_response(self, content: str, report_type: str) -> Dict[str, Any]:
        """Parse AI response and structure it appropriately."""
        try:
            # Try to parse as JSON first
            parsed = json.loads(content)
            
            # Check if the response is in the expected format
            if isinstance(parsed, dict):
                # Handle nested structure like {"CareerAnalysis": {"Sections": {...}}}
                structured_response = {}
                
                # Extract main sections from the parsed response
                for key, value in parsed.items():
                    if isinstance(value, dict):
                        # Check for "Sections" key (common in AI responses)
                        if "Sections" in value and isinstance(value["Sections"], dict):
                            # Extract individual sections
                            for section_key, section_data in value["Sections"].items():
                                if isinstance(section_data, dict) and "Title" in section_data and "Description" in section_data:
                                    # Convert to lowercase with underscores
                                    formatted_key = section_key.lower().replace(" ", "_")
                                    structured_response[formatted_key] = {
                                        "title": section_data["Title"],
                                        "description": section_data["Description"]
                                    }
                        
                        # Also check for direct title/description pairs
                        elif "Title" in value and "Description" in value:
                            formatted_key = key.lower().replace(" ", "_")
                            structured_response[formatted_key] = {
                                "title": value["Title"],
                                "description": value["Description"]
                            }
                        
                        # Handle flat structure where each key is a section
                        elif all(isinstance(v, dict) and "title" in v and "description" in v for v in value.values() if isinstance(v, dict)):
                            # This is already in the correct format
                            return value
                
                # If we found structured sections, return them
                if structured_response:
                    return structured_response
                
                # Fallback: return the parsed response as-is if it's properly structured
                return parsed
            else:
                # If it's not a dict, treat as text
                return self._create_single_section_response(content, report_type)
                
        except json.JSONDecodeError:
            # If not JSON, structure the text response
            return self._create_single_section_response(content, report_type)
    
    def _create_single_section_response(self, content: str, report_type: str) -> Dict[str, Any]:
        """Create a single section response for unstructured content."""
        return {
            f"{report_type}_analysis": {
                "title": f"{report_type.title()} Analysis",
                "description": content
            }
        }
    
    def _get_fallback_report(self, report_type: str, birth_chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback report when OpenAI is not available."""
        return {
            f"{report_type}_analysis": {
                "title": f"{report_type.title()} Analysis",
                "description": f"AI-powered {report_type} analysis is currently unavailable. Please ensure OpenAI API key is configured. Using traditional astrological interpretations as fallback."
            }
        }

class BirthChartService:
    def __init__(self):
        # Set ephemeris path (you may need to adjust this)
        swe.set_ephe_path('/usr/share/swisseph')
        
        # Initialize OpenAI service
        self.openai_service = OpenAIService()
    
    def _validate_birth_data(self, birth_date: str, birth_time: str, latitude: float, longitude: float, timezone_str: str = None):
        """Validate birth data inputs for accuracy."""
        errors = []
        
        # Validate date format
        try:
            date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
            if date_obj.year < 1900 or date_obj.year > 2100:
                errors.append(f"Birth year {date_obj.year} is outside optimal range (1900-2100)")
        except ValueError:
            errors.append(f"Invalid date format '{birth_date}'. Use YYYY-MM-DD format")
        
        # Validate time format
        try:
            datetime.strptime(birth_time, '%H:%M')
        except ValueError:
            errors.append(f"Invalid time format '{birth_time}'. Use HH:MM format (24-hour)")
        
        # Validate coordinates
        if not isinstance(latitude, (int, float)) or not (-90 <= latitude <= 90):
            errors.append(f"Invalid latitude {latitude}. Must be between -90 and +90 degrees")
        
        if not isinstance(longitude, (int, float)) or not (-180 <= longitude <= 180):
            errors.append(f"Invalid longitude {longitude}. Must be between -180 and +180 degrees")
        
        # Validate timezone
        if timezone_str:
            try:
                pytz.timezone(timezone_str)
            except pytz.exceptions.UnknownTimeZoneError:
                errors.append(f"Invalid timezone '{timezone_str}'. Use standard timezone names like 'America/New_York'")
        
        if errors:
            raise ValueError(f"Input validation failed: {'; '.join(errors)}")
    
    def get_zodiac_sign(self, longitude: float) -> ZodiacSign:
        """Get zodiac sign for a given longitude."""
        sign_index = int(longitude // 30)
        return ZODIAC_SIGNS[sign_index]
    
    def get_degree_in_sign(self, longitude: float) -> float:
        """Get degree within the sign for a given longitude."""
        return longitude % 30
    
    def calculate_ayanamsa(self, julian_day: float, ayanamsa_system: AyanamsaSystem) -> float:
        """Calculate ayanamsa value for given Julian day and system."""
        if ayanamsa_system not in AYANAMSA_CONSTANTS:
            raise ValueError(f"Unsupported ayanamsa system: {ayanamsa_system}")
        
        ayanamsa_constant = AYANAMSA_CONSTANTS[ayanamsa_system]
        swe.set_sid_mode(ayanamsa_constant)
        return swe.get_ayanamsa(julian_day)
    
    def apply_ayanamsa_correction(self, longitude: float, ayanamsa_value: float) -> float:
        """Apply ayanamsa correction to convert tropical to sidereal longitude."""
        corrected_longitude = longitude - ayanamsa_value
        if corrected_longitude < 0:
            corrected_longitude += 360
        return corrected_longitude
    
    def calculate_julian_day(self, birth_date: str, birth_time: str, timezone_str: Optional[str] = None) -> float:
        """Calculate Julian day for birth date and time with enhanced accuracy."""
        dt_str = f"{birth_date} {birth_time}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        
        if timezone_str:
            try:
                tz = pytz.timezone(timezone_str)
                
                # Handle DST ambiguity properly
                try:
                    dt = tz.localize(dt)
                except pytz.exceptions.AmbiguousTimeError:
                    # During DST overlap, use standard time
                    dt = tz.localize(dt, is_dst=False)
                except pytz.exceptions.NonExistentTimeError:
                    # During DST gap, use daylight time
                    dt = tz.localize(dt, is_dst=True)
                
                dt = dt.astimezone(pytz.UTC)
                
            except pytz.exceptions.UnknownTimeZoneError:
                raise ValueError(f"Invalid timezone: {timezone_str}")
            except Exception as e:
                raise ValueError(f"Timezone conversion failed: {e}")
        else:
            dt = dt.replace(tzinfo=pytz.UTC)
        
        # Enhanced precision calculation
        return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0)
    
    def calculate_planet_positions(self, julian_day: float, house_cusps: List[float], 
                                 ayanamsa_value: float) -> List[PlanetPosition]:
        """Calculate positions for all planets using Vedic (Sidereal) astrology."""
        planets = []
        
        for planet_enum in Planet:
            if planet_enum in PLANET_CONSTANTS:
                planet_id = PLANET_CONSTANTS[planet_enum]
                
                # Calculate position
                result = swe.calc_ut(julian_day, planet_id)
                position = result[0]
                longitude = position[0]
                latitude = position[1]
                distance = position[2]
                speed_val = position[3]
                
                # Always apply ayanamsa correction for Vedic (Sidereal) astrology
                longitude = self.apply_ayanamsa_correction(longitude, ayanamsa_value)
                
                # Handle Ketu (opposite of Rahu)
                if planet_enum == Planet.RAHU:
                    ketu_longitude = (longitude + 180) % 360
                    ketu_sign = self.get_zodiac_sign(ketu_longitude)
                    ketu_degree = self.get_degree_in_sign(ketu_longitude)
                    ketu_house = self.get_house_number(ketu_longitude, house_cusps)
                    
                    planets.append(PlanetPosition(
                        planet=Planet.KETU,
                        longitude=ketu_longitude,
                        latitude=-latitude,
                        distance=distance,
                        speed=-speed_val,
                        sign=ketu_sign,
                        degree=ketu_degree,
                        house=ketu_house,
                        retrograde=speed_val < 0
                    ))
                
                # Get sign and house
                sign = self.get_zodiac_sign(longitude)
                degree = self.get_degree_in_sign(longitude)
                house = self.get_house_number(longitude, house_cusps)
                
                planets.append(PlanetPosition(
                    planet=planet_enum,
                    longitude=longitude,
                    latitude=latitude,
                    distance=distance,
                    speed=speed_val,
                    sign=sign,
                    degree=degree,
                    house=house,
                    retrograde=speed_val < 0
                ))
        
        return planets
    
    def get_house_number(self, longitude: float, house_cusps: List[float]) -> int:
        """Determine which house a planet is in based on its longitude with accurate wraparound handling."""
        # Normalize longitude to 0-360 range
        longitude = longitude % 360
        
        # Normalize all house cusps
        normalized_cusps = [cusp % 360 for cusp in house_cusps]
        
        # Check each house with proper wraparound logic
        for i in range(12):
            cusp_current = normalized_cusps[i]
            cusp_next = normalized_cusps[(i + 1) % 12]
            
            # Handle wraparound at 0/360 degrees
            if cusp_current > cusp_next:
                # House crosses 0° (e.g., 350° to 10°)
                if longitude >= cusp_current or longitude < cusp_next:
                    return i + 1
            else:
                # Normal case - house doesn't cross 0°
                if cusp_current <= longitude < cusp_next:
                    return i + 1
        
        # Fallback to first house (should rarely happen)
        return 1
    
    def calculate_houses(self, julian_day: float, latitude: float, longitude: float, 
                        house_system: HouseSystem, ayanamsa_value: float) -> List[House]:
        """Calculate house cusps and create House objects using Vedic (Sidereal) astrology."""
        system_char = HOUSE_SYSTEMS[house_system]
        
        # Calculate houses
        houses_data = swe.houses(julian_day, latitude, longitude, system_char)
        house_cusps = houses_data[0][:12]  # First 12 are house cusps
        
        houses = []
        for i, cusp in enumerate(house_cusps):
            # Always apply ayanamsa correction for Vedic (Sidereal) astrology
            cusp = self.apply_ayanamsa_correction(cusp, ayanamsa_value)
            
            sign = self.get_zodiac_sign(cusp)
            ruler = HOUSE_RULERS[sign]
            
            houses.append(House(
                number=i + 1,
                cusp=cusp,
                sign=sign,
                ruler=ruler
            ))
        
        return houses
    
    def calculate_aspects(self, planets: List[PlanetPosition]) -> List[Aspect]:
        """Calculate aspects between planets."""
        aspects = []
        
        for i, planet1 in enumerate(planets):
            for j, planet2 in enumerate(planets[i+1:], i+1):
                angle = abs(planet1.longitude - planet2.longitude)
                if angle > 180:
                    angle = 360 - angle
                
                for aspect_name, aspect_angle, orb in ASPECTS:
                    orb_diff = abs(angle - aspect_angle)
                    if orb_diff <= orb:
                        # Determine if applying or separating (simplified)
                        applying = planet1.speed > planet2.speed
                        
                        aspects.append(Aspect(
                            planet1=planet1.planet,
                            planet2=planet2.planet,
                            aspect_type=aspect_name,
                            angle=angle,
                            orb=orb_diff,
                            applying=applying
                        ))
                        break
        
        return aspects
    
    def generate_chart_summary(self, planets: List[PlanetPosition], houses: List[House]) -> Dict[str, Any]:
        """Generate a summary of the chart."""
        # Count planets by sign
        sign_counts = {}
        for planet in planets:
            sign = planet.sign
            if sign not in sign_counts:
                sign_counts[sign] = 0
            sign_counts[sign] += 1
        
        # Count planets by house
        house_counts = {}
        for planet in planets:
            house = planet.house
            if house not in house_counts:
                house_counts[house] = 0
            house_counts[house] += 1
        
        # Find dominant sign and house
        dominant_sign = max(sign_counts, key=sign_counts.get) if sign_counts else None
        dominant_house = max(house_counts, key=house_counts.get) if house_counts else None
        
        # Count retrograde planets
        retrograde_count = sum(1 for planet in planets if planet.retrograde)
        
        return {
            "dominant_sign": dominant_sign,
            "dominant_house": dominant_house,
            "retrograde_planets": retrograde_count,
            "planets_by_sign": sign_counts,
            "planets_by_house": house_counts,
            "sun_sign": next((p.sign for p in planets if p.planet == Planet.SUN), None),
            "moon_sign": next((p.sign for p in planets if p.planet == Planet.MOON), None),
            "ascendant_sign": houses[0].sign if houses else None,
        }
    
    def generate_birth_chart(self, request: BirthChartRequest) -> BirthChartResponse:
        """Generate a comprehensive Vedic birth chart with enhanced accuracy."""
        try:
            # Validate input data
            self._validate_birth_data(request.birth_date, request.birth_time, 
                                    request.latitude, request.longitude, request.timezone)
            
            # Calculate Julian day
            julian_day = self.calculate_julian_day(
                request.birth_date, 
                request.birth_time, 
                request.timezone
            )
            
            # Calculate ayanamsa for Vedic (Sidereal) astrology
            ayanamsa_value = self.calculate_ayanamsa(julian_day, request.ayanamsa)
            
            # Calculate houses first (needed for planet house placement)
            houses = self.calculate_houses(
                julian_day, 
                request.latitude, 
                request.longitude, 
                request.house_system,
                ayanamsa_value
            )
            
            # Get house cusps for planet calculations
            house_cusps = [house.cusp for house in houses]
            
            # Calculate planet positions
            planets = self.calculate_planet_positions(
                julian_day, 
                house_cusps, 
                ayanamsa_value
            )
            
            # Calculate aspects
            aspects = self.calculate_aspects(planets)
            
            # Generate summary
            chart_summary = self.generate_chart_summary(planets, houses)
            
            # Create birth datetime
            birth_datetime = datetime.strptime(
                f"{request.birth_date} {request.birth_time}", 
                "%Y-%m-%d %H:%M"
            )
            
            return BirthChartResponse(
                name=request.name,
                birth_datetime=birth_datetime,
                location={"latitude": request.latitude, "longitude": request.longitude},
                julian_day=julian_day,
                house_system=request.house_system,
                ayanamsa=request.ayanamsa,
                ayanamsa_value=ayanamsa_value,
                planets=planets,
                houses=houses,
                aspects=aspects,
                chart_summary=chart_summary
            )
            
        except Exception as e:
            raise ValueError(f"Error generating birth chart: {str(e)}")

    def generate_detailed_report(self, request) -> 'DetailedReportResponse':
        """Generate a comprehensive detailed astrological report."""
        try:
            # First generate the birth chart
            birth_chart_request = BirthChartRequest(
                name=request.name,
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                latitude=request.latitude,
                longitude=request.longitude,
                timezone=request.timezone,
                house_system=request.house_system,
                ayanamsa=request.ayanamsa
            )
            
            birth_chart = self.generate_birth_chart(birth_chart_request)
            
            # Generate detailed interpretations
            personality_report = self._generate_personality_report(birth_chart)
            career_report = self._generate_career_report(birth_chart)
            relationship_report = self._generate_relationship_report(birth_chart)
            health_report = self._generate_health_report(birth_chart)
            spiritual_report = self._generate_spiritual_report(birth_chart)
            
            from app.models import DetailedReportResponse
            return DetailedReportResponse(
                name=request.name,
                birth_chart=birth_chart,
                personality_report=personality_report,
                career_report=career_report,
                relationship_report=relationship_report,
                health_report=health_report,
                spiritual_report=spiritual_report
            )
            
        except Exception as e:
            raise ValueError(f"Error generating detailed report: {str(e)}")

    def _generate_personality_report(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate personality analysis based on birth chart using OpenAI."""
        # Convert birth chart to dictionary for OpenAI processing
        chart_data = self._birth_chart_to_dict(birth_chart)
        
        # Use OpenAI service to generate the report
        ai_report = self.openai_service.generate_astrological_report(
            "personality", chart_data, birth_chart.name
        )
        
        # If OpenAI is available, use AI-generated content
        if self.openai_service.is_available():
            return ai_report
        
        # Fallback to template-based approach
        return self._generate_personality_report_fallback(birth_chart)
    
    def _generate_career_report(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate career and purpose analysis using OpenAI."""
        # Convert birth chart to dictionary for OpenAI processing
        chart_data = self._birth_chart_to_dict(birth_chart)
        
        # Use OpenAI service to generate the report
        ai_report = self.openai_service.generate_astrological_report(
            "career", chart_data, birth_chart.name
        )
        
        # If OpenAI is available, use AI-generated content
        if self.openai_service.is_available():
            return ai_report
        
        # Fallback to template-based approach
        return self._generate_career_report_fallback(birth_chart)
    
    def _generate_relationship_report(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate love and relationships analysis using OpenAI."""
        # Convert birth chart to dictionary for OpenAI processing
        chart_data = self._birth_chart_to_dict(birth_chart)
        
        # Use OpenAI service to generate the report
        ai_report = self.openai_service.generate_astrological_report(
            "relationship", chart_data, birth_chart.name
        )
        
        # If OpenAI is available, use AI-generated content
        if self.openai_service.is_available():
            return ai_report
        
        # Fallback to template-based approach
        return self._generate_relationship_report_fallback(birth_chart)
    
    def _generate_health_report(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate health and wellness analysis using OpenAI."""
        # Convert birth chart to dictionary for OpenAI processing
        chart_data = self._birth_chart_to_dict(birth_chart)
        
        # Use OpenAI service to generate the report
        ai_report = self.openai_service.generate_astrological_report(
            "health", chart_data, birth_chart.name
        )
        
        # If OpenAI is available, use AI-generated content
        if self.openai_service.is_available():
            return ai_report
        
        # Fallback to template-based approach
        return self._generate_health_report_fallback(birth_chart)
    
    def _generate_spiritual_report(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate spiritual and karmic analysis using OpenAI."""
        # Convert birth chart to dictionary for OpenAI processing
        chart_data = self._birth_chart_to_dict(birth_chart)
        
        # Use OpenAI service to generate the report
        ai_report = self.openai_service.generate_astrological_report(
            "spiritual", chart_data, birth_chart.name
        )
        
        # If OpenAI is available, use AI-generated content
        if self.openai_service.is_available():
            return ai_report
        
        # Fallback to template-based approach
        return self._generate_spiritual_report_fallback(birth_chart)

    # Helper methods for OpenAI integration
    def _birth_chart_to_dict(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Convert BirthChartResponse to dictionary for OpenAI processing."""
        return {
            "name": birth_chart.name,
            "birth_datetime": birth_chart.birth_datetime.isoformat(),
            "location": birth_chart.location,
            "julian_day": birth_chart.julian_day,
            "house_system": birth_chart.house_system.value,
            "ayanamsa": birth_chart.ayanamsa.value,
            "ayanamsa_value": birth_chart.ayanamsa_value,
            "planets": [
                {
                    "planet": planet.planet.value,
                    "longitude": planet.longitude,
                    "latitude": planet.latitude,
                    "distance": planet.distance,
                    "speed": planet.speed,
                    "sign": planet.sign.value,
                    "degree": planet.degree,
                    "house": planet.house,
                    "retrograde": planet.retrograde
                }
                for planet in birth_chart.planets
            ],
            "houses": [
                {
                    "number": house.number,
                    "cusp": house.cusp,
                    "sign": house.sign.value,
                    "ruler": house.ruler.value
                }
                for house in birth_chart.houses
            ],
            "aspects": [
                {
                    "planet1": aspect.planet1.value,
                    "planet2": aspect.planet2.value,
                    "aspect_type": aspect.aspect_type,
                    "angle": aspect.angle,
                    "orb": aspect.orb,
                    "applying": aspect.applying
                }
                for aspect in birth_chart.aspects
            ],
            "chart_summary": birth_chart.chart_summary
        }

    # Fallback methods for template-based reports (when OpenAI is not available)
    def _generate_personality_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate personality analysis using template-based approach."""
        sun_planet = next((p for p in birth_chart.planets if p.planet == Planet.SUN), None)
        moon_planet = next((p for p in birth_chart.planets if p.planet == Planet.MOON), None)
        ascendant = birth_chart.houses[0] if birth_chart.houses else None
        
        # Basic personality traits based on Sun sign
        sun_traits = self._get_sun_sign_traits(sun_planet.sign if sun_planet else None)
        moon_traits = self._get_moon_sign_traits(moon_planet.sign if moon_planet else None)
        ascendant_traits = self._get_ascendant_traits(ascendant.sign if ascendant else None)
        
        return {
            "core_personality": {
                "title": "Core Personality Traits",
                "description": f"Your {sun_planet.sign if sun_planet else 'Sun'} Sun combined with {moon_planet.sign if moon_planet else 'Moon'} Moon creates a unique blend of energies. {sun_traits['description']} This is balanced by your {moon_planet.sign if moon_planet else 'Moon'} Moon, which {moon_traits['description']}"
            },
            "strengths": {
                "title": "Key Strengths",
                "description": f"Your greatest strengths come from your {ascendant.sign if ascendant else 'Ascendant'} rising sign, which gives you {ascendant_traits['strengths']}. Combined with your planetary positions, you possess {sun_traits['strengths']} and {moon_traits['strengths']}."
            },
            "growth_areas": {
                "title": "Areas for Growth",
                "description": f"To reach your full potential, focus on {sun_traits['growth_areas']}. Your {moon_planet.sign if moon_planet else 'Moon'} Moon suggests working on {moon_traits['growth_areas']}."
            },
            "life_purpose": {
                "title": "Life Purpose & Dharma",
                "description": self._get_life_purpose_analysis(birth_chart)
            }
        }

    def _generate_career_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate career analysis using template-based approach."""
        tenth_house = next((h for h in birth_chart.houses if h.number == 10), None)
        sun_planet = next((p for p in birth_chart.planets if p.planet == Planet.SUN), None)
        jupiter_planet = next((p for p in birth_chart.planets if p.planet == Planet.JUPITER), None)
        
        return {
            "career_path": {
                "title": "Ideal Career Path",
                "description": f"Your 10th house of career is in {tenth_house.sign if tenth_house else 'unknown'}, suggesting success in {self._get_career_suggestions(tenth_house.sign if tenth_house else None)}. Your Sun in {sun_planet.sign if sun_planet else 'unknown'} indicates leadership abilities in {self._get_sun_career_traits(sun_planet.sign if sun_planet else None)}."
            },
            "work_style": {
                "title": "Work Style & Approach",
                "description": f"You work best in environments that align with your {sun_planet.sign if sun_planet else 'Sun'} nature. {self._get_work_style_analysis(sun_planet.sign if sun_planet else None)}"
            },
            "financial_prospects": {
                "title": "Financial Outlook",
                "description": f"Your Jupiter in {jupiter_planet.sign if jupiter_planet else 'unknown'} in the {jupiter_planet.house if jupiter_planet else 'unknown'} house suggests {self._get_financial_analysis(jupiter_planet)}"
            },
            "business_ventures": {
                "title": "Business & Entrepreneurship",
                "description": self._get_business_analysis(birth_chart)
            }
        }

    def _generate_relationship_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate relationship analysis using template-based approach."""
        venus_planet = next((p for p in birth_chart.planets if p.planet == Planet.VENUS), None)
        mars_planet = next((p for p in birth_chart.planets if p.planet == Planet.MARS), None)
        seventh_house = next((h for h in birth_chart.houses if h.number == 7), None)
        
        return {
            "love_nature": {
                "title": "Love Language & Expression",
                "description": f"Your Venus in {venus_planet.sign if venus_planet else 'unknown'} shows you express love through {self._get_venus_love_style(venus_planet.sign if venus_planet else None)}. Your Mars in {mars_planet.sign if mars_planet else 'unknown'} indicates {self._get_mars_passion_style(mars_planet.sign if mars_planet else None)}."
            },
            "relationship_patterns": {
                "title": "Relationship Patterns",
                "description": f"Your 7th house of partnerships is in {seventh_house.sign if seventh_house else 'unknown'}, suggesting you attract partners who are {self._get_partnership_traits(seventh_house.sign if seventh_house else None)}."
            },
            "compatibility": {
                "title": "Compatibility Insights",
                "description": self._get_compatibility_analysis(birth_chart)
            },
            "marriage_timing": {
                "title": "Marriage & Commitment",
                "description": self._get_marriage_timing_analysis(birth_chart)
            }
        }

    def _generate_health_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate health analysis using template-based approach."""
        sixth_house = next((h for h in birth_chart.houses if h.number == 6), None)
        sun_planet = next((p for p in birth_chart.planets if p.planet == Planet.SUN), None)
        moon_planet = next((p for p in birth_chart.planets if p.planet == Planet.MOON), None)
        
        return {
            "constitution": {
                "title": "Ayurvedic Constitution",
                "description": f"Based on your {sun_planet.sign if sun_planet else 'Sun'} Sun and {moon_planet.sign if moon_planet else 'Moon'} Moon, your constitution is primarily {self._get_ayurvedic_constitution(sun_planet, moon_planet)}."
            },
            "health_strengths": {
                "title": "Health Strengths",
                "description": f"Your {sun_planet.sign if sun_planet else 'Sun'} Sun gives you {self._get_health_strengths(sun_planet.sign if sun_planet else None)}."
            },
            "health_challenges": {
                "title": "Areas of Health Concern",
                "description": f"Your 6th house in {sixth_house.sign if sixth_house else 'unknown'} suggests paying attention to {self._get_health_challenges(sixth_house.sign if sixth_house else None)}."
            },
            "wellness_recommendations": {
                "title": "Wellness Recommendations",
                "description": self._get_wellness_recommendations(birth_chart)
            }
        }

    def _generate_spiritual_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate spiritual analysis using template-based approach."""
        ninth_house = next((h for h in birth_chart.houses if h.number == 9), None)
        twelfth_house = next((h for h in birth_chart.houses if h.number == 12), None)
        rahu_planet = next((p for p in birth_chart.planets if p.planet == Planet.RAHU), None)
        ketu_planet = next((p for p in birth_chart.planets if p.planet == Planet.KETU), None)
        
        return {
            "spiritual_path": {
                "title": "Spiritual Path & Dharma",
                "description": f"Your 9th house of spirituality is in {ninth_house.sign if ninth_house else 'unknown'}, indicating your spiritual path involves {self._get_spiritual_path(ninth_house.sign if ninth_house else None)}."
            },
            "karmic_lessons": {
                "title": "Karmic Lessons",
                "description": f"Your Rahu in {rahu_planet.sign if rahu_planet else 'unknown'} and Ketu in {ketu_planet.sign if ketu_planet else 'unknown'} suggest this lifetime's karmic focus is {self._get_karmic_lessons(rahu_planet, ketu_planet)}."
            },
            "meditation_practices": {
                "title": "Recommended Spiritual Practices",
                "description": f"Based on your {twelfth_house.sign if twelfth_house else 'unknown'} 12th house, practices like {self._get_meditation_recommendations(twelfth_house.sign if twelfth_house else None)} would be beneficial."
            },
            "past_life_influences": {
                "title": "Past Life Influences",
                "description": self._get_past_life_analysis(birth_chart)
            }
        }

    # Helper methods for generating specific interpretations
    def _get_sun_sign_traits(self, sign: ZodiacSign) -> Dict[str, str]:
        """Get personality traits for Sun sign."""
        traits = {
            ZodiacSign.ARIES: {
                "description": "brings dynamic leadership energy and pioneering spirit",
                "strengths": "natural leadership, courage, and initiative",
                "growth_areas": "patience and considering others' perspectives"
            },
            ZodiacSign.TAURUS: {
                "description": "provides stability, practicality, and appreciation for beauty",
                "strengths": "reliability, persistence, and aesthetic sense",
                "growth_areas": "flexibility and openness to change"
            },
            ZodiacSign.GEMINI: {
                "description": "brings curiosity, communication skills, and adaptability",
                "strengths": "versatility, intellectual agility, and social skills",
                "growth_areas": "focus and depth in commitments"
            },
            ZodiacSign.CANCER: {
                "description": "provides emotional depth, intuition, and nurturing qualities",
                "strengths": "empathy, protective instincts, and emotional intelligence",
                "growth_areas": "emotional boundaries and self-protection"
            },
            ZodiacSign.LEO: {
                "description": "brings creativity, warmth, and natural charisma",
                "strengths": "self-expression, generosity, and inspiring others",
                "growth_areas": "humility and sharing the spotlight"
            },
            ZodiacSign.VIRGO: {
                "description": "provides analytical skills, attention to detail, and service orientation",
                "strengths": "precision, helpfulness, and problem-solving abilities",
                "growth_areas": "self-acceptance and avoiding perfectionism"
            },
            ZodiacSign.LIBRA: {
                "description": "brings harmony, diplomacy, and aesthetic appreciation",
                "strengths": "balance, fairness, and relationship skills",
                "growth_areas": "decision-making and asserting personal needs"
            },
            ZodiacSign.SCORPIO: {
                "description": "provides intensity, transformation, and deep insight",
                "strengths": "emotional depth, investigation, and regeneration",
                "growth_areas": "trust and letting go of control"
            },
            ZodiacSign.SAGITTARIUS: {
                "description": "brings wisdom-seeking, adventure, and philosophical nature",
                "strengths": "optimism, teaching, and expanding horizons",
                "growth_areas": "attention to details and practical matters"
            },
            ZodiacSign.CAPRICORN: {
                "description": "provides ambition, discipline, and practical wisdom",
                "strengths": "goal achievement, responsibility, and long-term planning",
                "growth_areas": "emotional expression and work-life balance"
            },
            ZodiacSign.AQUARIUS: {
                "description": "brings innovation, humanitarian ideals, and independence",
                "strengths": "originality, social consciousness, and forward-thinking",
                "growth_areas": "emotional connection and personal relationships"
            },
            ZodiacSign.PISCES: {
                "description": "provides intuition, compassion, and spiritual sensitivity",
                "strengths": "empathy, creativity, and spiritual insight",
                "growth_areas": "boundaries and practical life management"
            }
        }
        return traits.get(sign, {
            "description": "brings unique qualities to your personality",
            "strengths": "individual talents and capabilities",
            "growth_areas": "personal development and self-awareness"
        })
    
    def _get_moon_sign_traits(self, sign: ZodiacSign) -> Dict[str, str]:
        """Get emotional traits for Moon sign."""
        traits = {
            ZodiacSign.ARIES: {
                "description": "gives you quick emotional responses and a need for independence",
                "strengths": "emotional courage and spontaneity",
                "growth_areas": "patience in emotional matters"
            },
            ZodiacSign.TAURUS: {
                "description": "provides emotional stability and a need for security",
                "strengths": "emotional steadiness and comfort-seeking",
                "growth_areas": "emotional flexibility"
            },
            ZodiacSign.GEMINI: {
                "description": "creates changeable moods and need for mental stimulation",
                "strengths": "emotional adaptability and communication",
                "growth_areas": "emotional depth and consistency"
            },
            ZodiacSign.CANCER: {
                "description": "amplifies intuition and emotional sensitivity",
                "strengths": "deep emotional understanding and nurturing",
                "growth_areas": "emotional protection and boundaries"
            },
            ZodiacSign.LEO: {
                "description": "brings emotional drama and need for recognition",
                "strengths": "emotional warmth and generosity",
                "growth_areas": "emotional humility"
            },
            ZodiacSign.VIRGO: {
                "description": "creates analytical emotions and need for practical service",
                "strengths": "emotional helpfulness and attention to detail",
                "growth_areas": "emotional self-acceptance"
            },
            ZodiacSign.LIBRA: {
                "description": "seeks emotional harmony and partnership",
                "strengths": "emotional balance and fairness",
                "growth_areas": "emotional independence"
            },
            ZodiacSign.SCORPIO: {
                "description": "intensifies emotions and creates need for transformation",
                "strengths": "emotional depth and regeneration",
                "growth_areas": "emotional trust and letting go"
            },
            ZodiacSign.SAGITTARIUS: {
                "description": "brings optimistic emotions and need for freedom",
                "strengths": "emotional adventure and wisdom-seeking",
                "growth_areas": "emotional grounding"
            },
            ZodiacSign.CAPRICORN: {
                "description": "creates reserved emotions and need for achievement",
                "strengths": "emotional discipline and goal-orientation",
                "growth_areas": "emotional expression and vulnerability"
            },
            ZodiacSign.AQUARIUS: {
                "description": "brings detached emotions and need for independence",
                "strengths": "emotional objectivity and humanitarian feelings",
                "growth_areas": "emotional intimacy"
            },
            ZodiacSign.PISCES: {
                "description": "creates intuitive emotions and spiritual sensitivity",
                "strengths": "emotional empathy and spiritual connection",
                "growth_areas": "emotional boundaries and practical grounding"
            }
        }
        return traits.get(sign, {
            "description": "influences your emotional nature in unique ways",
            "strengths": "individual emotional gifts",
            "growth_areas": "emotional development and balance"
        })
    
    def _get_ascendant_traits(self, sign: ZodiacSign) -> Dict[str, str]:
        """Get personality traits for Ascendant sign."""
        traits = {
            ZodiacSign.ARIES: {"strengths": "dynamic presence and natural leadership"},
            ZodiacSign.TAURUS: {"strengths": "steady presence and practical approach"},
            ZodiacSign.GEMINI: {"strengths": "adaptable communication and intellectual curiosity"},
            ZodiacSign.CANCER: {"strengths": "nurturing approach and emotional sensitivity"},
            ZodiacSign.LEO: {"strengths": "charismatic presence and creative expression"},
            ZodiacSign.VIRGO: {"strengths": "attention to detail and helpful nature"},
            ZodiacSign.LIBRA: {"strengths": "diplomatic approach and aesthetic sense"},
            ZodiacSign.SCORPIO: {"strengths": "intense presence and transformative ability"},
            ZodiacSign.SAGITTARIUS: {"strengths": "adventurous spirit and philosophical outlook"},
            ZodiacSign.CAPRICORN: {"strengths": "authoritative presence and practical wisdom"},
            ZodiacSign.AQUARIUS: {"strengths": "unique perspective and humanitarian approach"},
            ZodiacSign.PISCES: {"strengths": "intuitive understanding and compassionate nature"}
        }
        return traits.get(sign, {"strengths": "unique personal qualities"})
    
    # Additional helper methods
    def _get_life_purpose_analysis(self, birth_chart: BirthChartResponse) -> str:
        return "Your life purpose involves serving others while expressing your unique creative gifts. The combination of your planetary positions suggests a path of teaching, healing, or inspiring others through your authentic self-expression."
    
    def _get_career_suggestions(self, sign: ZodiacSign) -> str:
        career_map = {
            ZodiacSign.ARIES: "leadership, military, sports, or entrepreneurship",
            ZodiacSign.TAURUS: "banking, agriculture, arts, or luxury goods",
            ZodiacSign.GEMINI: "communication, writing, teaching, or technology",
            ZodiacSign.CANCER: "healthcare, hospitality, real estate, or counseling",
            ZodiacSign.LEO: "entertainment, politics, education, or creative fields",
            ZodiacSign.VIRGO: "healthcare, research, service, or analytical work",
            ZodiacSign.LIBRA: "law, diplomacy, beauty, or relationship counseling",
            ZodiacSign.SCORPIO: "investigation, psychology, research, or transformation work",
            ZodiacSign.SAGITTARIUS: "education, travel, philosophy, or publishing",
            ZodiacSign.CAPRICORN: "management, government, construction, or traditional fields",
            ZodiacSign.AQUARIUS: "technology, humanitarian work, science, or innovation",
            ZodiacSign.PISCES: "healthcare, spirituality, arts, or service to others"
        }
        return career_map.get(sign, "fields that align with your natural talents")
    
    def _get_sun_career_traits(self, sign: ZodiacSign) -> str:
        return "areas where you can shine and express your authentic self"
    
    def _get_work_style_analysis(self, sign: ZodiacSign) -> str:
        return "You prefer collaborative environments where you can make a meaningful impact while expressing your creativity and leadership abilities."
    
    def _get_financial_analysis(self, jupiter_planet) -> str:
        if jupiter_planet and jupiter_planet.house:
            house_meanings = {
                1: "good earning potential through personal efforts",
                2: "natural wealth accumulation abilities",
                3: "income through communication or siblings",
                4: "property and real estate investments",
                5: "creative ventures and speculation",
                6: "steady income through service",
                7: "partnerships and business collaborations",
                8: "transformation and shared resources",
                9: "higher education and wisdom-based income",
                10: "career advancement and recognition",
                11: "networking and large organizations",
                12: "foreign connections and spiritual work"
            }
            return house_meanings.get(jupiter_planet.house, "unique financial opportunities")
        return "varied financial opportunities based on your efforts and wisdom"
    
    def _get_business_analysis(self, birth_chart: BirthChartResponse) -> str:
        return "Your planetary configuration suggests success in businesses that combine your creative vision with practical service to others."
    
    def _get_venus_love_style(self, sign: ZodiacSign) -> str:
        return "romantic gestures and deep emotional connection"
    
    def _get_mars_passion_style(self, sign: ZodiacSign) -> str:
        return "direct and honest expression of desires"
    
    def _get_partnership_traits(self, sign: ZodiacSign) -> str:
        return "complementary to your nature and supportive of your growth"
    
    def _get_compatibility_analysis(self, birth_chart: BirthChartResponse) -> str:
        return "You are most compatible with partners who appreciate both your emotional depth and your need for creative expression."
    
    def _get_marriage_timing_analysis(self, birth_chart: BirthChartResponse) -> str:
        return "Marriage is likely to occur during periods when you feel emotionally secure and have established your personal identity."
    
    def _get_ayurvedic_constitution(self, sun_planet, moon_planet) -> str:
        return "a balanced constitution with emphasis on maintaining harmony between mind, body, and spirit"
    
    def _get_health_strengths(self, sign: ZodiacSign) -> str:
        return "good vitality and natural healing abilities"
    
    def _get_health_challenges(self, sign: ZodiacSign) -> str:
        return "stress management and maintaining work-life balance"
    
    def _get_wellness_recommendations(self, birth_chart: BirthChartResponse) -> str:
        return "Regular meditation, yoga, and creative expression will support your overall well-being. Pay attention to your emotional health as it directly impacts your physical vitality."
    
    def _get_spiritual_path(self, sign: ZodiacSign) -> str:
        return "exploring wisdom traditions and sharing your insights with others"
    
    def _get_karmic_lessons(self, rahu_planet, ketu_planet) -> str:
        return "learning to balance material success with spiritual growth"
    
    def _get_meditation_recommendations(self, sign: ZodiacSign) -> str:
        return "mindfulness meditation, chanting, and contemplative practices"
    
    def _get_past_life_analysis(self, birth_chart: BirthChartResponse) -> str:
        return "Your soul carries wisdom from past lives in service and teaching. This lifetime offers opportunities to integrate spiritual wisdom with practical application."

# Create service instance
birth_chart_service = BirthChartService()

# Legacy function for backward compatibility
def generate_birth_chart(date: str, time: str, lat: float, lon: float):
    """Legacy function for backward compatibility."""
    request = BirthChartRequest(
        birth_date=date,
        birth_time=time,
        latitude=lat,
        longitude=lon
    )
    return birth_chart_service.generate_birth_chart(request)
