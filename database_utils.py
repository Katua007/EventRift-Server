"""
Database utility functions for EventRift
"""
import sqlite3
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('eventrift.db')
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn

def get_users():
    """Get all users from database"""
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return [dict(user) for user in users]

def get_events():
    """Get all events from database"""
    conn = get_db_connection()
    events = conn.execute('''
        SELECT e.*, u.username as organizer_name 
        FROM events e 
        LEFT JOIN users u ON e.organizer_id = u.id
        ORDER BY e.created_at DESC
    ''').fetchall()
    conn.close()
    return [dict(event) for event in events]

def get_services():
    """Get all services from database"""
    conn = get_db_connection()
    services = conn.execute('''
        SELECT s.*, u.username as vendor_name 
        FROM services s 
        LEFT JOIN users u ON s.vendor_id = u.id
        ORDER BY s.created_at DESC
    ''').fetchall()
    conn.close()
    return [dict(service) for service in services]

def get_notifications():
    """Get all notifications from database"""
    conn = get_db_connection()
    notifications = conn.execute('''
        SELECT n.*, u.username 
        FROM notifications n 
        LEFT JOIN users u ON n.user_id = u.id
        ORDER BY n.created_at DESC
    ''').fetchall()
    conn.close()
    return [dict(notification) for notification in notifications]

def create_event(event_data):
    """Create new event in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO events (title, description, date, time, location, theme, 
                          category, dress_code, ticket_price, image_url, organizer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        event_data.get('title'),
        event_data.get('description'),
        event_data.get('date'),
        event_data.get('time'),
        event_data.get('location'),
        event_data.get('theme'),
        event_data.get('category'),
        event_data.get('dress_code'),
        event_data.get('ticket_price'),
        event_data.get('image_url'),
        event_data.get('organizer_id', 2)  # Default organizer
    ))
    
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id

def create_service(service_data):
    """Create new service in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO services (name, description, price, category, vendor_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        service_data.get('name'),
        service_data.get('description'),
        service_data.get('price'),
        service_data.get('category'),
        service_data.get('vendor_id', 3)  # Default vendor
    ))
    
    service_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return service_id

def create_notification(notification_data):
    """Create new notification in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO notifications (type, message, user_id)
        VALUES (?, ?, ?)
    ''', (
        notification_data.get('type'),
        notification_data.get('message'),
        notification_data.get('user_id')
    ))
    
    notification_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return notification_id