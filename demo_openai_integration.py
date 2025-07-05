#!/usr/bin/env python3
"""
Demo script for OpenAI integration in Starlight Astrology API.
This script demonstrates how the AI-powered detailed reports work.
"""

import os
import json
from dotenv import load_dotenv
from app.services.birth_chart import BirthChartService
from app.models import DetailedReportRequest, HouseSystem, AyanamsaSystem

# Load environment variables
load_dotenv()

def demo_openai_integration():
    """Demonstrate OpenAI integration with detailed astrological reports."""
    
    print("🤖 OpenAI Integration Demo - Starlight Astrology API")
    print("=" * 60)
    
    # Check if OpenAI is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured!")
        print("Please set OPENAI_API_KEY in your .env file")
        print("See OPENAI_SETUP.md for instructions")
        return False
    
    print(f"✅ OpenAI API key configured: {api_key[:10]}...")
    print(f"📄 OpenAI Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    print(f"🤖 AI Reports Enabled: {os.getenv('USE_AI_REPORTS', 'true')}")
    print()
    
    # Initialize the service
    service = BirthChartService()
    
    # Check if OpenAI service is available
    if not service.openai_service.is_available():
        print("❌ OpenAI service not available!")
        print("Will demonstrate fallback to template-based reports")
        print()
    else:
        print("✅ OpenAI service available and ready!")
        print()
    
    # Demo with Albert Einstein's birth data
    print("🎯 Demo: Generating detailed report for Albert Einstein")
    print("-" * 50)
    
    request = DetailedReportRequest(
        name="Albert Einstein",
        birth_date="1879-03-14",
        birth_time="11:30",
        latitude=48.3969,
        longitude=9.9918,
        timezone="Europe/Berlin",
        house_system=HouseSystem.PLACIDUS,
        ayanamsa=AyanamsaSystem.LAHIRI
    )
    
    try:
        print("📊 Generating birth chart...")
        report = service.generate_detailed_report(request)
        print("✅ Report generated successfully!")
        print()
        
        # Display report sections
        print("📋 Generated Report Sections:")
        print("-" * 30)
        
        # Personality Report
        print("🧠 PERSONALITY ANALYSIS:")
        personality = report.personality_report
        for section_key, section_data in personality.items():
            if isinstance(section_data, dict) and 'title' in section_data:
                print(f"  • {section_data['title']}")
                print(f"    {section_data['description'][:100]}...")
                print()
        
        # Career Report
        print("💼 CAREER ANALYSIS:")
        career = report.career_report
        for section_key, section_data in career.items():
            if isinstance(section_data, dict) and 'title' in section_data:
                print(f"  • {section_data['title']}")
                print(f"    {section_data['description'][:100]}...")
                print()
        
        # Relationship Report
        print("❤️ RELATIONSHIP ANALYSIS:")
        relationship = report.relationship_report
        for section_key, section_data in relationship.items():
            if isinstance(section_data, dict) and 'title' in section_data:
                print(f"  • {section_data['title']}")
                print(f"    {section_data['description'][:100]}...")
                print()
        
        # Health Report
        print("🏥 HEALTH ANALYSIS:")
        health = report.health_report
        for section_key, section_data in health.items():
            if isinstance(section_data, dict) and 'title' in section_data:
                print(f"  • {section_data['title']}")
                print(f"    {section_data['description'][:100]}...")
                print()
        
        # Spiritual Report
        print("🕉️ SPIRITUAL ANALYSIS:")
        spiritual = report.spiritual_report
        for section_key, section_data in spiritual.items():
            if isinstance(section_data, dict) and 'title' in section_data:
                print(f"  • {section_data['title']}")
                print(f"    {section_data['description'][:100]}...")
                print()
        
        # Show birth chart summary
        print("📊 BIRTH CHART SUMMARY:")
        print(f"  • Sun Sign: {report.birth_chart.chart_summary.get('sun_sign', 'Unknown')}")
        print(f"  • Moon Sign: {report.birth_chart.chart_summary.get('moon_sign', 'Unknown')}")
        print(f"  • Ascendant: {report.birth_chart.chart_summary.get('ascendant_sign', 'Unknown')}")
        print(f"  • Ayanamsa: {report.birth_chart.ayanamsa_value:.2f}°")
        print(f"  • House System: {report.birth_chart.house_system.value}")
        print()
        
        # Check if this was AI-generated or template-based
        is_ai_generated = service.openai_service.is_available()
        print(f"🤖 Report Type: {'AI-Generated' if is_ai_generated else 'Template-Based'}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        return False

def demo_comparison():
    """Demonstrate the difference between AI and template-based reports."""
    
    print("\n🔍 Comparison Demo: AI vs Template-Based Reports")
    print("=" * 60)
    
    service = BirthChartService()
    
    # Test data
    request = DetailedReportRequest(
        name="Demo Person",
        birth_date="1990-06-15",
        birth_time="12:00",
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York"
    )
    
    try:
        # Generate birth chart
        birth_chart_request = service.generate_detailed_report(request)
        
        # Show the difference
        if service.openai_service.is_available():
            print("✨ AI-Generated Report Features:")
            print("  • Unique content for each birth chart")
            print("  • Contextual references to specific planetary positions")
            print("  • Personalized insights and recommendations")
            print("  • Natural language flow and coherence")
            print("  • Traditional Vedic astrology interpretations")
            print()
        else:
            print("📝 Template-Based Report Features:")
            print("  • Consistent structure and format")
            print("  • Pre-written interpretations")
            print("  • Sign-based generalizations")
            print("  • Reliable fallback system")
            print("  • Fast response times")
            print()
            
    except Exception as e:
        print(f"❌ Error in comparison demo: {str(e)}")

def main():
    """Main demo function."""
    
    success = demo_openai_integration()
    
    if success:
        demo_comparison()
        
        print("\n🎉 OpenAI Integration Demo Complete!")
        print("=" * 60)
        print("✅ Your Starlight Astrology API now includes:")
        print("  • AI-powered detailed report generation")
        print("  • Personalized astrological insights")
        print("  • Comprehensive 5-section analysis")
        print("  • Graceful fallback system")
        print("  • Traditional Vedic astrology wisdom")
        print()
        print("🚀 Ready to generate amazing astrological reports!")
        print("📖 See OPENAI_SETUP.md for configuration details")
        print("🌐 API Documentation: http://localhost:8000/docs")
        
    else:
        print("\n❌ Demo failed - please check your configuration")
        print("📖 See OPENAI_SETUP.md for troubleshooting")

if __name__ == "__main__":
    main() 