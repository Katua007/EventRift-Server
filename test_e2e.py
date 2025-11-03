#!/usr/bin/env python3
"""
End-to-End Test Suite for EventRift Server
Tests all major functionality including auth, events, dashboard, and tickets
"""

import requests
import json
import time

BASE_URL = "https://eventrift-server.onrender.com"

class EventRiftE2ETest:
    def __init__(self):
        self.token = None
        self.user_data = None
        self.test_results = []

    def log_test(self, test_name, success, message="", response_time=0):
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'time': f"{response_time:.2f}s"
        })
        print(f"{status} {test_name} ({response_time:.2f}s) - {message}")

    def test_health_check(self):
        """Test server health endpoint"""
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}", end - start)
                return True
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}", end - start)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {e}")
            return False

    def test_login(self):
        """Test user login functionality"""
        try:
            start = time.time()
            login_data = {
                'email': 'test@example.com',
                'password': 'password123'
            }
            
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('access_token'):
                    self.token = data['access_token']
                    self.user_data = data.get('user', {})
                    self.log_test("User Login", True, f"User: {self.user_data.get('email')}", end - start)
                    return True
            
            self.log_test("User Login", False, f"Status: {response.status_code}", end - start)
            return False
        except Exception as e:
            self.log_test("User Login", False, f"Error: {e}")
            return False

    def test_profile(self):
        """Test user profile retrieval"""
        if not self.token:
            self.log_test("User Profile", False, "No token available")
            return False
            
        try:
            start = time.time()
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers, timeout=10)
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user = data.get('user', {})
                    self.log_test("User Profile", True, f"ID: {user.get('id')}, Role: {user.get('role')}", end - start)
                    return True
            
            self.log_test("User Profile", False, f"Status: {response.status_code}", end - start)
            return False
        except Exception as e:
            self.log_test("User Profile", False, f"Error: {e}")
            return False

    def test_events_list(self):
        """Test events listing"""
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/api/events", timeout=10)
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    events = data.get('events', [])
                    self.log_test("Events List", True, f"Found {len(events)} events", end - start)
                    return events
            
            self.log_test("Events List", False, f"Status: {response.status_code}", end - start)
            return []
        except Exception as e:
            self.log_test("Events List", False, f"Error: {e}")
            return []

    def test_event_detail(self, event_id):
        """Test individual event retrieval"""
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/api/events/{event_id}", timeout=10)
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    event = data.get('event', {})
                    self.log_test("Event Detail", True, f"Event: {event.get('title')}", end - start)
                    return event
            
            self.log_test("Event Detail", False, f"Status: {response.status_code}", end - start)
            return None
        except Exception as e:
            self.log_test("Event Detail", False, f"Error: {e}")
            return None

    def test_ticket_booking(self, event_id):
        """Test ticket booking functionality"""
        if not self.token:
            self.log_test("Ticket Booking", False, "No token available")
            return False
            
        try:
            start = time.time()
            headers = {'Authorization': f'Bearer {self.token}'}
            booking_data = {
                'event_id': event_id,
                'quantity': 2,
                'user_email': 'test@example.com'
            }
            
            response = requests.post(f"{BASE_URL}/api/tickets/book", 
                                   json=booking_data, headers=headers, timeout=10)
            end = time.time()
            
            if response.status_code == 201:
                data = response.json()
                if data.get('success'):
                    booking = data.get('booking', {})
                    self.log_test("Ticket Booking", True, 
                                f"Booked {booking.get('quantity')} tickets for KES {booking.get('total_price')}", 
                                end - start)
                    return booking
            
            self.log_test("Ticket Booking", False, f"Status: {response.status_code}", end - start)
            return None
        except Exception as e:
            self.log_test("Ticket Booking", False, f"Error: {e}")
            return None

    def test_user_tickets(self):
        """Test user tickets retrieval"""
        if not self.token:
            self.log_test("User Tickets", False, "No token available")
            return False
            
        try:
            start = time.time()
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{BASE_URL}/api/tickets/user", headers=headers, timeout=10)
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    tickets = data.get('tickets', [])
                    upcoming = data.get('upcoming_events', [])
                    self.log_test("User Tickets", True, 
                                f"{len(tickets)} total bookings, {len(upcoming)} upcoming", 
                                end - start)
                    return True
            
            self.log_test("User Tickets", False, f"Status: {response.status_code}", end - start)
            return False
        except Exception as e:
            self.log_test("User Tickets", False, f"Error: {e}")
            return False

    def test_goer_dashboard(self):
        """Test goer dashboard"""
        if not self.token:
            self.log_test("Goer Dashboard", False, "No token available")
            return False
            
        try:
            start = time.time()
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{BASE_URL}/api/dashboard/goer", headers=headers, timeout=10)
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('stats', {})
                    available = len(data.get('available_events', []))
                    self.log_test("Goer Dashboard", True, 
                                f"Stats loaded, {available} available events", 
                                end - start)
                    return True
            
            self.log_test("Goer Dashboard", False, f"Status: {response.status_code}", end - start)
            return False
        except Exception as e:
            self.log_test("Goer Dashboard", False, f"Error: {e}")
            return False

    def test_organizer_dashboard(self):
        """Test organizer dashboard"""
        if not self.token:
            self.log_test("Organizer Dashboard", False, "No token available")
            return False
            
        try:
            start = time.time()
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{BASE_URL}/api/dashboard/organizer", headers=headers, timeout=10)
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    total_events = data.get('total_events', 0)
                    revenue = data.get('total_revenue', 0)
                    self.log_test("Organizer Dashboard", True, 
                                f"{total_events} events, KES {revenue:,} revenue", 
                                end - start)
                    return True
            
            self.log_test("Organizer Dashboard", False, f"Status: {response.status_code}", end - start)
            return False
        except Exception as e:
            self.log_test("Organizer Dashboard", False, f"Error: {e}")
            return False

    def test_cors(self):
        """Test CORS configuration"""
        try:
            start = time.time()
            response = requests.options(f"{BASE_URL}/api/events", 
                                      headers={'Origin': 'https://event-rift-client.vercel.app'}, 
                                      timeout=10)
            end = time.time()
            
            if response.status_code == 204:
                self.log_test("CORS Configuration", True, "Preflight successful", end - start)
                return True
            
            self.log_test("CORS Configuration", False, f"Status: {response.status_code}", end - start)
            return False
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Error: {e}")
            return False

    def run_all_tests(self):
        """Run complete end-to-end test suite"""
        print("🚀 EventRift Server - End-to-End Test Suite")
        print("=" * 60)
        
        # Core functionality tests
        self.test_health_check()
        self.test_cors()
        
        # Authentication tests
        if self.test_login():
            self.test_profile()
        
        # Events tests
        events = self.test_events_list()
        if events:
            # Test first event detail
            event = self.test_event_detail(events[0]['id'])
            if event:
                # Test ticket booking
                booking = self.test_ticket_booking(events[0]['id'])
                if booking:
                    self.test_user_tickets()
        
        # Dashboard tests
        self.test_goer_dashboard()
        self.test_organizer_dashboard()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "PASS" in result['status'])
        total = len(self.test_results)
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']} ({result['time']}) - {result['message']}")
        
        print(f"\n🎯 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! EventRift server is fully functional.")
        else:
            print(f"⚠️  {total - passed} tests failed. Check the issues above.")

if __name__ == "__main__":
    tester = EventRiftE2ETest()
    tester.run_all_tests()