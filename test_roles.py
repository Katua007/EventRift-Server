#!/usr/bin/env python3
"""
Test role-based authentication and dashboard routing
"""

import requests
import time

BASE_URL = "https://eventrift-server.onrender.com"

def test_role_based_login():
    """Test login with different roles"""
    print("🎭 Testing Role-Based Authentication")
    print("=" * 50)
    
    test_users = [
        {'email': 'goer@test.com', 'password': 'test', 'expected_role': 'Goer'},
        {'email': 'organizer@test.com', 'password': 'test', 'expected_role': 'Organizer'},
        {'email': 'groom@gmail.com', 'password': 'test', 'expected_role': 'Organizer'},
        {'email': 'vendor@test.com', 'password': 'test', 'expected_role': 'Vendor'}
    ]
    
    for user in test_users:
        try:
            print(f"\n🔐 Testing {user['email']}...")
            
            # Test login
            response = requests.post(f"{BASE_URL}/api/auth/login", 
                                   json={'email': user['email'], 'password': user['password']})
            
            if response.status_code == 200:
                data = response.json()
                actual_role = data['user']['role']
                
                if actual_role == user['expected_role']:
                    print(f"✅ Role correct: {actual_role}")
                    
                    # Test appropriate dashboard
                    token = data['access_token']
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    if actual_role == 'Organizer':
                        dash_response = requests.get(f"{BASE_URL}/api/dashboard/organizer", headers=headers)
                    elif actual_role == 'Vendor':
                        dash_response = requests.get(f"{BASE_URL}/api/dashboard/vendor", headers=headers)
                    else:
                        dash_response = requests.get(f"{BASE_URL}/api/dashboard/goer", headers=headers)
                    
                    if dash_response.status_code == 200:
                        print(f"✅ Dashboard accessible")
                    else:
                        print(f"❌ Dashboard failed: {dash_response.status_code}")
                else:
                    print(f"❌ Role mismatch: expected {user['expected_role']}, got {actual_role}")
            else:
                print(f"❌ Login failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Wait for deployment
    time.sleep(30)
    test_role_based_login()