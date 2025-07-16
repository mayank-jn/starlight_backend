#!/usr/bin/env python3
"""Test script for Prokerala API authentication"""

import os
from app.services.prokerala_service import prokerala_service

def test_prokerala_auth():
    """Test Prokerala API authentication"""
    try:
        # Force debug mode
        prokerala_service.debug = True
        
        # Try to get a token
        token = prokerala_service._get_access_token()
        print(f"\nSuccess! Got token: {token[:10]}...")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_prokerala_auth() 