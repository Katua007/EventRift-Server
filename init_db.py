#!/usr/bin/env python3
"""
Database initialization script for EventRift
Creates SQLite database with all necessary tables and sample data
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialize the EventRift database with all tables and sample data"""
    
    # Connect to SQLite database (creates if doesn't exist)
    conn = sqlite3.connect('eventrift.db')
    cursor = conn.cursor()
    
    print("🗄️  Creating EventRift database...")
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'Goer',
            is_verified BOOLEAN DEFAULT FALSE,
            verification_token VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            date DATE NOT NULL,
            time TIME,
            location VARCHAR(200),
            theme VARCHAR(100),
            category VARCHAR(100),
            dress_code VARCHAR(100),
            ticket_price DECIMAL(10,2),
            image_url TEXT,
            organizer_id INTEGER,
            status VARCHAR(20) DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organizer_id) REFERENCES users (id)
        )
    ''')
    
    # Create Services table (for vendors)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            price DECIMAL(10,2),
            category VARCHAR(100),
            vendor_id INTEGER,
            status VARCHAR(20) DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES users (id)
        )
    ''')
    
    # Create Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            user_id INTEGER,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create Tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            user_id INTEGER,
            ticket_type VARCHAR(50),
            price DECIMAL(10,2),
            status VARCHAR(20) DEFAULT 'Active',
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    print("✅ Tables created successfully!")
    
    # Insert sample users
    sample_users = [
        ('admin', 'admin@eventrift.com', hash_password('admin123'), 'Admin'),
        ('organizer1', 'organizer@example.com', hash_password('org123'), 'Organizer'),
        ('vendor1', 'vendor@example.com', hash_password('vendor123'), 'Vendor'),
        ('goer1', 'goer@example.com', hash_password('goer123'), 'Goer'),
        ('john_doe', 'john@example.com', hash_password('password123'), 'Goer'),
        ('jane_smith', 'jane@example.com', hash_password('password123'), 'Organizer')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', sample_users)
    
    print("✅ Sample users created!")
    
    # Insert sample events
    future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    future_date2 = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
    
    sample_events = [
        ('Tech Conference 2024', 'Annual technology conference featuring latest innovations', 
         future_date, '09:00', 'Nairobi Convention Center', 'Innovation & Future', 
         'Technology', 'Business Casual', 5000.00, 'https://via.placeholder.com/400x300', 2),
        ('Music Festival Summer', 'Live music and entertainment festival', 
         future_date2, '18:00', 'Mombasa Beach Resort', 'Summer Vibes', 
         'Music', 'Casual', 3000.00, 'https://via.placeholder.com/400x300', 2),
        ('Startup Pitch Night', 'Entrepreneurs showcase their innovative startups', 
         future_date, '19:00', 'Kisumu Innovation Hub', 'Entrepreneurship', 
         'Business', 'Smart Casual', 2500.00, 'https://via.placeholder.com/400x300', 6)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO events (title, description, date, time, location, theme, 
                                    category, dress_code, ticket_price, image_url, organizer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_events)
    
    print("✅ Sample events created!")
    
    # Insert sample services
    sample_services = [
        ('Professional Catering', 'Full-service catering for events of all sizes', 
         15000.00, 'Food & Beverage', 3),
        ('Event Photography', 'Professional photography and videography services', 
         8000.00, 'Photography', 3),
        ('Sound & Lighting', 'Complete audio-visual setup for events', 
         12000.00, 'Technical Services', 3),
        ('Decoration Services', 'Beautiful event decoration and setup', 
         10000.00, 'Decoration', 3)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO services (name, description, price, category, vendor_id)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_services)
    
    print("✅ Sample services created!")
    
    # Insert sample notifications
    sample_notifications = [
        ('event_created', 'New event "Tech Conference 2024" has been created', 2),
        ('service_added', 'New service "Professional Catering" has been added', 3),
        ('event_updated', 'Event "Music Festival Summer" has been updated', 2)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO notifications (type, message, user_id)
        VALUES (?, ?, ?)
    ''', sample_notifications)
    
    print("✅ Sample notifications created!")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("🎉 EventRift database initialized successfully!")
    print("📊 Database contains:")
    print("   • 6 sample users (Admin, Organizer, Vendor, Goers)")
    print("   • 3 sample events")
    print("   • 4 sample services")
    print("   • 3 sample notifications")
    print("   • Ready for tickets and bookings")
    print()
    print("🔑 Login credentials:")
    print("   Admin: admin@eventrift.com / admin123")
    print("   Organizer: organizer@example.com / org123")
    print("   Vendor: vendor@example.com / vendor123")
    print("   Goer: goer@example.com / goer123")

if __name__ == '__main__':
    init_database()