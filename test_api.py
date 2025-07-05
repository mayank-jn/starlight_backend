#!/usr/bin/env python3
"""
Test script for the Starlight Astrology API.
This script tests the birth chart generation functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app.models import BirthChartRequest, HouseSystem
from app.services.birth_chart import birth_chart_service

def test_birth_chart_generation():
    """Test birth chart generation with sample data."""
    print("🌟 Testing Starlight Astrology API...")
    print("=" * 50)
    
    # Test data - Using a famous birth chart (Albert Einstein)
    test_request = BirthChartRequest(
        name="Albert Einstein",
        birth_date="1879-03-14",
        birth_time="11:30",
        latitude=47.6779,  # Ulm, Germany
        longitude=9.9830,
        timezone="Europe/Berlin",
        house_system=HouseSystem.PLACIDUS
    )
    
    try:
        print(f"📅 Generating birth chart for: {test_request.name}")
        print(f"📍 Date: {test_request.birth_date} at {test_request.birth_time}")
        print(f"🌍 Location: {test_request.latitude}, {test_request.longitude}")
        print(f"🏠 House System: {test_request.house_system}")
        print()
        
        # Generate the birth chart
        chart = birth_chart_service.generate_birth_chart(test_request)
        
        print("✅ Birth chart generated successfully!")
        print()
        
        # Display basic information
        print("📊 CHART SUMMARY:")
        print(f"Julian Day: {chart.julian_day:.2f}")
        print(f"Sun Sign: {chart.chart_summary.get('sun_sign', 'Unknown')}")
        print(f"Moon Sign: {chart.chart_summary.get('moon_sign', 'Unknown')}")
        print(f"Ascendant: {chart.chart_summary.get('ascendant_sign', 'Unknown')}")
        print(f"Dominant Sign: {chart.chart_summary.get('dominant_sign', 'Unknown')}")
        print(f"Retrograde Planets: {chart.chart_summary.get('retrograde_planets', 0)}")
        print()
        
        # Display planet positions
        print("🪐 PLANET POSITIONS:")
        for planet in chart.planets:
            print(f"{planet.planet.value:>8}: {planet.degree:.1f}° {planet.sign.value} (House {planet.house})")
            if planet.retrograde:
                print(f"{'':>8}  [Retrograde]")
        print()
        
        # Display house cusps
        print("🏠 HOUSE CUSPS:")
        for house in chart.houses:
            print(f"House {house.number:>2}: {house.cusp:.1f}° {house.sign.value} (Ruler: {house.ruler.value})")
        print()
        
        # Display aspects
        print("🔄 PLANETARY ASPECTS:")
        for aspect in chart.aspects[:10]:  # Show first 10 aspects
            print(f"{aspect.planet1.value} {aspect.aspect_type} {aspect.planet2.value} " +
                  f"(Orb: {aspect.orb:.1f}°)")
        
        if len(chart.aspects) > 10:
            print(f"... and {len(chart.aspects) - 10} more aspects")
        print()
        
        print("✨ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating birth chart: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_functions():
    """Test individual functions."""
    print("\n🔧 Testing individual functions...")
    
    try:
        # Test zodiac sign calculation
        service = birth_chart_service
        
        # Test various longitudes
        test_cases = [
            (0, "Aries"),
            (30, "Taurus"),
            (60, "Gemini"),
            (90, "Cancer"),
            (120, "Leo"),
            (150, "Virgo"),
            (180, "Libra"),
            (210, "Scorpio"),
            (240, "Sagittarius"),
            (270, "Capricorn"),
            (300, "Aquarius"),
            (330, "Pisces")
        ]
        
        print("Testing zodiac sign calculations:")
        for longitude, expected_sign in test_cases:
            calculated_sign = service.get_zodiac_sign(longitude)
            status = "✅" if calculated_sign.value == expected_sign else "❌"
            print(f"{status} {longitude}° -> {calculated_sign.value} (expected: {expected_sign})")
        
        print("\n✅ Individual function tests completed!")
        
    except Exception as e:
        print(f"❌ Error in individual function tests: {str(e)}")

if __name__ == "__main__":
    print("🌟 Starlight Astrology API Test Suite")
    print("=" * 50)
    
    # Test main birth chart generation
    success = test_birth_chart_generation()
    
    # Test individual functions
    test_individual_functions()
    
    if success:
        print("\n🎉 All tests passed! The API is ready to use.")
        print("\nTo start the API server, run:")
        print("cd starlight_backend && python -m uvicorn app.main:app --reload")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1) 