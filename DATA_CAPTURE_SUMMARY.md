# EventRift Data Capture and Storage Summary

This document outlines how the EventRift backend system captures, stores, and retrieves data for the three main user scenarios: Organizers creating events, Vendors adding services, and Goers purchasing tickets.

## 1. Event Creation by Organizers

### Data Capture Process:
- **Route**: `POST /api/events`
- **Authentication**: JWT required
- **Model**: [`Event`](eventrift/models/event.py:4)
- **Controller**: [`EventListResource.post()`](eventrift/routes/event_routes.py:52)

### Data Stored:
```python
Event {
    id: Integer (Primary Key)
    organizer_id: Integer (Foreign Key to users.id)
    name: String(100)
    description: Text
    location: String(200)
    date_time: DateTime
    ticket_price: Numeric(10, 2)
    capacity: Integer
    image_url: String(500) - Optional Cloudinary URL
    is_published: Boolean (default: False)
    created_at: DateTime
    updated_at: DateTime
}
```

### Data Retrieval:
- **Organizer's Events**: `GET /api/organizers/events`
- **All Events**: `GET /api/events` (with pagination)
- **Comprehensive Data**: `GET /api/data/organizer` - Returns events with payment and ticket statistics

## 2. Vendor Service Addition

### Data Capture Process:
- **Route**: `POST /vendors/services`
- **Authentication**: JWT required + Vendor role
- **Model**: [`VendorService`](eventrift/models/vendor_service.py:4)
- **Controller**: [`VendorServiceListResource.post()`](eventrift/routes/vendor_routes.py:12)

### Data Stored:
```python
VendorService {
    id: Integer (Primary Key)
    vendor_id: Integer (Foreign Key to users.id)
    service_name: String(200)
    service_description: Text
    service_category: String(100)
    pricing_model: String(50) - 'per_hour', 'fixed', 'per_person'
    base_price: Float
    availability_status: String(20) - 'Available', 'Booked', 'Unavailable'
    license_status: String(20) - 'Pending', 'Verified', 'Suspended'
    licensing_document_url: String(500)
    contact_phone: String(20)
    contact_email: String(120)
    service_location: String(200)
    created_at: DateTime
    updated_at: DateTime
}
```

### Data Retrieval:
- **Vendor's Services**: `GET /vendors/services` (filtered by vendor_id)
- **All Services**: `GET /vendors/services` (Admin access)
- **Specific Vendor Services**: `GET /vendors/{vendor_id}/services`
- **Comprehensive Data**: `GET /api/data/vendor` - Returns all vendor service details

## 3. Ticket Purchase by Goers

### Data Capture Process:
The ticket purchase process involves multiple models and steps:

#### Step 1: Payment Initiation
- **Route**: `POST /api/payments/initiate`
- **Model**: [`Payment`](eventrift/models/payment.py:4)
- **Controller**: [`InitiatePaymentResource.post()`](eventrift/routes/payments_routes.py:16)

#### Step 2: Payment Callback & Ticket Creation
- **Route**: `POST /api/payments/callback` (M-Pesa callback)
- **Models**: [`Payment`](eventrift/models/payment.py:4), [`Ticket`](eventrift/models/ticket_attendance.py:7), [`Attendance`](eventrift/models/ticket_attendance.py:52)
- **Controller**: [`MpesaCallbackResource.post()`](eventrift/routes/payments_routes.py:70)

### Data Stored:

#### Payment Model:
```python
Payment {
    id: Integer (Primary Key)
    checkout_request_id: String(50) - M-Pesa reference
    merchant_request_id: String(50)
    user_id: Integer (Foreign Key to users.id)
    event_id: Integer (Foreign Key to events.id)
    amount: Float
    quantity: Integer - Number of tickets
    phone_number: String(15)
    status: String(20) - 'PENDING', 'PAID', 'FAILED', 'CANCELLED'
    mpesa_receipt_number: String(20)
    transaction_date: DateTime
    created_at: DateTime
    updated_at: DateTime
}
```

