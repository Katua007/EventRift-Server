#!/usr/bin/env python3
"""
Test CORS configuration for frontend integration
"""

import requests

def test_cors_endpoints():
    """Test CORS for all endpoints the frontend uses"""
    base_url = "https://eventrift-server.onrender.com"
    origin = "https://event-rift-client.vercel.app"
    
    endpoints = [
        "/auth/profile",
        "/api/auth/profile", 
        "/api/auth/login",
        "/api/events"
    ]
    
    print("🔍 Testing CORS Configuration")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            # Test OPTIONS preflight
            response = requests.options(
                f"{base_url}{endpoint}",
                headers={'Origin': origin},
                timeout=10
            )
            
            status = "✅ PASS" if response.status_code in [200, 204] else "❌ FAIL"
            print(f"{status} {endpoint} - Status: {response.status_code}")
            
            if response.status_code not in [200, 204]:
                print(f"   Headers: {dict(response.headers)}")
                
        except Exception as e:
            print(f"❌ FAIL {endpoint} - Error: {e}")

if __name__ == "__main__":
    test_cors_endpoints()