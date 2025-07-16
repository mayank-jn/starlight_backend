#!/usr/bin/env python3
"""Test script for Prokerala birth chart generation"""

from datetime import datetime
from app.models import BirthChartRequest
from app.services.prokerala_service import prokerala_service

def test_birth_chart():
    """Test birth chart generation"""
    try:
        # Create a test request
        request = BirthChartRequest(
            name="Test User",
            birth_date="2000-01-01",
            birth_time="12:00",
            latitude=12.9716,  # Bangalore
            longitude=77.5946,
            timezone="Asia/Kolkata"
        )
        
        # Force debug mode
        prokerala_service.debug = True
        
        # Try to generate birth chart
        response = prokerala_service.generate_birth_chart(request)
        print("\nSuccess! Got birth chart response.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_birth_chart() 