"""
Birth Chart Service using Prokerala API
"""

from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import pytz
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from app.models import (
    BirthChartRequest, BirthChartResponse, PlanetPosition, House, Aspect,
    Planet, ZodiacSign, HouseSystem, AyanamsaSystem, DetailedReportRequest, DetailedReportResponse
)
from app.services.prokerala_service import prokerala_service

# Load environment variables
load_dotenv()

class OpenAIService:
    """Service for generating AI-powered astrological interpretations"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return bool(self.client)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for astrological analysis"""
        return """You are an expert Vedic astrologer with deep knowledge of both traditional and modern astrological techniques.
        Analyze the birth chart data provided and generate insightful, personalized interpretations.
        Focus on practical insights while maintaining astrological accuracy.
        Be specific but avoid overly deterministic predictions."""
    
    def _get_prompt_for_report_type(self, report_type: str, chart_data: str) -> str:
        """Get specific prompt based on report type"""
        prompts = {
            "personality": f"Analyze the following birth chart and provide insights about personality traits, strengths, and potential areas for growth:\n\n{chart_data}",
            "career": f"Based on this birth chart, provide insights about career potential, professional strengths, and optimal work environments:\n\n{chart_data}",
            "relationship": f"Analyze this birth chart for relationship patterns, compatibility needs, and romantic tendencies:\n\n{chart_data}",
            "health": f"Examine this birth chart for health predispositions and wellness recommendations (Note: This is not medical advice):\n\n{chart_data}",
            "spiritual": f"Provide insights about spiritual path, karmic patterns, and soul purpose based on this birth chart:\n\n{chart_data}"
        }
        return prompts.get(report_type, "Analyze this birth chart and provide general insights.")
    
    def _parse_ai_response(self, content: str, report_type: str) -> Dict[str, Any]:
        """Parse and structure the AI response"""
        return {
            "type": report_type,
            "content": content,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_fallback_report(self, report_type: str, birth_chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a basic fallback report when AI is unavailable"""
        return {
            "type": report_type,
            "content": "Detailed analysis is currently unavailable. Please try again later.",
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }
    
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

class BirthChartService:
    """Service for generating birth charts using Prokerala API"""
    
    def __init__(self):
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
    
    async def generate_birth_chart(self, request: BirthChartRequest) -> BirthChartResponse:
        """Generate a comprehensive Vedic birth chart using Prokerala API."""
        try:
            # Validate input data
            self._validate_birth_data(request.birth_date, request.birth_time, 
                                    request.latitude, request.longitude, request.timezone)
            
            # Use Prokerala service to generate birth chart
            return await prokerala_service.generate_birth_chart(request)
            
        except Exception as e:
            raise ValueError(f"Error generating birth chart: {str(e)}")

    def generate_detailed_report(self, request: DetailedReportRequest) -> DetailedReportResponse:
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
        chart_data = self._birth_chart_to_dict(birth_chart)
        ai_report = self.openai_service.generate_astrological_report(
            "career", chart_data, birth_chart.name
        )
        return ai_report if self.openai_service.is_available() else self._generate_career_report_fallback(birth_chart)
    
    def _generate_relationship_report(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate love and relationships analysis using OpenAI."""
        chart_data = self._birth_chart_to_dict(birth_chart)
        ai_report = self.openai_service.generate_astrological_report(
            "relationship", chart_data, birth_chart.name
        )
        return ai_report if self.openai_service.is_available() else self._generate_relationship_report_fallback(birth_chart)
    
    def _generate_health_report(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate health and wellness analysis using OpenAI."""
        chart_data = self._birth_chart_to_dict(birth_chart)
        ai_report = self.openai_service.generate_astrological_report(
            "health", chart_data, birth_chart.name
        )
        return ai_report if self.openai_service.is_available() else self._generate_health_report_fallback(birth_chart)
    
    def _generate_spiritual_report(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate spiritual and karmic analysis using OpenAI."""
        chart_data = self._birth_chart_to_dict(birth_chart)
        ai_report = self.openai_service.generate_astrological_report(
            "spiritual", chart_data, birth_chart.name
        )
        return ai_report if self.openai_service.is_available() else self._generate_spiritual_report_fallback(birth_chart)
    
    def _birth_chart_to_dict(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Convert BirthChartResponse to dictionary for OpenAI processing."""
        return {
            "birth_datetime": birth_chart.birth_datetime.isoformat(),
            "location": birth_chart.location,
            "ayanamsa_value": birth_chart.ayanamsa_value,
            "planets": [
                {
                    "planet": p.planet.value,
                    "sign": p.sign.value,
                    "degree": p.degree,
                    "house": p.house,
                    "retrograde": p.retrograde
                }
                for p in birth_chart.planets
            ],
            "houses": [
                {
                    "number": h.number,
                    "cusp": h.cusp,
                    "sign": h.sign.value,
                    "ruler": h.ruler.value
                }
                for h in birth_chart.houses
            ],
            "chart_summary": birth_chart.chart_summary
        }
    
    def _generate_personality_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate basic personality report when OpenAI is unavailable."""
        return {
            "type": "personality",
            "content": "Basic personality analysis is available. For detailed insights, please try again later.",
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }
    
    def _generate_career_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate basic career report when OpenAI is unavailable."""
        return {
            "type": "career",
            "content": "Basic career analysis is available. For detailed insights, please try again later.",
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }
    
    def _generate_relationship_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate basic relationship report when OpenAI is unavailable."""
        return {
            "type": "relationship",
            "content": "Basic relationship analysis is available. For detailed insights, please try again later.",
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }
    
    def _generate_health_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate basic health report when OpenAI is unavailable."""
        return {
            "type": "health",
            "content": "Basic health analysis is available. For detailed insights, please try again later.",
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }
    
    def _generate_spiritual_report_fallback(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Generate basic spiritual report when OpenAI is unavailable."""
        return {
            "type": "spiritual",
            "content": "Basic spiritual analysis is available. For detailed insights, please try again later.",
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        }

# Create service instance
birth_chart_service = BirthChartService()
