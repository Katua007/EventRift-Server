#!/usr/bin/env python3
"""
Final validation test for EventRift Server
"""

import requests
import time

BASE_URL = "https://eventrift-server.onrender.com"

def test_complete_user_flow():
    """Test complete user journey"""
    print("🎯 Testing Complete User Flow")
    print("=" * 50)
    
    # 1. Login
    start = time.time()
    login_response = requests.post(f"{BASE_URL}/api/auth/login", 
                                 json={'email': 'user@example.com', 'password': 'test'})
    login_time = time.time() - start
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        print(f"✅ Login: {login_time:.2f}s")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. Get Events
        start = time.time()
        events_response = requests.get(f"{BASE_URL}/api/events")
        events_time = time.time() - start
        
        if events_response.status_code == 200:
            events = events_response.json()['events']
            print(f"✅ Events List: {events_time:.2f}s ({len(events)} events)")
            
            if events:
                # 3. Book Ticket
                start = time.time()
                booking_response = requests.post(f"{BASE_URL}/api/tickets/book",
                                               json={'event_id': events[0]['id'], 'quantity': 1},
                                               headers=headers)
                booking_time = time.time() - start
                
                if booking_response.status_code == 201:
                    print(f"✅ Ticket Booking: {booking_time:.2f}s")
                    
                    # 4. Check Dashboard
                    start = time.time()
                    dashboard_response = requests.get(f"{BASE_URL}/api/dashboard/goer", headers=headers)
                    dashboard_time = time.time() - start
                    
                    if dashboard_response.status_code == 200:
                        print(f"✅ Dashboard: {dashboard_time:.2f}s")
                        
                        total_time = login_time + events_time + booking_time + dashboard_time
                        print(f"\n🎉 Complete Flow: {total_time:.2f}s")
                        print(f"📊 Average Response: {total_time/4:.2f}s")
                        
                        if total_time < 5.0:
                            print("🚀 Performance: EXCELLENT")
                        elif total_time < 8.0:
                            print("✅ Performance: GOOD")
                        else:
                            print("⚠️  Performance: NEEDS IMPROVEMENT")

if __name__ == "__main__":
    test_complete_user_flow()