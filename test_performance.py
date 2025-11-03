#!/usr/bin/env python3
"""
Performance test script for EventRift Server
Tests login speed and dashboard functionality
"""

import requests
import time
import json

def test_login_performance():
    """Test login endpoint performance"""
    print("🔐 Testing Login Performance...")
    
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    # Test multiple login attempts to measure average time
    times = []
    for i in range(3):
        start_time = time.time()
        try:
            response = requests.post(
                'https://eventrift-server.onrender.com/api/auth/login',
                json=login_data,
                timeout=10
            )
            end_time = time.time()
            times.append(end_time - start_time)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Login {i+1}: {times[-1]:.2f}s - Success")
                return result.get('access_token')
            else:
                print(f"❌ Login {i+1}: {times[-1]:.2f}s - Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Login {i+1}: Error - {e}")
    
    avg_time = sum(times) / len(times) if times else 0
    print(f"📊 Average login time: {avg_time:.2f}s")
    return None

def test_dashboard(token):
    """Test dashboard endpoints"""
    if not token:
        print("❌ No token available for dashboard test")
        return
    
    print("\n📊 Testing Dashboard Functionality...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test goer dashboard
    try:
        start_time = time.time()
        response = requests.get(
            'https://eventrift-server.onrender.com/api/dashboard/goer',
            headers=headers,
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Goer Dashboard: {end_time - start_time:.2f}s")
            print(f"   📈 Stats: {data.get('stats', {})}")
            print(f"   🎫 Available Events: {len(data.get('available_events', []))}")
        else:
            print(f"❌ Goer Dashboard: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Goer Dashboard Error: {e}")

def test_events_endpoint():
    """Test events endpoint performance"""
    print("\n🎪 Testing Events Endpoint...")
    
    try:
        start_time = time.time()
        response = requests.get(
            'https://eventrift-server.onrender.com/api/events',
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            events_count = len(data.get('events', []))
            print(f"✅ Events Endpoint: {end_time - start_time:.2f}s")
            print(f"   🎪 Total Events: {events_count}")
        else:
            print(f"❌ Events Endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Events Endpoint Error: {e}")

if __name__ == "__main__":
    print("🚀 EventRift Server Performance Test")
    print("=" * 50)
    
    # Test login performance
    token = test_login_performance()
    
    # Test dashboard functionality
    test_dashboard(token)
    
    # Test events endpoint
    test_events_endpoint()
    
    print("\n✅ Performance test completed!")