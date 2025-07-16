#!/usr/bin/env python3
"""
Supabase Database Service
Handles all database operations for user profiles and authentication
"""

import os
import base64
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from supabase import create_client, Client
from postgrest.exceptions import APIError

from app.models import (
    UserProfile, ProfileCreateRequest, ProfileUpdateRequest,
    BirthChartDetails
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Service for managing Supabase database operations
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            self.supabase_url = os.getenv('SUPABASE_URL', 'https://qwsuhrkzouptuhklyejh.supabase.co')
            self.supabase_key = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3c3Vocmt6b3VwdHVoa2x5ZWpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE3MDA2MjQsImV4cCI6MjA2NzI3NjYyNH0.EdpVqnaWc8txe0bsuSaQJleWZi4LkbD-nYP-IPUfvPk')
            
            # Initialize Supabase client with minimal configuration
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise

    def get_client(self) -> Client:
        """Get the initialized Supabase client"""
        return self.supabase

    async def create_profile(self, profile_data: ProfileCreateRequest) -> Optional[UserProfile]:
        """Create a new user profile"""
        try:
            data = profile_data.model_dump()
            logger.info(f"Creating profile with data: {data}")
            response = self.supabase.table('user_profiles').insert(data).execute()
            logger.info(f"Supabase response: {response.data}")
            
            if response.data:
                return UserProfile(**response.data[0])
            return None
        except APIError as e:
            logger.error(f"Failed to create profile: {str(e)}")
            raise

    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get a user profile by user_id"""
        try:
            response = self.supabase.table('user_profiles').select('*')\
                .match({'user_id': user_id}).execute()
            
            if response.data:
                return UserProfile(**response.data[0])
            return None
        except APIError as e:
            logger.error(f"Failed to get profile: {str(e)}")
            raise

    async def update_profile(self, user_id: str, profile_data: ProfileUpdateRequest) -> Optional[UserProfile]:
        """Update a user profile"""
        try:
            data = profile_data.model_dump(exclude_unset=True)
            response = self.supabase.table('user_profiles').update(data)\
                .match({'user_id': user_id}).execute()
            
            if response.data:
                return UserProfile(**response.data[0])
            return None
        except APIError as e:
            logger.error(f"Failed to update profile: {str(e)}")
            raise

    async def delete_profile(self, user_id: str) -> bool:
        """Delete a user profile"""
        try:
            response = self.supabase.table('user_profiles').delete()\
                .match({'user_id': user_id}).execute()
            return bool(response.data)
        except APIError as e:
            logger.error(f"Failed to delete profile: {str(e)}")
            raise

    async def profile_exists(self, user_id: str) -> bool:
        """Check if a profile exists"""
        try:
            response = self.supabase.table('user_profiles').select('id')\
                .match({'user_id': user_id}).execute()
            return bool(response.data)
        except APIError as e:
            logger.error(f"Failed to check profile existence: {str(e)}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check database connection health"""
        try:
            # Simple query to check database connection
            response = self.supabase.table('user_profiles').select('count').execute()
            return {
                "status": "connected",
                "total_profiles": len(response.data) if response.data else 0
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "disconnected",
                "error": str(e)
            }

    async def get_birth_chart_details(self, user_id: str) -> Optional[BirthChartDetails]:
        """Get birth chart details for a user"""
        try:
            response = self.supabase.table('birth_chart_details').select('*')\
                .match({'user_id': user_id}).execute()
            
            if response.data:
                data = response.data[0]
                
                # Handle chart_image decoding with error handling
                chart_image_data = data.get('chart_image', '')
                if chart_image_data:
                    try:
                        data['chart_image'] = base64.b64decode(chart_image_data)
                    except Exception as decode_error:
                        logger.warning(f"Failed to decode chart_image for user {user_id}: {decode_error}")
                        data['chart_image'] = b''  # Set to empty bytes if decoding fails
                else:
                    data['chart_image'] = b''  # Set to empty bytes if no chart_image
                
                return BirthChartDetails(**data)
            return None
        except APIError as e:
            logger.error(f"Failed to get birth chart details: {str(e)}")
            return None

    async def save_birth_chart_details(self, user_id: str, planet_positions: List[Dict[str, Any]], 
                                     chart_image: bytes = None) -> bool:
        """Save or update birth chart details"""
        try:
            data = {
                'user_id': user_id,
                'planet_positions': planet_positions,
                'updated_at': datetime.now().isoformat()
            }
            
            # Only include chart_image if it's provided and not empty
            if chart_image:
                data['chart_image'] = base64.b64encode(chart_image).decode('utf-8')
            
            # Try to update existing record first
            response = self.supabase.table('birth_chart_details').upsert(data).execute()
            
            return bool(response.data)
        except APIError as e:
            logger.error(f"Failed to save birth chart details: {str(e)}")
            return False

    async def delete_birth_chart_details(self, user_id: str) -> bool:
        """Delete birth chart details for a user"""
        try:
            response = self.supabase.table('birth_chart_details').delete()\
                .match({'user_id': user_id}).execute()
            return bool(response.data)
        except APIError as e:
            logger.error(f"Failed to delete birth chart details: {str(e)}")
            return False

    async def get_cached_birth_chart(self, user_id: str, birth_date: str, birth_time: str, 
                                   latitude: float, longitude: float, timezone: str,
                                   house_system: str = "Placidus", ayanamsa: str = "Lahiri") -> Optional[Dict[str, Any]]:
        """Get cached birth chart if it exists"""
        try:
            response = self.supabase.table('birth_chart_cache').select('*')\
                .match({
                    'user_id': user_id,
                    'birth_date': birth_date,
                    'birth_time': birth_time,
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone': timezone,
                    'house_system': house_system,
                    'ayanamsa': ayanamsa
                }).execute()
            
            if response.data:
                # Update last accessed timestamp
                cache_id = response.data[0]['id']
                self.supabase.table('birth_chart_cache').update({
                    'last_accessed_at': datetime.now().isoformat()
                }).match({'id': cache_id}).execute()
                
                return response.data[0]['chart_data']
            return None
        except APIError as e:
            logger.error(f"Failed to get cached birth chart: {str(e)}")
            return None

    async def cache_birth_chart(self, user_id: str, birth_date: str, birth_time: str,
                              latitude: float, longitude: float, timezone: str,
                              chart_data: Dict[str, Any], house_system: str = "Placidus",
                              ayanamsa: str = "Lahiri") -> bool:
        """Cache a birth chart"""
        try:
            data = {
                'user_id': user_id,
                'birth_date': birth_date,
                'birth_time': birth_time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone': timezone,
                'house_system': house_system,
                'ayanamsa': ayanamsa,
                'chart_data': chart_data,
                'created_at': datetime.now().isoformat(),
                'last_accessed_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('birth_chart_cache').upsert(data).execute()
            return bool(response.data)
        except APIError as e:
            logger.error(f"Failed to cache birth chart: {str(e)}")
            return False

    async def clear_old_cache_entries(self, days_old: int = 30) -> bool:
        """Clear cache entries older than specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            response = self.supabase.table('birth_chart_cache')\
                .delete().lt('last_accessed_at', cutoff_date).execute()
            return bool(response.data)
        except APIError as e:
            logger.error(f"Failed to clear old cache entries: {str(e)}")
            return False

# Initialize the service
supabase_service = SupabaseService() 