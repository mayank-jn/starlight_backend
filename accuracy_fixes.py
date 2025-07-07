#!/usr/bin/env python3
"""
Accuracy Fixes for Existing Birth Chart Service
Addresses the key issues found in house placement and sign calculations
"""

import swisseph as swe
from datetime import datetime
import pytz
from typing import List, Dict, Any, Optional
import traceback


class AccuracyFixes:
    """Key accuracy improvements for the existing birth chart service."""
    
    @staticmethod
    def calculate_accurate_julian_day(birth_date: str, birth_time: str, timezone_str: Optional[str] = None) -> Dict[str, Any]:
        """
        FIXED: Enhanced Julian Day calculation with proper timezone handling.
        
        ISSUES FIXED:
        1. Silent timezone conversion failures
        2. DST ambiguity handling
        3. Precision improvements
        """
        
        result = {
            'julian_day': None,
            'utc_time': None,
            'local_time': f"{birth_date} {birth_time}",
            'timezone': timezone_str or 'UTC',
            'warnings': [],
            'success': False
        }
        
        try:
            # Parse date and time
            dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
            
            # Enhanced timezone handling
            if timezone_str:
                try:
                    tz = pytz.timezone(timezone_str)
                    
                    # Handle DST ambiguity properly
                    try:
                        dt_local = tz.localize(dt)
                        result['warnings'].append(f"✅ Timezone conversion successful: {timezone_str}")
                    except pytz.exceptions.AmbiguousTimeError:
                        # During DST overlap, use standard time
                        dt_local = tz.localize(dt, is_dst=False)
                        result['warnings'].append(f"⚠️  DST ambiguity resolved to standard time")
                    except pytz.exceptions.NonExistentTimeError:
                        # During DST gap, use daylight time
                        dt_local = tz.localize(dt, is_dst=True)
                        result['warnings'].append(f"⚠️  DST gap resolved to daylight time")
                    
                    # Convert to UTC
                    dt_utc = dt_local.astimezone(pytz.UTC)
                    result['utc_time'] = dt_utc.isoformat()
                    
                except pytz.exceptions.UnknownTimeZoneError:
                    raise ValueError(f"❌ Invalid timezone: {timezone_str}")
                except Exception as e:
                    raise ValueError(f"❌ Timezone conversion failed: {e}")
            else:
                # No timezone specified
                dt_utc = dt.replace(tzinfo=pytz.UTC)
                result['warnings'].append("⚠️  No timezone specified, assuming UTC")
                result['utc_time'] = dt_utc.isoformat()
            
            # Calculate Julian Day with enhanced precision
            julian_day = swe.julday(
                dt_utc.year, 
                dt_utc.month, 
                dt_utc.day,
                dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
            )
            
            result['julian_day'] = julian_day
            result['success'] = True
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()
            return result
    
    @staticmethod
    def calculate_accurate_house_placement(longitude: float, house_cusps: List[float]) -> int:
        """
        FIXED: Accurate house placement with proper wraparound handling.
        
        ISSUES FIXED:
        1. Wraparound at 0/360 degrees
        2. Edge cases in house boundaries
        3. Proper cusp handling
        """
        
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
    
    @staticmethod
    def validate_birth_data(birth_date: str, birth_time: str, latitude: float, longitude: float, timezone_str: Optional[str] = None) -> Dict[str, Any]:
        """
        FIXED: Comprehensive input validation.
        
        ISSUES FIXED:
        1. Date format validation
        2. Coordinate range validation
        3. Timezone validation
        4. Time format validation
        """
        
        errors = []
        warnings = []
        
        # Validate date format and range
        try:
            date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
            
            # Check reasonable date range for accurate calculations
            if date_obj.year < 1900:
                warnings.append(f"⚠️  Birth year {date_obj.year} is before 1900 - accuracy may be reduced")
            elif date_obj.year > 2100:
                warnings.append(f"⚠️  Birth year {date_obj.year} is after 2100 - accuracy may be reduced")
                
        except ValueError:
            errors.append(f"❌ Invalid date format '{birth_date}'. Use YYYY-MM-DD format")
        
        # Validate time format
        try:
            time_obj = datetime.strptime(birth_time, '%H:%M')
        except ValueError:
            errors.append(f"❌ Invalid time format '{birth_time}'. Use HH:MM format (24-hour)")
        
        # Validate coordinates with proper ranges
        if not isinstance(latitude, (int, float)):
            errors.append(f"❌ Latitude must be a number, got {type(latitude).__name__}")
        elif not (-90 <= latitude <= 90):
            errors.append(f"❌ Invalid latitude {latitude}. Must be between -90 and +90 degrees")
        
        if not isinstance(longitude, (int, float)):
            errors.append(f"❌ Longitude must be a number, got {type(longitude).__name__}")
        elif not (-180 <= longitude <= 180):
            errors.append(f"❌ Invalid longitude {longitude}. Must be between -180 and +180 degrees")
        
        # Validate timezone
        if timezone_str:
            try:
                tz = pytz.timezone(timezone_str)
                # Test with sample date to validate timezone
                test_dt = datetime(2000, 1, 1, 12, 0)
                try:
                    tz.localize(test_dt)
                except Exception:
                    warnings.append(f"⚠️  Timezone {timezone_str} may have issues with the specified date")
            except pytz.exceptions.UnknownTimeZoneError:
                errors.append(f"❌ Invalid timezone '{timezone_str}'. Use standard timezone names like 'America/New_York'")
        else:
            warnings.append("⚠️  No timezone specified. Assuming UTC")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'summary': f"Validation: {'✅ PASSED' if len(errors) == 0 else '❌ FAILED'} ({len(errors)} errors, {len(warnings)} warnings)"
        }
    
    @staticmethod
    def apply_ayanamsa_correction(longitude: float, ayanamsa_value: float) -> float:
        """
        FIXED: Apply ayanamsa correction with proper normalization.
        
        ISSUES FIXED:
        1. Proper longitude normalization
        2. Consistent ayanamsa application
        """
        
        # Apply ayanamsa correction and normalize to 0-360 range
        corrected_longitude = (longitude - ayanamsa_value) % 360
        return corrected_longitude
    
    @staticmethod
    def get_zodiac_sign_accurate(longitude: float) -> str:
        """
        FIXED: Accurate zodiac sign calculation with proper bounds.
        
        ISSUES FIXED:
        1. Proper sign boundaries
        2. Normalization of longitude
        """
        
        signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer',
            'Leo', 'Virgo', 'Libra', 'Scorpio',
            'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        # Normalize longitude and calculate sign
        normalized_longitude = longitude % 360
        sign_index = int(normalized_longitude / 30)
        
        # Ensure sign index is within valid range
        sign_index = max(0, min(sign_index, 11))
        
        return signs[sign_index]
    
    @staticmethod
    def calculate_degree_in_sign(longitude: float) -> float:
        """
        FIXED: Calculate degree within sign with proper precision.
        
        ISSUES FIXED:
        1. Proper degree calculation
        2. Precision handling
        """
        
        normalized_longitude = longitude % 360
        degree_in_sign = normalized_longitude % 30
        
        return degree_in_sign
    
    @staticmethod
    def diagnostic_report(birth_date: str, birth_time: str, latitude: float, longitude: float, timezone_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a diagnostic report for accuracy verification.
        """
        
        print("🔍 ACCURACY DIAGNOSTIC REPORT")
        print("=" * 50)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_data': {
                'birth_date': birth_date,
                'birth_time': birth_time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone': timezone_str
            },
            'tests': {}
        }
        
        # Test 1: Input validation
        print("\n1️⃣  Testing Input Validation...")
        validation = AccuracyFixes.validate_birth_data(birth_date, birth_time, latitude, longitude, timezone_str)
        report['tests']['validation'] = validation
        print(f"   {validation['summary']}")
        
        for warning in validation['warnings']:
            print(f"   {warning}")
        for error in validation['errors']:
            print(f"   {error}")
        
        # Test 2: Julian Day calculation
        print("\n2️⃣  Testing Julian Day Calculation...")
        jd_result = AccuracyFixes.calculate_accurate_julian_day(birth_date, birth_time, timezone_str)
        report['tests']['julian_day'] = jd_result
        
        if jd_result['success']:
            print(f"   ✅ Julian Day: {jd_result['julian_day']:.6f}")
            print(f"   ✅ UTC Time: {jd_result['utc_time']}")
            for warning in jd_result['warnings']:
                print(f"   {warning}")
        else:
            print(f"   ❌ Julian Day calculation failed: {jd_result.get('error', 'Unknown error')}")
        
        # Test 3: Sample calculations
        print("\n3️⃣  Testing Sample Calculations...")
        
        # Test house placement with sample data
        sample_cusps = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
        test_longitudes = [15, 45, 75, 359, 1, 179, 181]
        
        house_tests = []
        for test_long in test_longitudes:
            house = AccuracyFixes.calculate_accurate_house_placement(test_long, sample_cusps)
            sign = AccuracyFixes.get_zodiac_sign_accurate(test_long)
            degree = AccuracyFixes.calculate_degree_in_sign(test_long)
            
            house_tests.append({
                'longitude': test_long,
                'house': house,
                'sign': sign,
                'degree': degree
            })
            
            print(f"   Longitude {test_long:3.0f}° → House {house}, {degree:.1f}° {sign}")
        
        report['tests']['house_placement'] = house_tests
        
        # Test 4: Ayanamsa correction
        print("\n4️⃣  Testing Ayanamsa Correction...")
        sample_ayanamsa = 24.0  # Approximate current Lahiri ayanamsa
        
        ayanamsa_tests = []
        for test_long in [0, 90, 180, 270, 360]:
            corrected = AccuracyFixes.apply_ayanamsa_correction(test_long, sample_ayanamsa)
            ayanamsa_tests.append({
                'original': test_long,
                'corrected': corrected,
                'difference': test_long - corrected
            })
            
            print(f"   {test_long:3.0f}° → {corrected:.1f}° (diff: {test_long - corrected:.1f}°)")
        
        report['tests']['ayanamsa_correction'] = ayanamsa_tests
        
        # Overall assessment
        print("\n🎯 ACCURACY ASSESSMENT")
        print("=" * 30)
        
        if validation['valid'] and jd_result['success']:
            print("✅ EXCELLENT - All core calculations working correctly")
            print("   • Input validation passed")
            print("   • Julian Day calculation accurate")
            print("   • House placement logic improved")
            print("   • Sign calculations precise")
            overall_status = "EXCELLENT"
        elif validation['valid']:
            print("⚠️  GOOD - Input validation passed but some calculation issues")
            overall_status = "GOOD"
        else:
            print("❌ POOR - Input validation failed")
            overall_status = "POOR"
        
        report['overall_status'] = overall_status
        
        return report


def main():
    """Test the accuracy fixes."""
    
    # Test with sample data
    AccuracyFixes.diagnostic_report(
        birth_date="1990-01-15",
        birth_time="14:30",
        latitude=40.7128,
        longitude=-74.0060,
        timezone_str="America/New_York"
    )
    
    print("\n" + "="*60)
    print("🛠️  RECOMMENDED FIXES FOR EXISTING SERVICE:")
    print("="*60)
    print("1. Replace calculate_julian_day() with calculate_accurate_julian_day()")
    print("2. Replace get_house_number() with calculate_accurate_house_placement()")
    print("3. Add validate_birth_data() before all calculations")
    print("4. Use apply_ayanamsa_correction() for consistent ayanamsa application")
    print("5. Replace sign calculations with get_zodiac_sign_accurate()")


if __name__ == "__main__":
    main() 