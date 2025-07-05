#!/usr/bin/env python3
"""
Comprehensive demo of the Starlight Astrology API functionality.
This script demonstrates all the features of the birth chart API.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
from app.models import BirthChartRequest, HouseSystem
from app.services.birth_chart import birth_chart_service

def demo_birth_chart_api():
    """Demonstrate the complete birth chart API functionality."""
    print("🌟 Starlight Astrology API Demo")
    print("=" * 60)
    
    # Demo 1: Famous Person - Albert Einstein
    print("\n🎯 Demo 1: Albert Einstein's Birth Chart")
    print("-" * 40)
    
    einstein_request = BirthChartRequest(
        name="Albert Einstein",
        birth_date="1879-03-14",
        birth_time="11:30",
        latitude=48.3969,  # Ulm, Germany
        longitude=9.9918,
        timezone="Europe/Berlin",
        house_system=HouseSystem.PLACIDUS
    )
    
    try:
        chart = birth_chart_service.generate_birth_chart(einstein_request)
        print(f"✅ Successfully generated chart for {chart.name}")
        print(f"📅 Birth: {chart.birth_datetime}")
        print(f"🏠 House System: {chart.house_system}")
        print(f"🌟 Sun Sign: {chart.chart_summary['sun_sign']}")
        print(f"🌙 Moon Sign: {chart.chart_summary['moon_sign']}")
        print(f"⬆️ Ascendant: {chart.chart_summary['ascendant_sign']}")
        print(f"🔮 Dominant Sign: {chart.chart_summary['dominant_sign']}")
        print(f"🔄 Retrograde Planets: {chart.chart_summary['retrograde_planets']}")
        
        # Show some key planets
        print("\n🪐 Key Planet Positions:")
        for planet in chart.planets:
            if planet.planet.value in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']:
                retrograde_symbol = " [R]" if planet.retrograde else ""
                print(f"  {planet.planet.value:>7}: {planet.degree:.1f}° {planet.sign.value} in House {planet.house}{retrograde_symbol}")
        
        # Show some aspects
        print("\n🔄 Major Aspects:")
        major_aspects = [a for a in chart.aspects if a.aspect_type in ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']]
        for aspect in major_aspects[:5]:
            print(f"  {aspect.planet1.value} {aspect.aspect_type} {aspect.planet2.value} (orb: {aspect.orb:.1f}°)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Demo 2: Modern Person with Different House System
    print("\n\n🎯 Demo 2: Modern Birth Chart (Koch House System)")
    print("-" * 50)
    
    modern_request = BirthChartRequest(
        name="Demo Person",
        birth_date="1990-07-15",
        birth_time="15:30",
        latitude=34.0522,  # Los Angeles
        longitude=-118.2437,
        timezone="America/Los_Angeles",
        house_system=HouseSystem.KOCH
    )
    
    try:
        chart2 = birth_chart_service.generate_birth_chart(modern_request)
        print(f"✅ Successfully generated chart for {chart2.name}")
        print(f"🏠 House System: {chart2.house_system}")
        print(f"🌟 Sun Sign: {chart2.chart_summary['sun_sign']}")
        print(f"🌙 Moon Sign: {chart2.chart_summary['moon_sign']}")
        print(f"⬆️ Ascendant: {chart2.chart_summary['ascendant_sign']}")
        
        # Show house cusps
        print("\n🏠 House Cusps:")
        for house in chart2.houses[:6]:  # Show first 6 houses
            print(f"  House {house.number}: {house.cusp:.1f}° {house.sign.value} (ruled by {house.ruler.value})")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Demo 3: API Response Format
    print("\n\n🎯 Demo 3: JSON API Response Format")
    print("-" * 40)
    
    # Create a sample response for JSON serialization
    sample_request = BirthChartRequest(
        name="API Sample",
        birth_date="2000-01-01",
        birth_time="12:00",
        latitude=40.7128,
        longitude=-74.0060,
        house_system=HouseSystem.PLACIDUS
    )
    
    try:
        chart3 = birth_chart_service.generate_birth_chart(sample_request)
        
        # Convert to dict for JSON serialization
        response_data = {
            "name": chart3.name,
            "birth_datetime": chart3.birth_datetime.isoformat(),
            "location": chart3.location,
            "julian_day": chart3.julian_day,
            "house_system": chart3.house_system.value,
            "planets": [
                {
                    "planet": p.planet.value,
                    "longitude": p.longitude,
                    "latitude": p.latitude,
                    "sign": p.sign.value,
                    "degree": p.degree,
                    "house": p.house,
                    "retrograde": p.retrograde
                } for p in chart3.planets[:3]  # Show first 3 planets
            ],
            "houses": [
                {
                    "number": h.number,
                    "cusp": h.cusp,
                    "sign": h.sign.value,
                    "ruler": h.ruler.value
                } for h in chart3.houses[:3]  # Show first 3 houses
            ],
            "aspects": [
                {
                    "planet1": a.planet1.value,
                    "planet2": a.planet2.value,
                    "aspect_type": a.aspect_type,
                    "angle": a.angle,
                    "orb": a.orb,
                    "applying": a.applying
                } for a in chart3.aspects[:3]  # Show first 3 aspects
            ],
            "chart_summary": chart3.chart_summary
        }
        
        print("✅ Sample JSON Response (first 3 planets/houses/aspects):")
        print(json.dumps(response_data, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Demo 4: Different House Systems Comparison
    print("\n\n🎯 Demo 4: House System Comparison")
    print("-" * 40)
    
    base_request = BirthChartRequest(
        name="House System Demo",
        birth_date="1985-06-21",
        birth_time="10:00",
        latitude=51.5074,  # London
        longitude=-0.1278,
        timezone="Europe/London"
    )
    
    house_systems = [HouseSystem.PLACIDUS, HouseSystem.KOCH, HouseSystem.EQUAL]
    
    for system in house_systems:
        try:
            base_request.house_system = system
            chart = birth_chart_service.generate_birth_chart(base_request)
            
            print(f"\n{system.value} House System:")
            print(f"  Ascendant: {chart.chart_summary['ascendant_sign']}")
            print(f"  1st House: {chart.houses[0].cusp:.1f}° {chart.houses[0].sign.value}")
            print(f"  10th House: {chart.houses[9].cusp:.1f}° {chart.houses[9].sign.value}")
            
        except Exception as e:
            print(f"❌ Error with {system.value}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 API Demo Complete!")
    print("\nThe Starlight Astrology API provides:")
    print("✨ Comprehensive birth chart generation")
    print("🪐 Accurate planetary positions using Swiss Ephemeris")
    print("🏠 Multiple house systems (Placidus, Koch, Equal, Whole Sign)")
    print("🔄 Planetary aspects with orbs")
    print("📊 Chart summaries and interpretations")
    print("🌍 Timezone and location handling")
    print("📱 JSON API responses ready for web/mobile apps")
    
    print("\n🚀 Ready to integrate with your frontend!")
    print("API Documentation: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = demo_birth_chart_api()
    
    if success:
        print("\n🌟 All demos completed successfully!")
    else:
        print("\n❌ Some demos failed.")
        sys.exit(1) 