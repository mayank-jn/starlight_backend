#!/usr/bin/env python3
"""
Enhanced Accurate Birth Chart Calculator
Addresses timezone, house calculation, and validation issues
"""

import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any
import math
import pytz
import os
import json
from pathlib import Path

class AccurateBirthChart:
    """Enhanced birth chart calculator with improved accuracy."""
    
    def __init__(self):
        """Initialize with proper Swiss Ephemeris setup."""
        # Set ephemeris path - critical for accuracy
        self.setup_ephemeris()
        
        # Planet constants with additional accuracy checks
        self.PLANETS = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Uranus': swe.URANUS,
            'Neptune': swe.NEPTUNE,
            'Pluto': swe.PLUTO,
            'Rahu': swe.TRUE_NODE,  # More accurate than mean node
        }
        
        # House systems with proper encoding
        self.HOUSE_SYSTEMS = {
            'Placidus': b'P',
            'Koch': b'K', 
            'Equal': b'E',
            'Whole Sign': b'W',
            'Campanus': b'C',
            'Regiomontanus': b'R'
        }
        
        # Accurate Ayanamsa systems
        self.AYANAMSAS = {
            'Lahiri': swe.SIDM_LAHIRI,
            'Raman': swe.SIDM_RAMAN,
            'Krishnamurti': swe.SIDM_KRISHNAMURTI,
            'Yukteshwar': swe.SIDM_YUKTESHWAR,
            'JN_Bhasin': swe.SIDM_JN_BHASIN
        }
        
        # Zodiac signs
        self.SIGNS = [
            'Aries', 'Taurus', 'Gemini', 'Cancer',
            'Leo', 'Virgo', 'Libra', 'Scorpio', 
            'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
    
    def setup_ephemeris(self):
        """Setup Swiss Ephemeris with proper data files."""
        # Try to set ephemeris path
        possible_paths = [
            '/usr/share/swisseph',
            '/usr/local/share/swisseph',
            './swisseph',
            os.path.expanduser('~/swisseph'),
            '/opt/swisseph'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                swe.set_ephe_path(path)
                print(f"✅ Swiss Ephemeris path set to: {path}")
                return
        
        print("⚠️  Swiss Ephemeris data files not found. Using built-in data.")
        print("   For maximum accuracy, download Swiss Ephemeris data files")
    
    def validate_input(self, birth_date: str, birth_time: str, 
                      latitude: float, longitude: float, timezone_str: str = None) -> Dict[str, Any]:
        """Comprehensive input validation with detailed error reporting."""
        errors = []
        warnings = []
        
        # Validate date format
        try:
            date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
            if date_obj.year < 1900 or date_obj.year > 2100:
                warnings.append(f"Date {birth_date} is outside optimal range (1900-2100)")
        except ValueError:
            errors.append(f"Invalid date format: {birth_date}. Use YYYY-MM-DD")
        
        # Validate time format
        try:
            time_obj = datetime.strptime(birth_time, '%H:%M')
        except ValueError:
            errors.append(f"Invalid time format: {birth_time}. Use HH:MM (24-hour)")
        
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            errors.append(f"Invalid latitude: {latitude}. Must be between -90 and +90")
        if not (-180 <= longitude <= 180):
            errors.append(f"Invalid longitude: {longitude}. Must be between -180 and +180")
        
        # Validate timezone
        if timezone_str:
            try:
                pytz.timezone(timezone_str)
            except pytz.exceptions.UnknownTimeZoneError:
                errors.append(f"Invalid timezone: {timezone_str}")
        else:
            warnings.append("No timezone specified. Assuming UTC")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def calculate_accurate_julian_day(self, birth_date: str, birth_time: str, 
                                    timezone_str: Optional[str] = None) -> float:
        """Calculate Julian Day with enhanced accuracy and error handling."""
        
        # Parse date and time
        dt_str = f"{birth_date} {birth_time}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        
        # Handle timezone with proper error checking
        if timezone_str:
            try:
                tz = pytz.timezone(timezone_str)
                # Localize to specified timezone
                dt = tz.localize(dt)
                # Convert to UTC for calculations
                dt_utc = dt.astimezone(pytz.UTC)
                print(f"✅ Timezone conversion: {dt} → {dt_utc} UTC")
            except pytz.exceptions.UnknownTimeZoneError:
                raise ValueError(f"Invalid timezone: {timezone_str}")
            except pytz.exceptions.AmbiguousTimeError:
                # Handle daylight saving time ambiguity
                dt = tz.localize(dt, is_dst=False)  # Use standard time
                dt_utc = dt.astimezone(pytz.UTC)
                print(f"⚠️  Ambiguous time resolved to standard time: {dt_utc} UTC")
            except pytz.exceptions.NonExistentTimeError:
                # Handle daylight saving time gap
                dt = tz.localize(dt, is_dst=True)  # Use daylight time
                dt_utc = dt.astimezone(pytz.UTC)
                print(f"⚠️  Non-existent time resolved to daylight time: {dt_utc} UTC")
        else:
            # Assume UTC if no timezone specified
            dt_utc = dt.replace(tzinfo=pytz.UTC)
            print(f"⚠️  No timezone specified, assuming UTC: {dt_utc}")
        
        # Calculate Julian Day with high precision
        jd = swe.julday(
            dt_utc.year, 
            dt_utc.month, 
            dt_utc.day, 
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        )
        
        print(f"📅 Julian Day: {jd:.6f}")
        return jd
    
    def calculate_accurate_ayanamsa(self, julian_day: float, ayanamsa_system: str = 'Lahiri') -> float:
        """Calculate ayanamsa with validation and multiple systems."""
        
        if ayanamsa_system not in self.AYANAMSAS:
            raise ValueError(f"Unsupported ayanamsa system: {ayanamsa_system}")
        
        # Set ayanamsa system
        swe.set_sid_mode(self.AYANAMSAS[ayanamsa_system])
        
        # Calculate ayanamsa value
        ayanamsa_value = swe.get_ayanamsa(julian_day)
        
        print(f"🔄 Ayanamsa ({ayanamsa_system}): {ayanamsa_value:.6f}°")
        return ayanamsa_value
    
    def calculate_accurate_houses(self, julian_day: float, latitude: float, longitude: float,
                                house_system: str = 'Placidus', ayanamsa_value: float = 0) -> Dict[str, Any]:
        """Calculate house cusps with enhanced accuracy."""
        
        if house_system not in self.HOUSE_SYSTEMS:
            raise ValueError(f"Unsupported house system: {house_system}")
        
        # Calculate houses using Swiss Ephemeris
        system_code = self.HOUSE_SYSTEMS[house_system]
        houses_data = swe.houses(julian_day, latitude, longitude, system_code)
        
        house_cusps = houses_data[0][:12]  # 12 house cusps
        ascmc = houses_data[1]  # Ascendant, MC, etc.
        
        # Apply ayanamsa correction for sidereal calculations
        corrected_cusps = []
        for cusp in house_cusps:
            corrected_cusp = (cusp - ayanamsa_value) % 360
            corrected_cusps.append(corrected_cusp)
        
        # Calculate house information
        houses = []
        for i, cusp in enumerate(corrected_cusps):
            sign_num = int(cusp / 30)
            sign = self.SIGNS[sign_num]
            degree_in_sign = cusp % 30
            
            houses.append({
                'house': i + 1,
                'cusp_longitude': cusp,
                'sign': sign,
                'degree': degree_in_sign,
                'sign_degree': f"{degree_in_sign:.2f}° {sign}"
            })
        
        # Calculate Ascendant and MC with ayanamsa correction
        ascendant = (ascmc[0] - ayanamsa_value) % 360
        midheaven = (ascmc[1] - ayanamsa_value) % 360
        
        return {
            'houses': houses,
            'house_cusps': corrected_cusps,
            'ascendant': ascendant,
            'midheaven': midheaven,
            'ascendant_sign': self.get_sign_from_longitude(ascendant),
            'mc_sign': self.get_sign_from_longitude(midheaven)
        }
    
    def calculate_accurate_planets(self, julian_day: float, house_cusps: List[float], 
                                 ayanamsa_value: float = 0) -> List[Dict[str, Any]]:
        """Calculate planetary positions with enhanced accuracy."""
        
        planets = []
        
        for planet_name, planet_id in self.PLANETS.items():
            try:
                # Calculate planetary position
                result = swe.calc_ut(julian_day, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
                
                if result[1] == 0:  # No error
                    longitude = result[0][0]
                    latitude = result[0][1]
                    distance = result[0][2]
                    speed_lon = result[0][3]
                    speed_lat = result[0][4]
                    speed_dist = result[0][5]
                    
                    # Apply ayanamsa correction for sidereal
                    sidereal_longitude = (longitude - ayanamsa_value) % 360
                    
                    # Calculate sign and degree
                    sign = self.get_sign_from_longitude(sidereal_longitude)
                    degree_in_sign = sidereal_longitude % 30
                    
                    # Calculate house placement with improved logic
                    house = self.get_accurate_house_placement(sidereal_longitude, house_cusps)
                    
                    # Determine if retrograde
                    is_retrograde = speed_lon < 0
                    
                    planet_data = {
                        'planet': planet_name,
                        'longitude': sidereal_longitude,
                        'latitude': latitude,
                        'distance': distance,
                        'speed': speed_lon,
                        'sign': sign,
                        'degree_in_sign': degree_in_sign,
                        'house': house,
                        'retrograde': is_retrograde,
                        'sign_degree': f"{degree_in_sign:.2f}° {sign}",
                        'house_position': f"House {house}"
                    }
                    
                    planets.append(planet_data)
                    
                    # Handle Ketu (South Node) for Rahu
                    if planet_name == 'Rahu':
                        ketu_longitude = (sidereal_longitude + 180) % 360
                        ketu_sign = self.get_sign_from_longitude(ketu_longitude)
                        ketu_degree = ketu_longitude % 30
                        ketu_house = self.get_accurate_house_placement(ketu_longitude, house_cusps)
                        
                        planets.append({
                            'planet': 'Ketu',
                            'longitude': ketu_longitude,
                            'latitude': -latitude,
                            'distance': distance,
                            'speed': -speed_lon,
                            'sign': ketu_sign,
                            'degree_in_sign': ketu_degree,
                            'house': ketu_house,
                            'retrograde': True,  # Ketu is always retrograde
                            'sign_degree': f"{ketu_degree:.2f}° {ketu_sign}",
                            'house_position': f"House {ketu_house}"
                        })
                    
                else:
                    print(f"❌ Error calculating {planet_name}: {result[1]}")
                    
            except Exception as e:
                print(f"❌ Exception calculating {planet_name}: {e}")
        
        return planets
    
    def get_sign_from_longitude(self, longitude: float) -> str:
        """Get zodiac sign from longitude."""
        sign_num = int(longitude / 30) % 12
        return self.SIGNS[sign_num]
    
    def get_accurate_house_placement(self, longitude: float, house_cusps: List[float]) -> int:
        """Accurately determine house placement with proper wraparound handling."""
        
        # Normalize longitude to 0-360
        longitude = longitude % 360
        
        # Check each house
        for i in range(12):
            cusp_current = house_cusps[i] % 360
            cusp_next = house_cusps[(i + 1) % 12] % 360
            
            # Handle wraparound at 0/360 degrees
            if cusp_current > cusp_next:  # Crosses 0° (like 350° to 10°)
                if longitude >= cusp_current or longitude < cusp_next:
                    return i + 1
            else:  # Normal case
                if cusp_current <= longitude < cusp_next:
                    return i + 1
        
        # Fallback to first house
        return 1
    
    def generate_accurate_birth_chart(self, birth_date: str, birth_time: str,
                                    latitude: float, longitude: float,
                                    timezone_str: str = None,
                                    house_system: str = 'Placidus',
                                    ayanamsa_system: str = 'Lahiri',
                                    astrology_system: str = 'Vedic') -> Dict[str, Any]:
        """Generate a highly accurate birth chart."""
        
        print("🌟 Generating Accurate Birth Chart")
        print("=" * 50)
        
        # Validate input
        validation = self.validate_input(birth_date, birth_time, latitude, longitude, timezone_str)
        if not validation['valid']:
            raise ValueError(f"Input validation failed: {validation['errors']}")
        
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"⚠️  {warning}")
        
        try:
            # Calculate Julian Day
            julian_day = self.calculate_accurate_julian_day(birth_date, birth_time, timezone_str)
            
            # Calculate Ayanamsa (for Vedic astrology)
            ayanamsa_value = 0
            if astrology_system.lower() == 'vedic':
                ayanamsa_value = self.calculate_accurate_ayanamsa(julian_day, ayanamsa_system)
            
            # Calculate Houses
            house_data = self.calculate_accurate_houses(julian_day, latitude, longitude, house_system, ayanamsa_value)
            
            # Calculate Planets
            planets = self.calculate_accurate_planets(julian_day, house_data['house_cusps'], ayanamsa_value)
            
            # Create comprehensive result
            chart = {
                'birth_info': {
                    'date': birth_date,
                    'time': birth_time,
                    'timezone': timezone_str or 'UTC',
                    'latitude': latitude,
                    'longitude': longitude,
                    'julian_day': julian_day
                },
                'calculation_info': {
                    'astrology_system': astrology_system,
                    'house_system': house_system,
                    'ayanamsa_system': ayanamsa_system if astrology_system.lower() == 'vedic' else None,
                    'ayanamsa_value': ayanamsa_value if astrology_system.lower() == 'vedic' else None
                },
                'houses': house_data['houses'],
                'ascendant': {
                    'longitude': house_data['ascendant'],
                    'sign': house_data['ascendant_sign'],
                    'degree': house_data['ascendant'] % 30
                },
                'midheaven': {
                    'longitude': house_data['midheaven'],
                    'sign': house_data['mc_sign'],
                    'degree': house_data['midheaven'] % 30
                },
                'planets': planets,
                'validation': validation
            }
            
            print("✅ Birth chart calculated successfully!")
            print("=" * 50)
            
            return chart
            
        except Exception as e:
            print(f"❌ Error generating birth chart: {e}")
            raise

# Example usage
if __name__ == "__main__":
    calculator = AccurateBirthChart()
    
    # Test with accurate data
    chart = calculator.generate_accurate_birth_chart(
        birth_date="1990-01-15",
        birth_time="14:30",
        latitude=40.7128,
        longitude=-74.0060,
        timezone_str="America/New_York",
        house_system="Placidus",
        ayanamsa_system="Lahiri",
        astrology_system="Vedic"
    )
    
    print("\n🌟 BIRTH CHART SUMMARY")
    print("=" * 30)
    print(f"Ascendant: {chart['ascendant']['degree']:.2f}° {chart['ascendant']['sign']}")
    print(f"Midheaven: {chart['midheaven']['degree']:.2f}° {chart['midheaven']['sign']}")
    print("\n🪐 PLANETS:")
    for planet in chart['planets']:
        status = " (R)" if planet['retrograde'] else ""
        print(f"{planet['planet']}: {planet['sign_degree']} in {planet['house_position']}{status}") 