#### Ticket Model:
```python
Ticket {
    id: Integer (Primary Key)
    uuid: String(36) - Unique ticket identifier
    user_id: Integer (Foreign Key to users.id)
    event_id: Integer (Foreign Key to events.id)
    payment_id: Integer (Foreign Key to payments.id)
    status: String(20) - 'PENDING', 'PAID', 'REFUNDED'
    ticket_type: String(50) - 'General Admission'
    qr_code_data: Text - For QR code generation
    created_at: DateTime
    updated_at: DateTime
}
```

#### Attendance Model:
```python
Attendance {
    id: Integer (Primary Key)
    ticket_id: Integer (Foreign Key to tickets.id)
    is_checked_in: Boolean (default: False)
    checked_in_at: DateTime
    checked_in_by_user_id: Integer (Foreign Key to users.id)
    created_at: DateTime
}
```

### Data Retrieval:
- **User's Tickets**: `GET /api/tickets/user`
- **Specific Ticket**: `GET /api/tickets/{uuid}`
- **Comprehensive Data**: `GET /api/data/goer` - Returns payments and tickets with event details

## 4. Data Relationships and Integrity

### Database Relationships:
- **User → Events**: One-to-Many (organizer_id)
- **User → VendorServices**: One-to-Many (vendor_id)
- **User → Payments**: One-to-Many (user_id)
- **User → Tickets**: One-to-Many (user_id)
- **Event → Payments**: One-to-Many (event_id)
- **Event → Tickets**: One-to-Many (event_id)
- **Payment → Tickets**: One-to-Many (payment_id)
- **Ticket → Attendance**: One-to-One (ticket_id)

### Foreign Key Constraints:
All models use proper foreign key constraints to ensure data integrity:
- [`users.id`](eventrift/models/user.py:6) referenced by events, services, payments, tickets
- [`events.id`](eventrift/models/event.py:5) referenced by payments, tickets
- [`payments.id`](eventrift/models/payment.py:4) referenced by tickets
- [`tickets.id`](eventrift/models/ticket_attendance.py:9) referenced by attendance

## 5. Data Retrieval Endpoints

### Comprehensive Data Retrieval:
- **`GET /api/data/organizer`**: Complete organizer data with event statistics
- **`GET /api/data/vendor`**: Complete vendor data with service details
- **`GET /api/data/goer`**: Complete goer data with payments and tickets
- **`GET /api/data/system-overview`**: System-wide statistics (Admin only)

### Individual Entity Retrieval:
- **Events**: `/api/events`, `/api/organizers/events`
- **Services**: `/vendors/services`, `/vendors/{id}/services`
- **Tickets**: `/api/tickets/user`, `/api/tickets/{uuid}`
- **Payments**: Included in goer data endpoint

## 6. Data Persistence and Storage

All data is stored in a relational database (SQLite/PostgreSQL) with:
- **ACID compliance** for transaction integrity
- **Foreign key constraints** for referential integrity
- **Timestamps** for audit trails
- **Unique constraints** for critical fields (UUIDs, receipt numbers)
- **Proper indexing** on foreign keys and frequently queried fields

## 7. Security and Access Control

- **JWT Authentication** required for all data operations
- **Role-based access control** (Organizer, Vendor, Goer, Admin)
- **User isolation** - users can only access their own data
- **Admin oversight** - system-wide data access for administrators

## Summary

The EventRift backend successfully captures, stores, and provides retrieval mechanisms for:

1. ✅ **Event Creation by Organizers** - Complete event data with relationships
2. ✅ **Service Addition by Vendors** - Comprehensive service information with licensing
3. ✅ **Ticket Purchases by Goers** - Full payment flow with ticket generation and attendance tracking

All data is properly stored in the database with appropriate relationships, constraints, and can be retrieved through dedicated API endpoints for reporting, analytics, and user interfaces.