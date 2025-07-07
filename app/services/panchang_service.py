"""
Panchang and Muhurat Service
Calculates Vedic calendar elements and auspicious timings using pyswisseph
"""

import swisseph as swe
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import pytz
import math

class PanchangService:
    """Service for calculating Panchang elements and Muhurats"""
    
    def __init__(self):
        """Initialize the Panchang service"""
        # Set ephemeris path
        swe.set_ephe_path('./swisseph_data')
        
        # Nakshatra names
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        # Tithi names
        self.tithis = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
            "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
            "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
        ]
        
        # Yoga names
        self.yogas = [
            "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
            "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva",
            "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",
            "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
            "Brahma", "Indra", "Vaidhriti"
        ]
        
        # Karana names
        self.karanas = [
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Shakuni", "Chatushpada", "Naga", "Kimstughna"
        ]
        
        # Weekday names
        self.weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
    def julian_day_from_datetime(self, dt: datetime) -> float:
        """Convert datetime to Julian Day Number"""
        # Convert to UTC if timezone-aware
        if dt.tzinfo is not None:
            dt_utc = dt.astimezone(timezone.utc)
        else:
            dt_utc = dt.replace(tzinfo=timezone.utc)
        
        year = dt_utc.year
        month = dt_utc.month
        day = dt_utc.day
        hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        
        jd = swe.julday(year, month, day, hour, swe.GREG_CAL)
        return jd
    
    def get_ayanamsa(self, jd: float, ayanamsa_type: str = "Lahiri") -> float:
        """Get ayanamsa value for given Julian Day"""
        ayanamsa_map = {
            "Lahiri": swe.SIDM_LAHIRI,
            "Raman": swe.SIDM_RAMAN,
            "KP": swe.SIDM_KRISHNAMURTI,
            "Yukteshwar": swe.SIDM_YUKTESHWAR
        }
        
        swe.set_sid_mode(ayanamsa_map.get(ayanamsa_type, swe.SIDM_LAHIRI))
        return swe.get_ayanamsa(jd)
    
    def calculate_planetary_positions(self, jd: float, ayanamsa: float) -> Dict[str, Dict[str, float]]:
        """Calculate sidereal positions of planets"""
        planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mars': swe.MARS,
            'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER,
            'Venus': swe.VENUS,
            'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE,
            'Ketu': swe.MEAN_NODE  # Ketu = Rahu + 180°
        }
        
        positions = {}
        
        for planet_name, planet_id in planets.items():
            try:
                # Calculate tropical position
                result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
                tropical_longitude = result[0][0]
                
                # Convert to sidereal
                if planet_name == 'Ketu':
                    sidereal_longitude = (tropical_longitude + 180 - ayanamsa) % 360
                else:
                    sidereal_longitude = (tropical_longitude - ayanamsa) % 360
                
                positions[planet_name] = {
                    'longitude': sidereal_longitude,
                    'tropical': tropical_longitude
                }
                
            except Exception as e:
                print(f"Error calculating {planet_name}: {e}")
                positions[planet_name] = {'longitude': 0, 'tropical': 0}
        
        return positions
    
    def calculate_tithi(self, sun_longitude: float, moon_longitude: float) -> Dict[str, Any]:
        """Calculate Tithi (Lunar Day)"""
        # Tithi is based on the angular difference between Sun and Moon
        longitude_diff = (moon_longitude - sun_longitude) % 360
        
        # Each tithi spans 12 degrees
        tithi_number = int(longitude_diff / 12) + 1
        tithi_progress = (longitude_diff % 12) / 12 * 100
        
        # Determine if it's Krishna Paksha or Shukla Paksha
        if tithi_number <= 15:
            paksha = "Shukla Paksha"
            tithi_name = self.tithis[tithi_number - 1] if tithi_number <= 14 else "Purnima"
        else:
            paksha = "Krishna Paksha"
            krishna_tithi = tithi_number - 15
            tithi_name = self.tithis[krishna_tithi - 1] if krishna_tithi <= 14 else "Amavasya"
        
        return {
            'tithi_number': tithi_number,
            'tithi_name': tithi_name,
            'paksha': paksha,
            'progress_percent': round(tithi_progress, 2),
            'longitude_diff': round(longitude_diff, 4)
        }
    
    def calculate_nakshatra(self, moon_longitude: float) -> Dict[str, Any]:
        """Calculate Nakshatra (Constellation)"""
        # Each nakshatra spans 13°20' (800 minutes of arc)
        nakshatra_span = 360 / 27  # 13.333...°
        
        nakshatra_number = int(moon_longitude / nakshatra_span) + 1
        nakshatra_progress = (moon_longitude % nakshatra_span) / nakshatra_span * 100
        
        # Nakshatra pada (quarter)
        pada_number = int((moon_longitude % nakshatra_span) / (nakshatra_span / 4)) + 1
        
        nakshatra_name = self.nakshatras[nakshatra_number - 1]
        
        return {
            'nakshatra_number': nakshatra_number,
            'nakshatra_name': nakshatra_name,
            'pada': pada_number,
            'progress_percent': round(nakshatra_progress, 2),
            'longitude': round(moon_longitude, 4)
        }
    
    def calculate_yoga(self, sun_longitude: float, moon_longitude: float) -> Dict[str, Any]:
        """Calculate Yoga"""
        # Yoga is based on the sum of Sun and Moon longitudes
        yoga_longitude = (sun_longitude + moon_longitude) % 360
        
        # Each yoga spans 13°20' (same as nakshatra)
        yoga_span = 360 / 27
        yoga_number = int(yoga_longitude / yoga_span) + 1
        yoga_progress = (yoga_longitude % yoga_span) / yoga_span * 100
        
        yoga_name = self.yogas[yoga_number - 1]
        
        return {
            'yoga_number': yoga_number,
            'yoga_name': yoga_name,
            'progress_percent': round(yoga_progress, 2),
            'longitude_sum': round(yoga_longitude, 4)
        }
    
    def calculate_karana(self, sun_longitude: float, moon_longitude: float) -> Dict[str, Any]:
        """Calculate Karana (Half Tithi)"""
        longitude_diff = (moon_longitude - sun_longitude) % 360
        
        # Each karana spans 6 degrees (half of tithi)
        karana_number = int(longitude_diff / 6) + 1
        karana_progress = (longitude_diff % 6) / 6 * 100
        
        # Karana follows a specific pattern
        if karana_number <= 7:
            karana_name = self.karanas[karana_number - 1]
        elif karana_number <= 14:
            karana_name = self.karanas[(karana_number - 8) % 7]
        elif karana_number <= 21:
            karana_name = self.karanas[(karana_number - 15) % 7]
        elif karana_number <= 28:
            karana_name = self.karanas[(karana_number - 22) % 7]
        elif karana_number <= 35:
            karana_name = self.karanas[(karana_number - 29) % 7]
        elif karana_number <= 42:
            karana_name = self.karanas[(karana_number - 36) % 7]
        elif karana_number <= 49:
            karana_name = self.karanas[(karana_number - 43) % 7]
        elif karana_number <= 56:
            karana_name = self.karanas[(karana_number - 50) % 7]
        else:
            # Fixed karanas
            if karana_number == 57:
                karana_name = self.karanas[7]  # Shakuni
            elif karana_number == 58:
                karana_name = self.karanas[8]  # Chatushpada
            elif karana_number == 59:
                karana_name = self.karanas[9]  # Naga
            else:
                karana_name = self.karanas[10]  # Kimstughna
        
        return {
            'karana_number': karana_number,
            'karana_name': karana_name,
            'progress_percent': round(karana_progress, 2)
        }
    
    def calculate_rahu_kaal(self, date: datetime, latitude: float, longitude: float) -> Dict[str, Any]:
        """Calculate Rahu Kaal timings using approximate sunrise/sunset"""
        try:
            # Approximate sunrise and sunset calculation
            # This is a simplified method that's more reliable than Swiss Ephemeris for this purpose
            
            # Get day of year
            day_of_year = date.timetuple().tm_yday
            
            # Calculate declination of sun (approximate)
            P = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            
            # Calculate sunrise and sunset times (approximate)
            lat_rad = math.radians(latitude)
            argument = -math.tan(lat_rad) * math.tan(math.radians(P))
            
            # Handle polar regions
            if argument < -1:
                argument = -1
            elif argument > 1:
                argument = 1
                
            hour_angle = math.degrees(math.acos(argument))
            
            # Calculate sunrise and sunset in decimal hours
            sunrise_hour = 12 - hour_angle / 15
            sunset_hour = 12 + hour_angle / 15
            
            # Apply longitude correction
            longitude_correction = longitude / 15
            sunrise_hour += longitude_correction
            sunset_hour += longitude_correction
            
            # Convert to datetime
            sunrise_dt = date.replace(hour=int(sunrise_hour), 
                                    minute=int((sunrise_hour % 1) * 60),
                                    second=0, microsecond=0)
            sunset_dt = date.replace(hour=int(sunset_hour), 
                                   minute=int((sunset_hour % 1) * 60),
                                   second=0, microsecond=0)
            
            # Calculate day duration
            day_duration = sunset_dt - sunrise_dt
            rahu_kaal_duration = day_duration / 8  # Rahu Kaal is 1/8th of day
            
            # Rahu Kaal timing based on weekday
            weekday = date.weekday()  # 0=Monday, 6=Sunday
            weekday_rahu_order = [7, 1, 6, 4, 5, 3, 2]  # Mon, Tue, Wed, Thu, Fri, Sat, Sun
            rahu_period = weekday_rahu_order[weekday]
            
            # Calculate Rahu Kaal start time
            rahu_start = sunrise_dt + (rahu_period - 1) * rahu_kaal_duration
            rahu_end = rahu_start + rahu_kaal_duration
            
            return {
                'rahu_kaal_start': rahu_start.strftime('%H:%M'),
                'rahu_kaal_end': rahu_end.strftime('%H:%M'),
                'duration_minutes': int(rahu_kaal_duration.total_seconds() / 60),
                'sunrise': sunrise_dt.strftime('%H:%M'),
                'sunset': sunset_dt.strftime('%H:%M'),
                'day_duration_hours': round(day_duration.total_seconds() / 3600, 2)
            }
            
        except Exception as e:
            print(f"Error calculating Rahu Kaal: {e}")
            return {
                'rahu_kaal_start': 'N/A',
                'rahu_kaal_end': 'N/A',
                'duration_minutes': 0,
                'sunrise': 'N/A',
                'sunset': 'N/A',
                'day_duration_hours': 0,
                'error': str(e)
            }
    
    def calculate_abhijit_muhurat(self, date: datetime, latitude: float, longitude: float) -> Dict[str, Any]:
        """Calculate Abhijit Muhurat (most auspicious time) using approximate sunrise/sunset"""
        try:
            # Use the same approximate calculation as Rahu Kaal
            day_of_year = date.timetuple().tm_yday
            
            # Calculate declination of sun (approximate)
            P = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            
            # Calculate sunrise and sunset times (approximate)
            lat_rad = math.radians(latitude)
            argument = -math.tan(lat_rad) * math.tan(math.radians(P))
            
            # Handle polar regions
            if argument < -1:
                argument = -1
            elif argument > 1:
                argument = 1
                
            hour_angle = math.degrees(math.acos(argument))
            
            # Calculate sunrise and sunset in decimal hours
            sunrise_hour = 12 - hour_angle / 15
            sunset_hour = 12 + hour_angle / 15
            
            # Apply longitude correction
            longitude_correction = longitude / 15
            sunrise_hour += longitude_correction
            sunset_hour += longitude_correction
            
            # Convert to datetime
            sunrise_dt = date.replace(hour=int(sunrise_hour), 
                                    minute=int((sunrise_hour % 1) * 60),
                                    second=0, microsecond=0)
            sunset_dt = date.replace(hour=int(sunset_hour), 
                                   minute=int((sunset_hour % 1) * 60),
                                   second=0, microsecond=0)
            
            # Abhijit muhurat is the 8th muhurat (middle of the day)
            day_duration = sunset_dt - sunrise_dt
            muhurat_duration = day_duration / 15  # Day divided into 15 muhurats
            
            # 8th muhurat (Abhijit) - most auspicious
            abhijit_start = sunrise_dt + 7 * muhurat_duration
            abhijit_end = abhijit_start + muhurat_duration
            
            return {
                'abhijit_start': abhijit_start.strftime('%H:%M'),
                'abhijit_end': abhijit_end.strftime('%H:%M'),
                'duration_minutes': int(muhurat_duration.total_seconds() / 60),
                'description': 'Most auspicious time for starting new ventures'
            }
            
        except Exception as e:
            return {
                'abhijit_start': 'N/A',
                'abhijit_end': 'N/A',
                'duration_minutes': 0,
                'description': 'Error calculating Abhijit muhurat',
                'error': str(e)
            }
    
    def jd_to_datetime(self, jd: float, tzinfo=None) -> datetime:
        """Convert Julian Day to datetime"""
        try:
            year, month, day, hour = swe.jdut1_to_utc(jd, swe.GREG_CAL)
            
            # Extract hours, minutes, seconds properly
            hours = int(hour)
            minutes_float = (hour - hours) * 60
            minutes = int(minutes_float)
            seconds_float = (minutes_float - minutes) * 60
            seconds = int(seconds_float)
            
            # Ensure values are within valid ranges
            hours = max(0, min(23, hours))
            minutes = max(0, min(59, minutes))
            seconds = max(0, min(59, seconds))
            
            dt = datetime(int(year), int(month), int(day), hours, minutes, seconds)
            
            if tzinfo:
                dt = dt.replace(tzinfo=timezone.utc).astimezone(tzinfo)
            
            return dt
            
        except Exception as e:
            print(f"Error in jd_to_datetime: {e}, jd={jd}")
            # Return a fallback datetime
            return datetime(2000, 1, 1, 12, 0, 0)
    
    def get_panchang(self, date: datetime, latitude: float, longitude: float, 
                    ayanamsa_type: str = "Lahiri") -> Dict[str, Any]:
        """Calculate complete Panchang for a given date and location"""
        
        # Convert to Julian Day
        jd = self.julian_day_from_datetime(date)
        
        # Get ayanamsa
        ayanamsa = self.get_ayanamsa(jd, ayanamsa_type)
        
        # Calculate planetary positions
        positions = self.calculate_planetary_positions(jd, ayanamsa)
        
        sun_longitude = positions['Sun']['longitude']
        moon_longitude = positions['Moon']['longitude']
        
        # Calculate Panchang elements
        tithi = self.calculate_tithi(sun_longitude, moon_longitude)
        nakshatra = self.calculate_nakshatra(moon_longitude)
        yoga = self.calculate_yoga(sun_longitude, moon_longitude)
        karana = self.calculate_karana(sun_longitude, moon_longitude)
        
        # Calculate Muhurats
        rahu_kaal = self.calculate_rahu_kaal(date, latitude, longitude)
        abhijit = self.calculate_abhijit_muhurat(date, latitude, longitude)
        
        # Weekday
        weekday = self.weekdays[date.weekday() if date.weekday() != 6 else 0]
        if date.weekday() == 6:  # Sunday
            weekday = self.weekdays[0]
        else:
            weekday = self.weekdays[date.weekday() + 1]
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'weekday': weekday,
            'ayanamsa': {
                'type': ayanamsa_type,
                'value': round(ayanamsa, 6)
            },
            'tithi': tithi,
            'nakshatra': nakshatra,
            'yoga': yoga,
            'karana': karana,
            'planetary_positions': {
                'sun': round(sun_longitude, 4),
                'moon': round(moon_longitude, 4)
            },
            'muhurats': {
                'rahu_kaal': rahu_kaal,
                'abhijit': abhijit
            },
            'timestamp': datetime.now().isoformat()
        } 