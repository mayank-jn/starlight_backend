#!/usr/bin/env python3
"""
Vedic Astrology Compatibility Matching Service
Implements comprehensive Ashtakoota (8-fold) compatibility matching system
"""

import swisseph as swe
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import math

from app.models import (
    CompatibilityMatchRequest, CompatibilityMatchResponse, BirthChartRequest,
    KootaScore, DoshaInfo, CompatibilityLevel, DoshaType, KootaType,
    ZodiacSign, Planet, PlanetPosition, BirthChartResponse
)
from app.services.birth_chart import BirthChartService


class CompatibilityMatchingService:
    """
    Comprehensive Vedic Astrology Compatibility Matching Service
    
    Implements the traditional Ashtakoota system:
    1. Varna (1 point) - Spiritual compatibility
    2. Vashya (2 points) - Mutual control/attraction
    3. Tara (3 points) - Health and well-being
    4. Yoni (4 points) - Sexual compatibility
    5. Grah Maitri (5 points) - Friendship of ruling planets
    6. Gana (6 points) - Nature compatibility
    7. Bhakoot (7 points) - Emotional & material prosperity
    8. Nadi (8 points) - Health & progeny
    
    Total: 36 points
    """
    
    def __init__(self):
        self.birth_chart_service = BirthChartService()
        
        # Initialize lookup tables for Ashtakoota calculations
        self._init_nakshatra_data()
        self._init_koota_tables()
        
    def _init_nakshatra_data(self):
        """Initialize Nakshatra data for calculations."""
        
        # 27 Nakshatras with their properties
        self.nakshatras = {
            1: {"name": "Ashwini", "lord": "Ketu", "gana": "Deva", "yoni": "Horse", "nadi": "Vata"},
            2: {"name": "Bharani", "lord": "Venus", "gana": "Manushya", "yoni": "Elephant", "nadi": "Pitta"},
            3: {"name": "Krittika", "lord": "Sun", "gana": "Rakshasa", "yoni": "Goat", "nadi": "Kapha"},
            4: {"name": "Rohini", "lord": "Moon", "gana": "Manushya", "yoni": "Serpent", "nadi": "Kapha"},
            5: {"name": "Mrigashira", "lord": "Mars", "gana": "Deva", "yoni": "Serpent", "nadi": "Pitta"},
            6: {"name": "Ardra", "lord": "Rahu", "gana": "Manushya", "yoni": "Dog", "nadi": "Vata"},
            7: {"name": "Punarvasu", "lord": "Jupiter", "gana": "Deva", "yoni": "Cat", "nadi": "Vata"},
            8: {"name": "Pushya", "lord": "Saturn", "gana": "Deva", "yoni": "Goat", "nadi": "Pitta"},
            9: {"name": "Ashlesha", "lord": "Mercury", "gana": "Rakshasa", "yoni": "Cat", "nadi": "Kapha"},
            10: {"name": "Magha", "lord": "Ketu", "gana": "Rakshasa", "yoni": "Rat", "nadi": "Kapha"},
            11: {"name": "Purva Phalguni", "lord": "Venus", "gana": "Manushya", "yoni": "Rat", "nadi": "Pitta"},
            12: {"name": "Uttara Phalguni", "lord": "Sun", "gana": "Manushya", "yoni": "Cow", "nadi": "Vata"},
            13: {"name": "Hasta", "lord": "Moon", "gana": "Deva", "yoni": "Buffalo", "nadi": "Vata"},
            14: {"name": "Chitra", "lord": "Mars", "gana": "Rakshasa", "yoni": "Tiger", "nadi": "Pitta"},
            15: {"name": "Swati", "lord": "Rahu", "gana": "Deva", "yoni": "Buffalo", "nadi": "Kapha"},
            16: {"name": "Vishakha", "lord": "Jupiter", "gana": "Rakshasa", "yoni": "Tiger", "nadi": "Kapha"},
            17: {"name": "Anuradha", "lord": "Saturn", "gana": "Deva", "yoni": "Deer", "nadi": "Pitta"},
            18: {"name": "Jyeshtha", "lord": "Mercury", "gana": "Rakshasa", "yoni": "Deer", "nadi": "Vata"},
            19: {"name": "Moola", "lord": "Ketu", "gana": "Rakshasa", "yoni": "Dog", "nadi": "Vata"},
            20: {"name": "Purva Ashadha", "lord": "Venus", "gana": "Manushya", "yoni": "Monkey", "nadi": "Pitta"},
            21: {"name": "Uttara Ashadha", "lord": "Sun", "gana": "Manushya", "yoni": "Mongoose", "nadi": "Kapha"},
            22: {"name": "Shravana", "lord": "Moon", "gana": "Deva", "yoni": "Monkey", "nadi": "Kapha"},
            23: {"name": "Dhanishta", "lord": "Mars", "gana": "Rakshasa", "yoni": "Lion", "nadi": "Pitta"},
            24: {"name": "Shatabhisha", "lord": "Rahu", "gana": "Rakshasa", "yoni": "Horse", "nadi": "Vata"},
            25: {"name": "Purva Bhadrapada", "lord": "Jupiter", "gana": "Manushya", "yoni": "Lion", "nadi": "Vata"},
            26: {"name": "Uttara Bhadrapada", "lord": "Saturn", "gana": "Manushya", "yoni": "Cow", "nadi": "Pitta"},
            27: {"name": "Revati", "lord": "Mercury", "gana": "Deva", "yoni": "Elephant", "nadi": "Kapha"}
        }
        
        # Varna (caste) system for zodiac signs
        self.varna_system = {
            ZodiacSign.ARIES: "Kshatriya",
            ZodiacSign.TAURUS: "Vaishya", 
            ZodiacSign.GEMINI: "Shudra",
            ZodiacSign.CANCER: "Brahmin",
            ZodiacSign.LEO: "Kshatriya",
            ZodiacSign.VIRGO: "Vaishya",
            ZodiacSign.LIBRA: "Shudra",
            ZodiacSign.SCORPIO: "Brahmin",
            ZodiacSign.SAGITTARIUS: "Kshatriya",
            ZodiacSign.CAPRICORN: "Vaishya",
            ZodiacSign.AQUARIUS: "Shudra",
            ZodiacSign.PISCES: "Brahmin"
        }
        
        # Vashya (dominance) system
        self.vashya_system = {
            ZodiacSign.ARIES: "Quadruped",
            ZodiacSign.TAURUS: "Quadruped",
            ZodiacSign.GEMINI: "Human",
            ZodiacSign.CANCER: "Water",
            ZodiacSign.LEO: "Quadruped",
            ZodiacSign.VIRGO: "Human",
            ZodiacSign.LIBRA: "Human",
            ZodiacSign.SCORPIO: "Insect",
            ZodiacSign.SAGITTARIUS: "Human",
            ZodiacSign.CAPRICORN: "Water",
            ZodiacSign.AQUARIUS: "Human",
            ZodiacSign.PISCES: "Water"
        }
        
    def _init_koota_tables(self):
        """Initialize compatibility tables for various kootas."""
        
        # Varna compatibility matrix
        self.varna_compatibility = {
            ("Brahmin", "Brahmin"): 1,
            ("Brahmin", "Kshatriya"): 1,
            ("Brahmin", "Vaishya"): 1,
            ("Brahmin", "Shudra"): 1,
            ("Kshatriya", "Brahmin"): 0,
            ("Kshatriya", "Kshatriya"): 1,
            ("Kshatriya", "Vaishya"): 1,
            ("Kshatriya", "Shudra"): 1,
            ("Vaishya", "Brahmin"): 0,
            ("Vaishya", "Kshatriya"): 0,
            ("Vaishya", "Vaishya"): 1,
            ("Vaishya", "Shudra"): 1,
            ("Shudra", "Brahmin"): 0,
            ("Shudra", "Kshatriya"): 0,
            ("Shudra", "Vaishya"): 0,
            ("Shudra", "Shudra"): 1,
        }
        
        # Vashya compatibility matrix
        self.vashya_compatibility = {
            ("Quadruped", "Quadruped"): 2,
            ("Quadruped", "Human"): 1,
            ("Human", "Human"): 2,
            ("Human", "Water"): 1,
            ("Human", "Insect"): 0,
            ("Water", "Water"): 2,
            ("Water", "Human"): 1,
            ("Insect", "Insect"): 2,
            ("Insect", "Human"): 0,
        }
        
        # Gana compatibility matrix
        self.gana_compatibility = {
            ("Deva", "Deva"): 6,
            ("Deva", "Manushya"): 5,
            ("Deva", "Rakshasa"): 0,
            ("Manushya", "Deva"): 5,
            ("Manushya", "Manushya"): 6,
            ("Manushya", "Rakshasa"): 0,
            ("Rakshasa", "Deva"): 0,
            ("Rakshasa", "Manushya"): 0,
            ("Rakshasa", "Rakshasa"): 6,
        }
        
        # Yoni compatibility matrix
        self.yoni_compatibility = {
            ("Horse", "Horse"): 4,
            ("Elephant", "Elephant"): 4,
            ("Goat", "Goat"): 4,
            ("Serpent", "Serpent"): 4,
            ("Dog", "Dog"): 4,
            ("Cat", "Cat"): 4,
            ("Rat", "Rat"): 4,
            ("Cow", "Cow"): 4,
            ("Buffalo", "Buffalo"): 4,
            ("Tiger", "Tiger"): 4,
            ("Deer", "Deer"): 4,
            ("Monkey", "Monkey"): 4,
            ("Mongoose", "Mongoose"): 4,
            ("Lion", "Lion"): 4,
            # Friendly combinations
            ("Horse", "Elephant"): 3,
            ("Goat", "Cow"): 3,
            ("Serpent", "Mongoose"): 0,  # Enemies
            ("Dog", "Deer"): 2,
            ("Cat", "Rat"): 0,  # Enemies
            ("Tiger", "Deer"): 0,  # Enemies
            ("Buffalo", "Tiger"): 3,
            ("Monkey", "Lion"): 2,
            # Add more combinations as needed
        }
        
        # Nadi compatibility (same nadi = 0 points, different nadi = 8 points)
        self.nadi_compatibility = {
            ("Vata", "Vata"): 0,
            ("Pitta", "Pitta"): 0,
            ("Kapha", "Kapha"): 0,
            ("Vata", "Pitta"): 8,
            ("Vata", "Kapha"): 8,
            ("Pitta", "Vata"): 8,
            ("Pitta", "Kapha"): 8,
            ("Kapha", "Vata"): 8,
            ("Kapha", "Pitta"): 8,
        }
        
        # Bhakoot compatibility based on distance between moon signs
        self.bhakoot_compatibility = {
            1: 0,  # Same sign
            2: 0,  # 2nd from each other
            3: 3,  # 3rd from each other
            4: 1,  # 4th from each other
            5: 0,  # 5th from each other
            6: 0,  # 6th from each other
            7: 7,  # 7th from each other (full points)
            8: 1,  # 8th from each other
            9: 3,  # 9th from each other
            10: 1, # 10th from each other
            11: 3, # 11th from each other
            12: 0, # 12th from each other
        }
        
    def calculate_nakshatra_from_moon(self, moon_longitude: float) -> int:
        """Calculate nakshatra number from Moon's longitude."""
        # Each nakshatra spans 13°20' (800 minutes)
        nakshatra_span = 13 + 20/60  # 13.333... degrees
        nakshatra_num = int(moon_longitude / nakshatra_span) + 1
        return min(nakshatra_num, 27)
        
    def get_moon_planet(self, birth_chart: BirthChartResponse) -> PlanetPosition:
        """Get Moon's position from birth chart."""
        for planet in birth_chart.planets:
            if planet.planet == Planet.MOON:
                return planet
        raise ValueError("Moon position not found in birth chart")
        
    def calculate_varna_koota(self, person1_moon_sign: ZodiacSign, person2_moon_sign: ZodiacSign) -> KootaScore:
        """Calculate Varna (spiritual compatibility) koota."""
        person1_varna = self.varna_system[person1_moon_sign]
        person2_varna = self.varna_system[person2_moon_sign]
        
        points = self.varna_compatibility.get((person1_varna, person2_varna), 0)
        
        description = f"Person 1 Varna: {person1_varna}, Person 2 Varna: {person2_varna}. "
        if points == 1:
            description += "Spiritual compatibility is present."
        else:
            description += "Spiritual compatibility may need attention."
            
        return KootaScore(
            koota_type=KootaType.VARNA,
            points_earned=points,
            max_points=1,
            percentage=(points / 1) * 100,
            compatibility_level=self._get_compatibility_level(points / 1),
            description=description,
            factors={"person1_varna": person1_varna, "person2_varna": person2_varna}
        )
        
    def calculate_vashya_koota(self, person1_moon_sign: ZodiacSign, person2_moon_sign: ZodiacSign) -> KootaScore:
        """Calculate Vashya (dominance/control) koota."""
        person1_vashya = self.vashya_system[person1_moon_sign]
        person2_vashya = self.vashya_system[person2_moon_sign]
        
        points = self.vashya_compatibility.get((person1_vashya, person2_vashya), 0)
        if points == 0:
            # Try reverse combination
            points = self.vashya_compatibility.get((person2_vashya, person1_vashya), 0)
            
        description = f"Person 1 Vashya: {person1_vashya}, Person 2 Vashya: {person2_vashya}. "
        if points == 2:
            description += "Excellent mutual control and attraction."
        elif points == 1:
            description += "Good attraction with balanced control."
        else:
            description += "May face challenges in mutual control."
            
        return KootaScore(
            koota_type=KootaType.VASHYA,
            points_earned=points,
            max_points=2,
            percentage=(points / 2) * 100,
            compatibility_level=self._get_compatibility_level(points / 2),
            description=description,
            factors={"person1_vashya": person1_vashya, "person2_vashya": person2_vashya}
        )
        
    def calculate_tara_koota(self, person1_nakshatra: int, person2_nakshatra: int) -> KootaScore:
        """Calculate Tara (health and well-being) koota."""
        # Calculate distance between nakshatras
        distance1 = ((person2_nakshatra - person1_nakshatra) % 27) + 1
        distance2 = ((person1_nakshatra - person2_nakshatra) % 27) + 1
        
        # Tara classification
        favorable_taras = [1, 3, 5, 7, 9]  # Janma, Sampat, Kshema, Sadhaka, Mitra
        
        points = 0
        if distance1 in favorable_taras and distance2 in favorable_taras:
            points = 3
        elif distance1 in favorable_taras or distance2 in favorable_taras:
            points = 1.5
        else:
            points = 0
            
        tara_names = {1: "Janma", 2: "Sampat", 3: "Vipat", 4: "Kshema", 5: "Pratyak", 
                     6: "Sadhaka", 7: "Vadha", 8: "Mitra", 9: "Atimitra"}
        
        person1_tara = tara_names.get(distance1, "Unknown")
        person2_tara = tara_names.get(distance2, "Unknown")
        
        description = f"Person 1 Tara: {person1_tara}, Person 2 Tara: {person2_tara}. "
        if points == 3:
            description += "Excellent health and well-being compatibility."
        elif points == 1.5:
            description += "Good health compatibility with some caution needed."
        else:
            description += "Health and well-being compatibility needs attention."
            
        return KootaScore(
            koota_type=KootaType.TARA,
            points_earned=points,
            max_points=3,
            percentage=(points / 3) * 100,
            compatibility_level=self._get_compatibility_level(points / 3),
            description=description,
            factors={"person1_tara": person1_tara, "person2_tara": person2_tara}
        )
        
    def calculate_yoni_koota(self, person1_nakshatra: int, person2_nakshatra: int) -> KootaScore:
        """Calculate Yoni (sexual compatibility) koota."""
        person1_yoni = self.nakshatras[person1_nakshatra]["yoni"]
        person2_yoni = self.nakshatras[person2_nakshatra]["yoni"]
        
        points = self.yoni_compatibility.get((person1_yoni, person2_yoni), 0)
        if points == 0:
            # Try reverse combination
            points = self.yoni_compatibility.get((person2_yoni, person1_yoni), 0)
            
        if points == 0:
            # Default scoring for unlisted combinations
            if person1_yoni == person2_yoni:
                points = 4
            else:
                points = 2  # Neutral compatibility
                
        description = f"Person 1 Yoni: {person1_yoni}, Person 2 Yoni: {person2_yoni}. "
        if points == 4:
            description += "Excellent sexual and physical compatibility."
        elif points >= 2:
            description += "Good physical compatibility."
        else:
            description += "Physical compatibility may need attention."
            
        return KootaScore(
            koota_type=KootaType.YONI,
            points_earned=points,
            max_points=4,
            percentage=(points / 4) * 100,
            compatibility_level=self._get_compatibility_level(points / 4),
            description=description,
            factors={"person1_yoni": person1_yoni, "person2_yoni": person2_yoni}
        )
        
    def calculate_grah_maitri_koota(self, person1_moon_sign: ZodiacSign, person2_moon_sign: ZodiacSign) -> KootaScore:
        """Calculate Grah Maitri (planetary friendship) koota."""
        # Get ruling planets of the signs
        sign_rulers = {
            ZodiacSign.ARIES: "Mars",
            ZodiacSign.TAURUS: "Venus",
            ZodiacSign.GEMINI: "Mercury",
            ZodiacSign.CANCER: "Moon",
            ZodiacSign.LEO: "Sun",
            ZodiacSign.VIRGO: "Mercury",
            ZodiacSign.LIBRA: "Venus",
            ZodiacSign.SCORPIO: "Mars",
            ZodiacSign.SAGITTARIUS: "Jupiter",
            ZodiacSign.CAPRICORN: "Saturn",
            ZodiacSign.AQUARIUS: "Saturn",
            ZodiacSign.PISCES: "Jupiter"
        }
        
        # Planetary friendship table
        planet_friends = {
            "Sun": ["Moon", "Mars", "Jupiter"],
            "Moon": ["Sun", "Mercury"],
            "Mars": ["Sun", "Moon", "Jupiter"],
            "Mercury": ["Sun", "Venus"],
            "Jupiter": ["Sun", "Moon", "Mars"],
            "Venus": ["Mercury", "Saturn"],
            "Saturn": ["Mercury", "Venus"]
        }
        
        person1_ruler = sign_rulers[person1_moon_sign]
        person2_ruler = sign_rulers[person2_moon_sign]
        
        points = 0
        if person1_ruler == person2_ruler:
            points = 5  # Same ruler
        elif person2_ruler in planet_friends.get(person1_ruler, []):
            points = 4  # Friends
        elif person1_ruler in planet_friends.get(person2_ruler, []):
            points = 4  # Friends
        else:
            points = 1  # Neutral or enemy
            
        description = f"Person 1 Ruler: {person1_ruler}, Person 2 Ruler: {person2_ruler}. "
        if points == 5:
            description += "Same planetary ruler - excellent compatibility."
        elif points == 4:
            description += "Friendly planetary rulers - good compatibility."
        else:
            description += "Planetary rulers need harmonization."
            
        return KootaScore(
            koota_type=KootaType.GRAH_MAITRI,
            points_earned=points,
            max_points=5,
            percentage=(points / 5) * 100,
            compatibility_level=self._get_compatibility_level(points / 5),
            description=description,
            factors={"person1_ruler": person1_ruler, "person2_ruler": person2_ruler}
        )
        
    def calculate_gana_koota(self, person1_nakshatra: int, person2_nakshatra: int) -> KootaScore:
        """Calculate Gana (nature/temperament) koota."""
        person1_gana = self.nakshatras[person1_nakshatra]["gana"]
        person2_gana = self.nakshatras[person2_nakshatra]["gana"]
        
        points = self.gana_compatibility.get((person1_gana, person2_gana), 0)
        
        description = f"Person 1 Gana: {person1_gana}, Person 2 Gana: {person2_gana}. "
        if points == 6:
            description += "Excellent temperament compatibility."
        elif points == 5:
            description += "Good temperament compatibility."
        else:
            description += "Temperament differences may cause friction."
            
        return KootaScore(
            koota_type=KootaType.GANA,
            points_earned=points,
            max_points=6,
            percentage=(points / 6) * 100,
            compatibility_level=self._get_compatibility_level(points / 6),
            description=description,
            factors={"person1_gana": person1_gana, "person2_gana": person2_gana}
        )
        
    def calculate_bhakoot_koota(self, person1_moon_sign: ZodiacSign, person2_moon_sign: ZodiacSign) -> KootaScore:
        """Calculate Bhakoot (emotional and material prosperity) koota."""
        # Get sign numbers (1-12)
        sign_numbers = {
            ZodiacSign.ARIES: 1, ZodiacSign.TAURUS: 2, ZodiacSign.GEMINI: 3,
            ZodiacSign.CANCER: 4, ZodiacSign.LEO: 5, ZodiacSign.VIRGO: 6,
            ZodiacSign.LIBRA: 7, ZodiacSign.SCORPIO: 8, ZodiacSign.SAGITTARIUS: 9,
            ZodiacSign.CAPRICORN: 10, ZodiacSign.AQUARIUS: 11, ZodiacSign.PISCES: 12
        }
        
        person1_sign_num = sign_numbers[person1_moon_sign]
        person2_sign_num = sign_numbers[person2_moon_sign]
        
        # Calculate distance
        distance = abs(person1_sign_num - person2_sign_num)
        if distance > 6:
            distance = 12 - distance
            
        points = self.bhakoot_compatibility.get(distance, 0)
        
        description = f"Signs are {distance} positions apart. "
        if points == 7:
            description += "Excellent emotional and material prosperity."
        elif points >= 3:
            description += "Good emotional compatibility."
        elif points == 1:
            description += "Moderate emotional compatibility."
        else:
            description += "Emotional compatibility needs attention."
            
        return KootaScore(
            koota_type=KootaType.BHAKOOT,
            points_earned=points,
            max_points=7,
            percentage=(points / 7) * 100,
            compatibility_level=self._get_compatibility_level(points / 7),
            description=description,
            factors={"distance": distance, "person1_sign": person1_moon_sign, "person2_sign": person2_moon_sign}
        )
        
    def calculate_nadi_koota(self, person1_nakshatra: int, person2_nakshatra: int) -> KootaScore:
        """Calculate Nadi (health and progeny) koota."""
        person1_nadi = self.nakshatras[person1_nakshatra]["nadi"]
        person2_nadi = self.nakshatras[person2_nakshatra]["nadi"]
        
        points = self.nadi_compatibility.get((person1_nadi, person2_nadi), 0)
        
        description = f"Person 1 Nadi: {person1_nadi}, Person 2 Nadi: {person2_nadi}. "
        if points == 8:
            description += "Excellent health and progeny compatibility."
        else:
            description += "Same Nadi - health and progeny issues may arise. Remedies recommended."
            
        return KootaScore(
            koota_type=KootaType.NADI,
            points_earned=points,
            max_points=8,
            percentage=(points / 8) * 100,
            compatibility_level=self._get_compatibility_level(points / 8),
            description=description,
            factors={"person1_nadi": person1_nadi, "person2_nadi": person2_nadi}
        )
        
    def calculate_manglik_dosha(self, birth_chart: BirthChartResponse) -> Dict[str, Any]:
        """Calculate Manglik Dosha from birth chart."""
        # Get Mars position
        mars_planet = None
        for planet in birth_chart.planets:
            if planet.planet == Planet.MARS:
                mars_planet = planet
                break
                
        if not mars_planet:
            return {"is_manglik": False, "houses": [], "severity": "None"}
            
        mars_house = mars_planet.house
        
        # Manglik houses: 1, 2, 4, 7, 8, 12
        manglik_houses = [1, 2, 4, 7, 8, 12]
        
        is_manglik = mars_house in manglik_houses
        
        severity = "None"
        if is_manglik:
            if mars_house in [1, 4, 7, 8, 12]:
                severity = "High"
            elif mars_house == 2:
                severity = "Medium"
                
        return {
            "is_manglik": is_manglik,
            "mars_house": mars_house,
            "severity": severity,
            "description": f"Mars is in house {mars_house}"
        }
        
    def calculate_doshas(self, person1_chart: BirthChartResponse, person2_chart: BirthChartResponse) -> List[DoshaInfo]:
        """Calculate all doshas for both persons."""
        doshas = []
        
        # Calculate Manglik Dosha
        person1_manglik = self.calculate_manglik_dosha(person1_chart)
        person2_manglik = self.calculate_manglik_dosha(person2_chart)
        
        cancelled = False
        cancellation_reason = None
        
        # Check if Manglik Dosha is cancelled
        if person1_manglik["is_manglik"] and person2_manglik["is_manglik"]:
            cancelled = True
            cancellation_reason = "Both persons are Manglik, dosha is cancelled"
        elif person1_manglik["is_manglik"] and not person2_manglik["is_manglik"]:
            # Check other cancellation conditions
            pass
        elif not person1_manglik["is_manglik"] and person2_manglik["is_manglik"]:
            # Check other cancellation conditions
            pass
            
        remedies = []
        if (person1_manglik["is_manglik"] or person2_manglik["is_manglik"]) and not cancelled:
            remedies = [
                "Perform Mangal Shanti Puja",
                "Recite Hanuman Chalisa daily",
                "Wear red coral gemstone",
                "Fast on Tuesdays",
                "Worship Lord Hanuman"
            ]
            
        manglik_dosha = DoshaInfo(
            dosha_type=DoshaType.MANGLIK,
            person1_affected=person1_manglik["is_manglik"],
            person2_affected=person2_manglik["is_manglik"],
            severity=max(person1_manglik["severity"], person2_manglik["severity"]),
            cancelled=cancelled,
            cancellation_reason=cancellation_reason,
            remedies=remedies,
            description=f"Person 1: {person1_manglik['description']}, Person 2: {person2_manglik['description']}"
        )
        
        doshas.append(manglik_dosha)
        
        # Calculate Nadi Dosha (from Nadi Koota)
        person1_moon = self.get_moon_planet(person1_chart)
        person2_moon = self.get_moon_planet(person2_chart)
        
        person1_nakshatra = self.calculate_nakshatra_from_moon(person1_moon.longitude)
        person2_nakshatra = self.calculate_nakshatra_from_moon(person2_moon.longitude)
        
        person1_nadi = self.nakshatras[person1_nakshatra]["nadi"]
        person2_nadi = self.nakshatras[person2_nakshatra]["nadi"]
        
        nadi_dosha_present = person1_nadi == person2_nadi
        
        nadi_dosha = DoshaInfo(
            dosha_type=DoshaType.NADI,
            person1_affected=nadi_dosha_present,
            person2_affected=nadi_dosha_present,
            severity="High" if nadi_dosha_present else "None",
            cancelled=False,
            cancellation_reason=None,
            remedies=["Perform Nadi Dosha remedies", "Consult astrologer for specific remedies"] if nadi_dosha_present else [],
            description=f"Person 1 Nadi: {person1_nadi}, Person 2 Nadi: {person2_nadi}"
        )
        
        doshas.append(nadi_dosha)
        
        return doshas
        
    def _get_compatibility_level(self, percentage: float) -> CompatibilityLevel:
        """Get compatibility level based on percentage."""
        if percentage >= 0.9:
            return CompatibilityLevel.EXCELLENT
        elif percentage >= 0.75:
            return CompatibilityLevel.VERY_GOOD
        elif percentage >= 0.6:
            return CompatibilityLevel.GOOD
        elif percentage >= 0.4:
            return CompatibilityLevel.AVERAGE
        elif percentage >= 0.2:
            return CompatibilityLevel.BELOW_AVERAGE
        else:
            return CompatibilityLevel.POOR
            
    def _get_overall_compatibility_level(self, total_points: float) -> CompatibilityLevel:
        """Get overall compatibility level based on total points."""
        percentage = total_points / 36
        return self._get_compatibility_level(percentage)
        
    def generate_match_summary(self, total_points: float, koota_scores: List[KootaScore], doshas: List[DoshaInfo]) -> str:
        """Generate comprehensive match summary."""
        percentage = (total_points / 36) * 100
        
        summary = f"This match scores {total_points:.1f} out of 36 points ({percentage:.1f}%). "
        
        if percentage >= 75:
            summary += "This is an excellent match with strong compatibility across multiple dimensions. "
        elif percentage >= 60:
            summary += "This is a good match with solid compatibility. "
        elif percentage >= 50:
            summary += "This is an average match that can work with mutual understanding. "
        else:
            summary += "This match faces challenges and requires careful consideration. "
            
        # Highlight strong areas
        strong_areas = [koota.koota_type for koota in koota_scores if koota.percentage >= 75]
        if strong_areas:
            summary += f"Strong areas include: {', '.join(strong_areas)}. "
            
        # Highlight weak areas
        weak_areas = [koota.koota_type for koota in koota_scores if koota.percentage < 50]
        if weak_areas:
            summary += f"Areas needing attention: {', '.join(weak_areas)}. "
            
        # Mention doshas
        active_doshas = [dosha for dosha in doshas if (dosha.person1_affected or dosha.person2_affected) and not dosha.cancelled]
        if active_doshas:
            summary += f"Active doshas: {', '.join([dosha.dosha_type for dosha in active_doshas])}. "
            
        return summary
        
    def generate_recommendations(self, total_points: float, koota_scores: List[KootaScore], doshas: List[DoshaInfo]) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        percentage = (total_points / 36) * 100
        
        if percentage >= 75:
            recommendations.append("This is an excellent match. Focus on nurturing the strong compatibility.")
        elif percentage >= 60:
            recommendations.append("Work on strengthening the weaker compatibility areas.")
        elif percentage >= 50:
            recommendations.append("Open communication and mutual understanding are key to success.")
        else:
            recommendations.append("Consider astrological remedies and counseling before proceeding.")
            
        # Specific koota recommendations
        for koota in koota_scores:
            if koota.percentage < 50:
                if koota.koota_type == KootaType.GANA:
                    recommendations.append("Practice patience and understanding due to temperament differences.")
                elif koota.koota_type == KootaType.NADI:
                    recommendations.append("Consult an astrologer for Nadi Dosha remedies.")
                elif koota.koota_type == KootaType.BHAKOOT:
                    recommendations.append("Work on emotional understanding and financial planning.")
                    
        # Dosha recommendations
        for dosha in doshas:
            if (dosha.person1_affected or dosha.person2_affected) and not dosha.cancelled:
                if dosha.dosha_type == DoshaType.MANGLIK:
                    recommendations.append("Perform Manglik Dosha remedies before marriage.")
                elif dosha.dosha_type == DoshaType.NADI:
                    recommendations.append("Address Nadi Dosha through appropriate remedies.")
                    
        return recommendations
        
    def calculate_compatibility_match(self, request: CompatibilityMatchRequest) -> CompatibilityMatchResponse:
        """Calculate comprehensive compatibility match using Ashtakoota system."""
        
        # Generate birth charts for both persons
        person1_request = BirthChartRequest(
            name=request.person1_name,
            birth_date=request.person1_birth_date,
            birth_time=request.person1_birth_time,
            latitude=request.person1_latitude,
            longitude=request.person1_longitude,
            timezone=request.person1_timezone,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa
        )
        
        person2_request = BirthChartRequest(
            name=request.person2_name,
            birth_date=request.person2_birth_date,
            birth_time=request.person2_birth_time,
            latitude=request.person2_latitude,
            longitude=request.person2_longitude,
            timezone=request.person2_timezone,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa
        )
        
        person1_chart = self.birth_chart_service.generate_birth_chart(person1_request)
        person2_chart = self.birth_chart_service.generate_birth_chart(person2_request)
        
        # Get Moon positions and calculate nakshatras
        person1_moon = self.get_moon_planet(person1_chart)
        person2_moon = self.get_moon_planet(person2_chart)
        
        person1_nakshatra = self.calculate_nakshatra_from_moon(person1_moon.longitude)
        person2_nakshatra = self.calculate_nakshatra_from_moon(person2_moon.longitude)
        
        # Calculate all 8 kootas
        koota_scores = []
        
        # 1. Varna Koota
        koota_scores.append(self.calculate_varna_koota(person1_moon.sign, person2_moon.sign))
        
        # 2. Vashya Koota
        koota_scores.append(self.calculate_vashya_koota(person1_moon.sign, person2_moon.sign))
        
        # 3. Tara Koota
        koota_scores.append(self.calculate_tara_koota(person1_nakshatra, person2_nakshatra))
        
        # 4. Yoni Koota
        koota_scores.append(self.calculate_yoni_koota(person1_nakshatra, person2_nakshatra))
        
        # 5. Grah Maitri Koota
        koota_scores.append(self.calculate_grah_maitri_koota(person1_moon.sign, person2_moon.sign))
        
        # 6. Gana Koota
        koota_scores.append(self.calculate_gana_koota(person1_nakshatra, person2_nakshatra))
        
        # 7. Bhakoot Koota
        koota_scores.append(self.calculate_bhakoot_koota(person1_moon.sign, person2_moon.sign))
        
        # 8. Nadi Koota
        koota_scores.append(self.calculate_nadi_koota(person1_nakshatra, person2_nakshatra))
        
        # Calculate total points
        total_points = sum(koota.points_earned for koota in koota_scores)
        total_percentage = (total_points / 36) * 100
        
        # Calculate doshas
        doshas = self.calculate_doshas(person1_chart, person2_chart)
        
        # Generate summary and recommendations
        match_summary = self.generate_match_summary(total_points, koota_scores, doshas)
        recommendations = self.generate_recommendations(total_points, koota_scores, doshas)
        
        # Create response
        return CompatibilityMatchResponse(
            person1_name=request.person1_name,
            person2_name=request.person2_name,
            total_points=total_points,
            total_percentage=total_percentage,
            compatibility_level=self._get_overall_compatibility_level(total_points),
            koota_scores=koota_scores,
            doshas=doshas,
            match_summary=match_summary,
            recommendations=recommendations,
            person1_chart=person1_chart,
            person2_chart=person2_chart
        )


# Create service instance
compatibility_service = CompatibilityMatchingService() 