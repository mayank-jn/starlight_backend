#!/usr/bin/env python3
"""
Improved Birth Chart Service with Enhanced Accuracy
Addresses timezone, house calculation, and validation issues
"""

import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any
import pytz
import math
import traceback
from enum import Enum


class Planet(Enum):
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"
    URANUS = "Uranus"
    NEPTUNE = "Neptune"
    PLUTO = "Pluto"
    RAHU = "Rahu"
    KETU = "Ketu"


class ZodiacSign(Enum):
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"


class HouseSystem(Enum):
    PLACIDUS = "Placidus"
    KOCH = "Koch"
    EQUAL = "Equal"
    WHOLE_SIGN = "Whole Sign"
    CAMPANUS = "Campanus"
    REGIOMONTANUS = "Regiomontanus"


class AyanamsaSystem(Enum):
    LAHIRI = "Lahiri"
    RAMAN = "Raman"
    KRISHNAMURTI = "Krishnamurti"
    YUKTESHWAR = "Yukteshwar"
    JN_BHASIN = "JN_Bhasin"


class ImprovedBirthChartService:
    """Enhanced birth chart service with improved accuracy and validation."""

    def __init__(self):
        """Initialize the service with proper Swiss Ephemeris configuration."""
        
        # Enhanced planet constants
        self.PLANET_CONSTANTS = {
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
            Planet.RAHU: swe.TRUE_NODE,  # More accurate than mean node
        }
        
        # Enhanced house systems
        self.HOUSE_SYSTEMS = {
            HouseSystem.PLACIDUS: b'P',
            HouseSystem.KOCH: b'K',
            HouseSystem.EQUAL: b'E',
            HouseSystem.WHOLE_SIGN: b'W',
            HouseSystem.CAMPANUS: b'C',
            HouseSystem.REGIOMONTANUS: b'R'
        }
        
        # Enhanced ayanamsa systems
        self.AYANAMSA_SYSTEMS = {
            AyanamsaSystem.LAHIRI: swe.SIDM_LAHIRI,
            AyanamsaSystem.RAMAN: swe.SIDM_RAMAN,
            AyanamsaSystem.KRISHNAMURTI: swe.SIDM_KRISHNAMURTI,
            AyanamsaSystem.YUKTESHWAR: swe.SIDM_YUKTESHWAR,
            AyanamsaSystem.JN_BHASIN: swe.SIDM_JN_BHASIN
        }
        
        # Zodiac signs
        self.ZODIAC_SIGNS = [
            ZodiacSign.ARIES, ZodiacSign.TAURUS, ZodiacSign.GEMINI, ZodiacSign.CANCER,
            ZodiacSign.LEO, ZodiacSign.VIRGO, ZodiacSign.LIBRA, ZodiacSign.SCORPIO,
            ZodiacSign.SAGITTARIUS, ZodiacSign.CAPRICORN, ZodiacSign.AQUARIUS, ZodiacSign.PISCES
        ]
        
        # Initialize Swiss Ephemeris
        self._setup_ephemeris()
        
        print("✅ Improved Birth Chart Service initialized")

    def _setup_ephemeris(self):
        """Setup Swiss Ephemeris with best available configuration."""
        try:
            # Try to use built-in ephemeris data
            swe.set_ephe_path("")
            
            # Test if calculations work
            test_result = swe.calc_ut(2451545.0, swe.SUN, swe.FLG_SWIEPH)
            if test_result[1] == 0:
                print("✅ Swiss Ephemeris initialized with built-in data")
                self.ephemeris_available = True
            else:
                print(f"⚠️  Swiss Ephemeris test failed: Error {test_result[1]}")
                self.ephemeris_available = False
                
        except Exception as e:
            print(f"❌ Swiss Ephemeris initialization failed: {e}")
            self.ephemeris_available = False

    def validate_birth_data(self, birth_date: str, birth_time: str, 
                          latitude: float, longitude: float, 
                          timezone_str: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive validation of birth data."""
        
        errors = []
        warnings = []
        
        # Validate date format and range
        try:
            date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
            
            # Check reasonable date range
            if date_obj.year < 1800:
                warnings.append(f"Birth year {date_obj.year} is very early - accuracy may be reduced")
            elif date_obj.year > 2100:
                warnings.append(f"Birth year {date_obj.year} is far future - accuracy may be reduced")
                
        except ValueError as e:
            errors.append(f"Invalid date format '{birth_date}': {e}")
        
        # Validate time format
        try:
            time_obj = datetime.strptime(birth_time, '%H:%M')
            
        except ValueError as e:
            errors.append(f"Invalid time format '{birth_time}': {e}")
        
        # Validate coordinates
        if not isinstance(latitude, (int, float)) or not (-90 <= latitude <= 90):
            errors.append(f"Invalid latitude {latitude}: must be between -90 and +90")
            
        if not isinstance(longitude, (int, float)) or not (-180 <= longitude <= 180):
            errors.append(f"Invalid longitude {longitude}: must be between -180 and +180")
        
        # Validate timezone
        if timezone_str:
            try:
                tz = pytz.timezone(timezone_str)
                # Test timezone with the birth date to check for validity
                test_dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
                try:
                    localized_dt = tz.localize(test_dt)
                except pytz.exceptions.AmbiguousTimeError:
                    warnings.append(f"Ambiguous time due to DST - using standard time")
                except pytz.exceptions.NonExistentTimeError:
                    warnings.append(f"Non-existent time due to DST - using daylight time")
                    
            except pytz.exceptions.UnknownTimeZoneError:
                errors.append(f"Invalid timezone '{timezone_str}'")
        else:
            warnings.append("No timezone specified - assuming UTC")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def calculate_precise_julian_day(self, birth_date: str, birth_time: str, 
                                   timezone_str: Optional[str] = None) -> Tuple[float, Dict[str, Any]]:
        """Calculate Julian Day with enhanced precision and error handling."""
        
        conversion_info = {
            'local_time': f"{birth_date} {birth_time}",
            'timezone': timezone_str or 'UTC',
            'utc_time': None,
            'julian_day': None,
            'warnings': []
        }
        
        try:
            # Parse date and time
            dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
            
            # Handle timezone conversion with proper error handling
            if timezone_str:
                try:
                    tz = pytz.timezone(timezone_str)
                    
                    # Handle DST ambiguity
                    try:
                        dt_local = tz.localize(dt)
                    except pytz.exceptions.AmbiguousTimeError:
                        # During DST transition, choose standard time
                        dt_local = tz.localize(dt, is_dst=False)
                        conversion_info['warnings'].append("DST ambiguity resolved to standard time")
                    except pytz.exceptions.NonExistentTimeError:
                        # During DST gap, choose daylight time
                        dt_local = tz.localize(dt, is_dst=True)
                        conversion_info['warnings'].append("DST gap resolved to daylight time")
                    
                    # Convert to UTC
                    dt_utc = dt_local.astimezone(pytz.UTC)
                    
                except pytz.exceptions.UnknownTimeZoneError:
                    raise ValueError(f"Invalid timezone: {timezone_str}")
            else:
                # No timezone specified, assume UTC
                dt_utc = dt.replace(tzinfo=pytz.UTC)
                conversion_info['warnings'].append("No timezone specified, assuming UTC")
            
            conversion_info['utc_time'] = dt_utc.isoformat()
            
            # Calculate Julian Day with high precision
            julian_day = swe.julday(
                dt_utc.year, 
                dt_utc.month, 
                dt_utc.day,
                dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0 + dt_utc.microsecond / 3600000000.0
            )
            
            conversion_info['julian_day'] = julian_day
            
            return julian_day, conversion_info
            
        except Exception as e:
            raise ValueError(f"Failed to calculate Julian Day: {e}")

    def calculate_precise_ayanamsa(self, julian_day: float, 
                                 ayanamsa_system: AyanamsaSystem = AyanamsaSystem.LAHIRI) -> float:
        """Calculate ayanamsa with validation."""
        
        try:
            # Set the ayanamsa system
            swe.set_sid_mode(self.AYANAMSA_SYSTEMS[ayanamsa_system])
            
            # Calculate ayanamsa
            ayanamsa_value = swe.get_ayanamsa(julian_day)
            
            return ayanamsa_value
            
        except Exception as e:
            raise ValueError(f"Failed to calculate ayanamsa: {e}")

    def calculate_precise_houses(self, julian_day: float, latitude: float, longitude: float,
                               house_system: HouseSystem = HouseSystem.PLACIDUS,
                               ayanamsa_value: float = 0.0) -> Dict[str, Any]:
        """Calculate houses with enhanced precision."""
        
        try:
            # Get house system code
            system_code = self.HOUSE_SYSTEMS[house_system]
            
            # Calculate houses
            houses_data = swe.houses(julian_day, latitude, longitude, system_code)
            
            house_cusps = houses_data[0][:12]  # 12 house cusps
            ascmc = houses_data[1]  # Ascendant, MC, etc.
            
            # Apply ayanamsa correction for Vedic astrology
            corrected_cusps = []
            for cusp in house_cusps:
                corrected_cusp = self._normalize_longitude(cusp - ayanamsa_value)
                corrected_cusps.append(corrected_cusp)
            
            # Calculate corrected angles
            ascendant = self._normalize_longitude(ascmc[0] - ayanamsa_value)
            midheaven = self._normalize_longitude(ascmc[1] - ayanamsa_value)
            
            # Create house objects
            houses = []
            for i, cusp in enumerate(corrected_cusps):
                sign = self._get_sign_from_longitude(cusp)
                degree_in_sign = cusp % 30
                
                houses.append({
                    'house': i + 1,
                    'cusp_longitude': cusp,
                    'sign': sign.value,
                    'degree_in_sign': degree_in_sign,
                    'formatted': f"{degree_in_sign:.2f}° {sign.value}"
                })
            
            return {
                'houses': houses,
                'house_cusps': corrected_cusps,
                'ascendant': {
                    'longitude': ascendant,
                    'sign': self._get_sign_from_longitude(ascendant).value,
                    'degree': ascendant % 30
                },
                'midheaven': {
                    'longitude': midheaven,
                    'sign': self._get_sign_from_longitude(midheaven).value,
                    'degree': midheaven % 30
                }
            }
            
        except Exception as e:
            raise ValueError(f"Failed to calculate houses: {e}")

    def calculate_precise_planets(self, julian_day: float, house_cusps: List[float],
                                ayanamsa_value: float = 0.0) -> List[Dict[str, Any]]:
        """Calculate planetary positions with enhanced precision."""
        
        planets = []
        
        for planet_enum, planet_id in self.PLANET_CONSTANTS.items():
            try:
                # Calculate planetary position
                result = swe.calc_ut(julian_day, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
                
                if result[1] == 0:  # No error
                    position = result[0]
                    longitude = position[0]
                    latitude = position[1]
                    distance = position[2]
                    speed_lon = position[3]
                    speed_lat = position[4]
                    speed_dist = position[5]
                    
                    # Apply ayanamsa correction
                    corrected_longitude = self._normalize_longitude(longitude - ayanamsa_value)
                    
                    # Calculate sign and degree
                    sign = self._get_sign_from_longitude(corrected_longitude)
                    degree_in_sign = corrected_longitude % 30
                    
                    # Calculate house placement
                    house = self._calculate_house_placement(corrected_longitude, house_cusps)
                    
                    # Create planet data
                    planet_data = {
                        'planet': planet_enum.value,
                        'longitude': corrected_longitude,
                        'latitude': latitude,
                        'distance': distance,
                        'speed_longitude': speed_lon,
                        'speed_latitude': speed_lat,
                        'speed_distance': speed_dist,
                        'sign': sign.value,
                        'degree_in_sign': degree_in_sign,
                        'house': house,
                        'retrograde': speed_lon < 0,
                        'formatted': f"{degree_in_sign:.2f}° {sign.value}",
                        'house_position': f"House {house}"
                    }
                    
                    planets.append(planet_data)
                    
                    # Calculate Ketu for Rahu
                    if planet_enum == Planet.RAHU:
                        ketu_longitude = self._normalize_longitude(corrected_longitude + 180)
                        ketu_sign = self._get_sign_from_longitude(ketu_longitude)
                        ketu_degree = ketu_longitude % 30
                        ketu_house = self._calculate_house_placement(ketu_longitude, house_cusps)
                        
                        planets.append({
                            'planet': Planet.KETU.value,
                            'longitude': ketu_longitude,
                            'latitude': -latitude,
                            'distance': distance,
                            'speed_longitude': -speed_lon,
                            'speed_latitude': -speed_lat,
                            'speed_distance': speed_dist,
                            'sign': ketu_sign.value,
                            'degree_in_sign': ketu_degree,
                            'house': ketu_house,
                            'retrograde': True,  # Ketu is always retrograde
                            'formatted': f"{ketu_degree:.2f}° {ketu_sign.value}",
                            'house_position': f"House {ketu_house}"
                        })
                        
                else:
                    print(f"❌ Error calculating {planet_enum.value}: Swiss Ephemeris error {result[1]}")
                    
            except Exception as e:
                print(f"❌ Exception calculating {planet_enum.value}: {e}")
                print(f"   Traceback: {traceback.format_exc()}")
        
        return planets

    def _normalize_longitude(self, longitude: float) -> float:
        """Normalize longitude to 0-360 range."""
        return longitude % 360

    def _get_sign_from_longitude(self, longitude: float) -> ZodiacSign:
        """Get zodiac sign from longitude."""
        sign_index = int(self._normalize_longitude(longitude) / 30)
        return self.ZODIAC_SIGNS[sign_index % 12]

    def _calculate_house_placement(self, longitude: float, house_cusps: List[float]) -> int:
        """Calculate house placement with proper wraparound handling."""
        
        longitude = self._normalize_longitude(longitude)
        
        # Check each house with proper wraparound logic
        for i in range(12):
            cusp_current = self._normalize_longitude(house_cusps[i])
            cusp_next = self._normalize_longitude(house_cusps[(i + 1) % 12])
            
            # Handle wraparound at 0/360 degrees
            if cusp_current > cusp_next:
                # House crosses 0° (e.g., 350° to 10°)
                if longitude >= cusp_current or longitude < cusp_next:
                    return i + 1
            else:
                # Normal case
                if cusp_current <= longitude < cusp_next:
                    return i + 1
        
        # Fallback to first house
        return 1

    def generate_accurate_birth_chart(self, birth_date: str, birth_time: str,
                                    latitude: float, longitude: float,
                                    timezone_str: Optional[str] = None,
                                    house_system: HouseSystem = HouseSystem.PLACIDUS,
                                    ayanamsa_system: AyanamsaSystem = AyanamsaSystem.LAHIRI) -> Dict[str, Any]:
        """Generate a precise birth chart with comprehensive validation."""
        
        print(f"🌟 Generating Accurate Birth Chart")
        print(f"   Date: {birth_date}")
        print(f"   Time: {birth_time}")
        print(f"   Location: {latitude:.4f}°, {longitude:.4f}°")
        print(f"   Timezone: {timezone_str or 'UTC'}")
        print(f"   House System: {house_system.value}")
        print(f"   Ayanamsa: {ayanamsa_system.value}")
        
        try:
            # Validate input data
            validation = self.validate_birth_data(birth_date, birth_time, latitude, longitude, timezone_str)
            
            if not validation['valid']:
                raise ValueError(f"Validation failed: {validation['errors']}")
            
            # Calculate Julian Day
            julian_day, time_conversion = self.calculate_precise_julian_day(birth_date, birth_time, timezone_str)
            
            # Calculate Ayanamsa
            ayanamsa_value = self.calculate_precise_ayanamsa(julian_day, ayanamsa_system)
            
            # Calculate Houses
            house_data = self.calculate_precise_houses(julian_day, latitude, longitude, house_system, ayanamsa_value)
            
            # Calculate Planets
            planets = self.calculate_precise_planets(julian_day, house_data['house_cusps'], ayanamsa_value)
            
            # Create comprehensive result
            result = {
                'success': True,
                'birth_info': {
                    'date': birth_date,
                    'time': birth_time,
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone': timezone_str or 'UTC',
                    'julian_day': julian_day,
                    'time_conversion': time_conversion
                },
                'calculation_settings': {
                    'house_system': house_system.value,
                    'ayanamsa_system': ayanamsa_system.value,
                    'ayanamsa_value': ayanamsa_value,
                    'astrology_system': 'Vedic (Sidereal)'
                },
                'ascendant': house_data['ascendant'],
                'midheaven': house_data['midheaven'],
                'houses': house_data['houses'],
                'planets': planets,
                'validation': validation,
                'calculation_summary': {
                    'total_planets': len(planets),
                    'successful_calculations': len([p for p in planets if 'longitude' in p]),
                    'ephemeris_status': 'Available' if self.ephemeris_available else 'Limited'
                }
            }
            
            print(f"✅ Birth chart generated successfully!")
            print(f"   Ascendant: {house_data['ascendant']['formatted']}")
            print(f"   Planets calculated: {len(planets)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating birth chart: {e}")
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }


# Example usage and testing
def test_improved_service():
    """Test the improved birth chart service."""
    
    service = ImprovedBirthChartService()
    
    # Test with a known birth chart
    print("\n" + "="*60)
    print("TESTING IMPROVED BIRTH CHART SERVICE")
    print("="*60)
    
    # Test case: A sample birth chart
    chart = service.generate_accurate_birth_chart(
        birth_date="1990-01-15",
        birth_time="14:30", 
        latitude=40.7128,   # New York
        longitude=-74.0060,
        timezone_str="America/New_York",
        house_system=HouseSystem.PLACIDUS,
        ayanamsa_system=AyanamsaSystem.LAHIRI
    )
    
    if chart['success']:
        print("\n🎯 CHART SUMMARY:")
        print(f"Ascendant: {chart['ascendant']['degree']:.2f}° {chart['ascendant']['sign']}")
        print(f"Midheaven: {chart['midheaven']['degree']:.2f}° {chart['midheaven']['sign']}")
        print(f"Ayanamsa: {chart['calculation_settings']['ayanamsa_value']:.6f}°")
        
        print("\n🪐 PLANETS:")
        for planet in chart['planets']:
            retro = " (R)" if planet['retrograde'] else ""
            print(f"  {planet['planet']}: {planet['formatted']} in {planet['house_position']}{retro}")
        
        print("\n🏠 HOUSES:")
        for house in chart['houses'][:4]:  # First 4 houses
            print(f"  House {house['house']}: {house['formatted']}")
    else:
        print(f"❌ Chart generation failed: {chart['error']}")


if __name__ == "__main__":
    test_improved_service() 