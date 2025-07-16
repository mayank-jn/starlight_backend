#!/usr/bin/env python3
"""
Profile Router for User Profile Management
Provides endpoints for CRUD operations on user profiles stored in Supabase
"""

from fastapi import APIRouter, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

from app.models import (
    UserProfile, ProfileCreateRequest, ProfileUpdateRequest, ProfileResponse,
    ErrorResponse
)
from app.services.supabase_service import supabase_service

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/profile", response_model=ProfileResponse)
async def upsert_profile(request: ProfileCreateRequest):
    """
    Create or update a user profile
    
    This endpoint handles both creation and updates:
    - If profile doesn't exist, creates a new one
    - If profile exists, updates the existing one
    - Validates all required fields
    - Returns the complete profile data
    
    Args:
        request: ProfileCreateRequest with all profile data
        
    Returns:
        ProfileResponse: Profile data or error message
    """
    try:
        logger.info(f"Upserting profile for user_id: {request.user_id}")
        
        # Check if profile exists
        existing_profile = await supabase_service.profile_exists(request.user_id)
        
        if existing_profile:
            # Update existing profile
            logger.info(f"Updating existing profile for user_id: {request.user_id}")
            # Convert CreateRequest to UpdateRequest
            update_data = ProfileUpdateRequest(
                name=request.name,
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                latitude=request.latitude,
                longitude=request.longitude,
                timezone=request.timezone,
                city=request.city,
                state=request.state,
                country=request.country
            )
            profile = await supabase_service.update_profile(request.user_id, update_data)
            message = "Profile updated successfully"
        else:
            # Create new profile
            logger.info(f"Creating new profile for user_id: {request.user_id}")
            profile = await supabase_service.create_profile(request)
            message = "Profile created successfully"
        
        if profile:
            return ProfileResponse(
                success=True,
                profile=profile,
                message=message
            )
        else:
            return ProfileResponse(
                success=False,
                error="Failed to upsert profile"
            )
            
    except ValueError as e:
        logger.error(f"Validation error upserting profile: {str(e)}")
        return ProfileResponse(
            success=False,
            error=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error upserting profile: {str(e)}")
        return ProfileResponse(
            success=False,
            error=f"Failed to upsert profile: {str(e)}"
        )

@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: str = Path(..., description="Supabase user ID")
):
    """
    Get user profile by user_id
    
    This endpoint retrieves a user's complete profile information including:
    - Personal information (name, birth details)
    - Birth location (coordinates, city, state, country)
    - Timestamps (created_at, updated_at)
    
    Args:
        user_id: Supabase user ID
        
    Returns:
        ProfileResponse: User profile data or error message
    """
    try:
        logger.info(f"Retrieving profile for user_id: {user_id}")
        
        # Get profile from database
        profile = await supabase_service.get_profile(user_id)
        
        if profile:
            return ProfileResponse(
                success=True,
                profile=profile,
                message="Profile retrieved successfully"
            )
        else:
            return ProfileResponse(
                success=False,
                message=f"No profile found for user_id: {user_id}"
            )
            
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        return ProfileResponse(
            success=False,
            error=f"Failed to retrieve profile: {str(e)}"
        )

@router.delete("/profile/{user_id}")
async def delete_profile(
    user_id: str = Path(..., description="Supabase user ID")
):
    """
    Delete a user profile
    
    This endpoint permanently deletes a user's profile from the database:
    - Removes all profile data including birth information
    - Cannot be undone - permanent deletion
    - Returns success/failure status
    
    Args:
        user_id: Supabase user ID
        
    Returns:
        JSON response indicating success or failure
    """
    try:
        logger.info(f"Deleting profile for user_id: {user_id}")
        
        # Check if profile exists
        existing_profile = await supabase_service.profile_exists(user_id)
        if not existing_profile:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "error": f"No profile found for user_id: {user_id}"
                }
            )
        
        # Delete profile
        success = await supabase_service.delete_profile(user_id)
        
        if success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Profile deleted successfully"
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Failed to delete profile"
                }
            )
            
    except Exception as e:
        logger.error(f"Unexpected error deleting profile: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"Failed to delete profile: {str(e)}"
            }
        )

@router.get("/profile/{user_id}/exists")
async def check_profile_exists(
    user_id: str = Path(..., description="Supabase user ID")
):
    """
    Check if a user profile exists
    
    This endpoint checks whether a user has a profile in the database:
    - Lightweight check without returning full profile data
    - Useful for conditional UI rendering
    - Returns boolean exists status
    
    Args:
        user_id: Supabase user ID
        
    Returns:
        JSON response with exists boolean
    """
    try:
        logger.info(f"Checking profile existence for user_id: {user_id}")
        
        exists = await supabase_service.profile_exists(user_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "exists": exists,
                "user_id": user_id
            }
        )
        
    except Exception as e:
        logger.error(f"Error checking profile existence: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"Failed to check profile existence: {str(e)}"
            }
        )

@router.get("/profiles", response_model=Dict[str, Any])
async def get_all_profiles(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of profiles to return"),
    offset: int = Query(default=0, ge=0, description="Number of profiles to skip")
):
    """
    Get all user profiles (Admin endpoint)
    
    This endpoint retrieves all user profiles with pagination:
    - Intended for admin use only
    - Supports pagination with limit and offset
    - Returns list of all profiles
    
    Args:
        limit: Maximum number of profiles to return (1-1000)
        offset: Number of profiles to skip for pagination
        
    Returns:
        JSON response with profiles list and metadata
    """
    try:
        logger.info(f"Retrieving all profiles (limit: {limit}, offset: {offset})")
        
        profiles = await supabase_service.get_all_profiles(limit, offset)
        
        return {
            "success": True,
            "profiles": [profile.dict() for profile in profiles],
            "count": len(profiles),
            "limit": limit,
            "offset": offset,
            "message": f"Retrieved {len(profiles)} profiles"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving all profiles: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to retrieve profiles: {str(e)}"
        }

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the profile service
    
    This endpoint checks the health of the profile service:
    - Tests Supabase database connection
    - Returns connection status and metadata
    - Includes total profile count
    
    Returns:
        JSON response with health status
    """
    try:
        logger.info("Performing profile service health check")
        
        # Check Supabase connection
        health_status = await supabase_service.health_check()
        
        return {
            "service": "Profile Management API",
            "version": "1.0.0",
            "status": "healthy",
            "database": health_status,
            "endpoints": {
                "get_profile": "GET /profile/{user_id}",
                "create_profile": "POST /profile",
                "update_profile": "PUT /profile/{user_id}",
                "delete_profile": "DELETE /profile/{user_id}",
                "check_exists": "GET /profile/{user_id}/exists",
                "get_all_profiles": "GET /profiles",
                "health_check": "GET /health"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "service": "Profile Management API",
            "version": "1.0.0",
            "status": "unhealthy",
            "error": str(e)
        } 