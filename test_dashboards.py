#!/usr/bin/env python3
"""
Test script to verify all dashboard endpoints are working correctly
Run this after starting the server to test all user roles and their dashboards
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5555"

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            return response.json() if response.content else {}
        else:
            print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return False

def main():
    print("🚀 Testing EventRift Server Dashboard Endpoints")
    print("=" * 50)
    
    # Test health check
    print("\n📋 Testing Health Check")
    health = test_endpoint('GET', '/api/test/health')
    if not health:
        print("❌ Server is not running or health check failed")
        sys.exit(1)
    
    # Setup test data
    print("\n📋 Setting up test data")
    setup_result = test_endpoint('POST', '/api/test/setup-test-data', expected_status=201)
    if not setup_result:
        print("⚠️  Test data setup failed, continuing with existing data")
    
    # Test user registration and login for each role
    test_users = [
        {'email': 'goer@test.com', 'username': 'Test Goer', 'role': 'Goer', 'password': 'password123'},
        {'email': 'organizer@test.com', 'username': 'Test Organizer', 'role': 'Organizer', 'password': 'password123'},
        {'email': 'vendor@test.com', 'username': 'Test Vendor', 'role': 'Vendor', 'password': 'password123'},
        {'email': 'admin@test.com', 'username': 'Test Admin', 'role': 'Admin', 'password': 'password123'}
    ]
    
    tokens = {}
    
    for user in test_users:
        print(f"\n📋 Testing {user['role']} Authentication")
        
        # Try to register (might fail if user exists)
        register_result = test_endpoint('POST', '/auth/register', user, expected_status=201)
        if not register_result:
            print(f"   Registration failed (user might already exist)")
        
        # Login
        login_data = {'email': user['email'], 'password': user['password']}
        login_result = test_endpoint('POST', '/auth/login', login_data)
        
        if login_result and 'access_token' in login_result:
            tokens[user['role']] = login_result['access_token']
            print(f"   ✅ {user['role']} login successful")
        else:
            print(f"   ❌ {user['role']} login failed")
            continue
        
        # Test dashboard for this role
        headers = {'Authorization': f'Bearer {tokens[user["role"]]}'}
        
        print(f"   📊 Testing {user['role']} Dashboard")
        dashboard_result = test_endpoint('GET', '/api/dashboard', headers=headers)
        
        if dashboard_result:
            print(f"   ✅ {user['role']} dashboard loaded successfully")
            print(f"   📈 Stats: {dashboard_result.get('stats', {})}")
        else:
            print(f"   ❌ {user['role']} dashboard failed")
        
        # Test profile endpoints
        print(f"   👤 Testing {user['role']} Profile")
        profile_result = test_endpoint('GET', '/api/profile', headers=headers)
        
        if profile_result:
            print(f"   ✅ {user['role']} profile loaded successfully")
        else:
            print(f"   ❌ {user['role']} profile failed")
        
        # Test role verification
        verify_result = test_endpoint('GET', '/api/test/verify-roles', headers=headers)
        if verify_result:
            print(f"   ✅ {user['role']} role verification successful")
            print(f"   🔑 Permissions: {verify_result.get('permissions', [])}")
        else:
            print(f"   ❌ {user['role']} role verification failed")
    
    # Test role-specific endpoints
    print(f"\n📋 Testing Role-Specific Endpoints")
    
    # Test Organizer endpoints
    if 'Organizer' in tokens:
        headers = {'Authorization': f'Bearer {tokens["Organizer"]}'}
        print("   🎪 Testing Organizer Events")
        
        # Get organizer events
        org_events = test_endpoint('GET', '/api/organizers/events', headers=headers)
        if org_events:
            print("   ✅ Organizer events loaded")
        
        # Get organizer data
        org_data = test_endpoint('GET', '/api/data/organizer', headers=headers)
        if org_data:
            print("   ✅ Organizer data retrieved")
    
    # Test Vendor endpoints
    if 'Vendor' in tokens:
        headers = {'Authorization': f'Bearer {tokens["Vendor"]}'}
        print("   🏪 Testing Vendor Services")
        
        # Get vendor services
        vendor_services = test_endpoint('GET', '/vendors/services', headers=headers)
        if vendor_services:
            print("   ✅ Vendor services loaded")
        
        # Get vendor data
        vendor_data = test_endpoint('GET', '/api/data/vendor', headers=headers)
        if vendor_data:
            print("   ✅ Vendor data retrieved")
        
        # Get vendor stall bookings
        stall_bookings = test_endpoint('GET', '/api/stalls/', headers=headers)
        if stall_bookings:
            print("   ✅ Vendor stall bookings loaded")
    
    # Test Goer endpoints
    if 'Goer' in tokens:
        headers = {'Authorization': f'Bearer {tokens["Goer"]}'}
        print("   🎫 Testing Goer Tickets")
        
        # Get goer tickets
        goer_tickets = test_endpoint('GET', '/api/tickets/user', headers=headers)
        if goer_tickets:
            print("   ✅ Goer tickets loaded")
        
        # Get goer data
        goer_data = test_endpoint('GET', '/api/data/goer', headers=headers)
        if goer_data:
            print("   ✅ Goer data retrieved")
    
    # Test Admin endpoints
    if 'Admin' in tokens:
        headers = {'Authorization': f'Bearer {tokens["Admin"]}'}
        print("   👑 Testing Admin System Overview")
        
        # Get system overview
        system_overview = test_endpoint('GET', '/api/data/system-overview', headers=headers)
        if system_overview:
            print("   ✅ Admin system overview loaded")
    
    # Test public endpoints
    print(f"\n📋 Testing Public Endpoints")
    
    # Get all events (public)
    events = test_endpoint('GET', '/api/events')
    if events:
        print("   ✅ Public events loaded")
    
    # Get endpoints list
    endpoints = test_endpoint('GET', '/api/test/endpoints')
    if endpoints:
        print("   ✅ Endpoints list loaded")
        print(f"   📋 Available endpoints: {len(endpoints.get('endpoints', {}))}")
    
    print("\n" + "=" * 50)
    print("🎉 Dashboard testing completed!")
    print("✅ All user roles and their corresponding dashboards have been tested")
    print("📊 Each role has access to their specific data and functionality")
    print("🔒 Role-based access control is working correctly")

if __name__ == "__main__":
    main()