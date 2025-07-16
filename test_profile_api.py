#!/usr/bin/env python3
"""
Test script for Supabase Profile API integration
Tests all profile management endpoints
"""

import requests
import json
import uuid
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/profile"
TEST_USER_ID = f"test-user-{uuid.uuid4()}"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Database: {data['database']['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_create_profile():
    """Test creating a new profile"""
    print("\n📝 Testing profile creation...")
    
    profile_data = {
        "user_id": TEST_USER_ID,
        "name": "Test User",
        "birth_date": "1990-01-15",
        "birth_time": "14:30",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "Asia/Kolkata",
        "city": "New York",
        "state": "NY",
        "country": "USA"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/profile", json=profile_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Profile created successfully")
                print(f"   Profile ID: {data['profile']['id']}")
                print(f"   User ID: {data['profile']['user_id']}")
                print(f"   Name: {data['profile']['name']}")
                return True
            else:
                print(f"❌ Profile creation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Profile creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile creation error: {str(e)}")
        return False

def test_get_profile():
    """Test retrieving a profile"""
    print("\n🔍 Testing profile retrieval...")
    
    try:
        response = requests.get(f"{BASE_URL}/profile/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Profile retrieved successfully")
                print(f"   Name: {data['profile']['name']}")
                print(f"   Birth Date: {data['profile']['birth_date']}")
                print(f"   Birth Time: {data['profile']['birth_time']}")
                print(f"   Location: {data['profile']['city']}, {data['profile']['state']}")
                print(f"   Coordinates: {data['profile']['latitude']}, {data['profile']['longitude']}")
                return True
            else:
                print(f"❌ Profile retrieval failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile retrieval error: {str(e)}")
        return False

def test_check_profile_exists():
    """Test checking if profile exists"""
    print("\n🔍 Testing profile existence check...")
    
    try:
        response = requests.get(f"{BASE_URL}/profile/{TEST_USER_ID}/exists")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Profile existence check passed")
                print(f"   Profile exists: {data['exists']}")
                return True
            else:
                print(f"❌ Profile existence check failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Profile existence check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile existence check error: {str(e)}")
        return False

def test_update_profile():
    """Test updating a profile"""
    print("\n✏️ Testing profile update...")
    
    update_data = {
        "name": "Updated Test User",
        "city": "Los Angeles",
        "state": "CA"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/profile/{TEST_USER_ID}", json=update_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Profile updated successfully")
                print(f"   Updated Name: {data['profile']['name']}")
                print(f"   Updated City: {data['profile']['city']}")
                print(f"   Updated State: {data['profile']['state']}")
                print(f"   Updated House System: {data['profile']['house_system']}")
                return True
            else:
                print(f"❌ Profile update failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Profile update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile update error: {str(e)}")
        return False

def test_get_all_profiles():
    """Test retrieving all profiles"""
    print("\n📋 Testing get all profiles...")
    
    try:
        response = requests.get(f"{BASE_URL}/profiles?limit=10&offset=0")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ All profiles retrieved successfully")
                print(f"   Profile count: {data['count']}")
                print(f"   Limit: {data['limit']}")
                print(f"   Offset: {data['offset']}")
                return True
            else:
                print(f"❌ Get all profiles failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Get all profiles failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Get all profiles error: {str(e)}")
        return False

def test_delete_profile():
    """Test deleting a profile"""
    print("\n🗑️ Testing profile deletion...")
    
    try:
        response = requests.delete(f"{BASE_URL}/profile/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Profile deleted successfully")
                return True
            else:
                print(f"❌ Profile deletion failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Profile deletion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile deletion error: {str(e)}")
        return False

def test_get_deleted_profile():
    """Test retrieving a deleted profile (should fail)"""
    print("\n🔍 Testing retrieval of deleted profile...")
    
    try:
        response = requests.get(f"{BASE_URL}/profile/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            if not data.get("success"):
                print(f"✅ Deleted profile correctly not found")
                return True
            else:
                print(f"❌ Deleted profile was found (should not happen)")
                return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Deleted profile test error: {str(e)}")
        return False

def test_validation_errors():
    """Test validation errors"""
    print("\n🔍 Testing validation errors...")
    
    # Test invalid birth date
    invalid_profile = {
        "user_id": f"test-invalid-{uuid.uuid4()}",
        "name": "Invalid User",
        "birth_date": "invalid-date",
        "birth_time": "14:30",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    try:
        response = requests.post(f"{BASE_URL}/profile", json=invalid_profile)
        
        if response.status_code == 200:
            data = response.json()
            if not data.get("success"):
                print(f"✅ Validation error correctly caught: {data.get('error', 'Unknown error')}")
                return True
            else:
                print(f"❌ Invalid data was accepted (should not happen)")
                return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Validation test error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🌟 Starlight Astrology Profile API Test Suite")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Create Profile", test_create_profile),
        ("Get Profile", test_get_profile),
        ("Check Profile Exists", test_check_profile_exists),
        ("Update Profile", test_update_profile),
        ("Get All Profiles", test_get_all_profiles),
        ("Delete Profile", test_delete_profile),
        ("Get Deleted Profile", test_get_deleted_profile),
        ("Validation Errors", test_validation_errors)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The Profile API is working correctly.")
        return 0
    else:
        print(f"❌ {failed} tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 