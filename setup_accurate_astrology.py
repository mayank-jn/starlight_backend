#!/usr/bin/env python3
"""
Setup Accurate Astrology System
Downloads Swiss Ephemeris data and verifies calculations
"""

import os
import requests
import gzip
import shutil
from pathlib import Path
import swisseph as swe
from datetime import datetime
import pytz

class AstrologyAccuracySetup:
    """Setup and verify accurate astrology calculations."""
    
    def __init__(self):
        self.ephemeris_dir = Path("./swisseph_data")
        self.ephemeris_files = [
            'sepl_18.se1',  # Main planetary ephemeris
            'semo_18.se1',  # Moon ephemeris  
            'seas_18.se1',  # Asteroid ephemeris
        ]
        self.base_url = "https://www.astro.com/ftp/swisseph/ephe/"
    
    def create_ephemeris_directory(self):
        """Create directory for ephemeris files."""
        self.ephemeris_dir.mkdir(exist_ok=True)
        print(f"📁 Created ephemeris directory: {self.ephemeris_dir}")
    
    def download_ephemeris_file(self, filename: str) -> bool:
        """Download a specific ephemeris file."""
        url = f"{self.base_url}{filename}"
        file_path = self.ephemeris_dir / filename
        
        if file_path.exists():
            print(f"✅ {filename} already exists")
            return True
        
        try:
            print(f"⬇️  Downloading {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            print(f"✅ Downloaded {filename} ({file_path.stat().st_size / 1024:.1f} KB)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            return False
    
    def download_all_ephemeris_files(self):
        """Download all required ephemeris files."""
        print("🌟 Downloading Swiss Ephemeris Data Files")
        print("=" * 50)
        
        self.create_ephemeris_directory()
        
        success_count = 0
        for filename in self.ephemeris_files:
            if self.download_ephemeris_file(filename):
                success_count += 1
        
        print(f"\n✅ Downloaded {success_count}/{len(self.ephemeris_files)} files")
        return success_count == len(self.ephemeris_files)
    
    def setup_swisseph(self):
        """Configure Swiss Ephemeris with downloaded data."""
        if self.ephemeris_dir.exists():
            swe.set_ephe_path(str(self.ephemeris_dir))
            print(f"✅ Swiss Ephemeris path set to: {self.ephemeris_dir}")
            return True
        else:
            print("❌ Ephemeris directory not found")
            return False
    
    def test_planetary_calculation(self, julian_day: float = 2451545.0):
        """Test planetary calculations with current setup."""
        print("\n🧪 Testing Planetary Calculations")
        print("=" * 40)
        
        planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Rahu': swe.TRUE_NODE
        }
        
        successful_calculations = 0
        
        for planet_name, planet_id in planets.items():
            try:
                result = swe.calc_ut(julian_day, planet_id, swe.FLG_SWIEPH)
                
                if result[1] == 0:  # No error
                    longitude = result[0][0]
                    print(f"✅ {planet_name}: {longitude:.6f}°")
                    successful_calculations += 1
                else:
                    print(f"❌ {planet_name}: Error {result[1]}")
                    
            except Exception as e:
                print(f"❌ {planet_name}: Exception {e}")
        
        accuracy_percentage = (successful_calculations / len(planets)) * 100
        print(f"\n📊 Calculation Success Rate: {accuracy_percentage:.1f}%")
        
        return successful_calculations == len(planets)
    
    def test_house_calculation(self):
        """Test house calculations."""
        print("\n🏠 Testing House Calculations")
        print("=" * 40)
        
        # Test coordinates: New York City
        julian_day = 2451545.0  # J2000.0
        latitude = 40.7128
        longitude = -74.0060
        
        house_systems = {
            'Placidus': b'P',
            'Koch': b'K',
            'Equal': b'E',
            'Whole Sign': b'W'
        }
        
        for system_name, system_code in house_systems.items():
            try:
                houses_data = swe.houses(julian_day, latitude, longitude, system_code)
                house_cusps = houses_data[0][:12]
                ascendant = houses_data[1][0]
                
                print(f"✅ {system_name}: ASC {ascendant:.2f}°, Houses OK")
                
            except Exception as e:
                print(f"❌ {system_name}: {e}")
    
    def compare_calculations(self):
        """Compare calculations with and without ephemeris files."""
        print("\n⚖️  Comparing Calculation Methods")
        print("=" * 50)
        
        julian_day = 2451545.0  # J2000.0
        
        # Test with downloaded ephemeris
        if self.ephemeris_dir.exists():
            swe.set_ephe_path(str(self.ephemeris_dir))
            result_with_files = swe.calc_ut(julian_day, swe.SUN, swe.FLG_SWIEPH)
            print(f"📁 With ephemeris files: Sun at {result_with_files[0][0]:.6f}°")
        
        # Test with built-in data
        swe.set_ephe_path("")  # Use built-in
        result_builtin = swe.calc_ut(julian_day, swe.SUN, swe.FLG_SWIEPH)
        print(f"💾 Built-in data: Sun at {result_builtin[0][0]:.6f}°")
        
        # Calculate difference
        if self.ephemeris_dir.exists():
            difference = abs(result_with_files[0][0] - result_builtin[0][0])
            print(f"📏 Difference: {difference:.6f}° ({difference * 3600:.1f} arcseconds)")
            
            if difference < 0.001:  # Less than 3.6 arcseconds
                print("✅ Excellent agreement between methods")
            elif difference < 0.01:  # Less than 36 arcseconds  
                print("✅ Good agreement between methods")
            else:
                print("⚠️  Significant difference - ephemeris files recommended")
    
    def generate_test_chart(self):
        """Generate a test chart with maximum accuracy."""
        print("\n🌟 Generating Test Birth Chart")
        print("=" * 40)
        
        # Use a well-known birth chart for verification
        # Albert Einstein: March 14, 1879, 11:30 AM, Ulm, Germany
        
        # Parse birth data
        birth_date = "1879-03-14"
        birth_time = "11:30"
        timezone_str = "Europe/Berlin"
        latitude = 48.3984  # Ulm, Germany
        longitude = 9.9916
        
        # Calculate Julian Day with timezone
        dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
        tz = pytz.timezone(timezone_str)
        dt = tz.localize(dt)
        dt_utc = dt.astimezone(pytz.UTC)
        julian_day = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                               dt_utc.hour + dt_utc.minute / 60.0)
        
        print(f"👤 Subject: Albert Einstein")
        print(f"📅 Birth: {birth_date} {birth_time} {timezone_str}")
        print(f"📍 Location: {latitude}°N, {longitude}°E")
        print(f"⏰ Julian Day: {julian_day:.6f}")
        
        # Calculate with ephemeris files if available
        if self.ephemeris_dir.exists():
            swe.set_ephe_path(str(self.ephemeris_dir))
            print("📁 Using downloaded ephemeris files")
        else:
            print("💾 Using built-in ephemeris data")
        
        # Calculate Lahiri Ayanamsa
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(julian_day)
        print(f"🔄 Lahiri Ayanamsa: {ayanamsa:.6f}°")
        
        # Calculate houses (Placidus system)
        houses_data = swe.houses(julian_day, latitude, longitude, b'P')
        house_cusps = houses_data[0][:12]
        ascendant = houses_data[1][0]
        midheaven = houses_data[1][1]
        
        # Apply ayanamsa correction for Vedic
        asc_vedic = (ascendant - ayanamsa) % 360
        mc_vedic = (midheaven - ayanamsa) % 360
        
        print(f"🏠 Ascendant (Vedic): {asc_vedic:.2f}° ({self.get_sign(asc_vedic)})")
        print(f"🏠 Midheaven (Vedic): {mc_vedic:.2f}° ({self.get_sign(mc_vedic)})")
        
        # Calculate key planets
        planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        planet_ids = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN]
        
        print("\n🪐 Planetary Positions (Vedic):")
        for planet_name, planet_id in zip(planets, planet_ids):
            try:
                result = swe.calc_ut(julian_day, planet_id, swe.FLG_SWIEPH)
                if result[1] == 0:
                    longitude = result[0][0]
                    vedic_longitude = (longitude - ayanamsa) % 360
                    sign = self.get_sign(vedic_longitude)
                    degree = vedic_longitude % 30
                    print(f"   {planet_name}: {degree:.2f}° {sign}")
                else:
                    print(f"   {planet_name}: Calculation error {result[1]}")
            except Exception as e:
                print(f"   {planet_name}: Exception {e}")
    
    def get_sign(self, longitude: float) -> str:
        """Get zodiac sign from longitude."""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_num = int(longitude / 30) % 12
        return signs[sign_num]
    
    def create_accuracy_report(self):
        """Create a comprehensive accuracy report."""
        print("\n📋 ASTROLOGY ACCURACY REPORT")
        print("=" * 60)
        
        # Check ephemeris setup
        ephemeris_available = self.ephemeris_dir.exists() and any(self.ephemeris_dir.iterdir())
        print(f"Swiss Ephemeris Files: {'✅ Available' if ephemeris_available else '❌ Missing'}")
        
        # Test calculations
        calc_success = self.test_planetary_calculation()
        print(f"Planetary Calculations: {'✅ Working' if calc_success else '❌ Failed'}")
        
        # Test houses
        self.test_house_calculation()
        
        # Overall assessment
        if ephemeris_available and calc_success:
            print("\n🎯 ACCURACY LEVEL: EXCELLENT")
            print("   • Swiss Ephemeris data files available")
            print("   • All calculations working correctly")
            print("   • Maximum precision achieved")
        elif calc_success:
            print("\n⚠️  ACCURACY LEVEL: GOOD")
            print("   • Using built-in ephemeris data")
            print("   • Calculations working correctly")
            print("   • Consider downloading ephemeris files for maximum accuracy")
        else:
            print("\n❌ ACCURACY LEVEL: POOR")
            print("   • Calculation errors detected")
            print("   • System configuration required")
        
        return ephemeris_available and calc_success

def main():
    """Main setup and testing function."""
    setup = AstrologyAccuracySetup()
    
    # Download ephemeris files
    setup.download_all_ephemeris_files()
    
    # Setup Swiss Ephemeris
    setup.setup_swisseph()
    
    # Run tests
    setup.create_accuracy_report()
    
    # Generate test chart
    setup.generate_test_chart()
    
    # Compare methods
    setup.compare_calculations()

if __name__ == "__main__":
    main() 