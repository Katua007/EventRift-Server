# EventRift Server 

Welcome to EventRift Server - the powerful backend that brings events to life! This Flask-based API serves as the backbone for the EventRift platform, handling everything from user authentication to event management with style and efficiency.

##  What is EventRift?

EventRift is a comprehensive event management platform that connects event organizers with attendees. Think of it as the bridge between amazing events and the people who want to experience them. Our server handles all the heavy lifting - user management, event creation, ticket booking, payments, and much more.

##  Features That Make Us Special

###  Authentication & Authorization
- **JWT-based authentication** - Secure and stateless
- **Role-based access control** - Organizers, Attendees, and Admins each have their place
- **Password hashing** - Your secrets stay secret

### Event Management
- **Create and manage events** - From concerts to conferences
- **Image uploads via Cloudinary** - Because every event needs a face
- **Event categorization** - Keep things organized
- **Pagination support** - Handle thousands of events smoothly
- **Status management** - Active, Draft, Cancelled - we've got you covered

###  Ticketing System
- **Multiple ticket types** - VIP, General, Early Bird - you name it
- **Inventory management** - Never oversell again
- **Booking confirmations** - Peace of mind for everyone

### Payment Integration
- **M-Pesa integration** - Because we're proudly Kenyan
- **Secure payment processing** - Your money is safe with us
- **Transaction tracking** - Every penny accounted for

###  Vendor & Stall Management
- **Vendor registration** - Food trucks, merchandise, services
- **Stall booking system** - Prime locations for everyone
- **Service categorization** - Find exactly what you need

### Communication
- **Email notifications** - Stay in the loop
- **Real-time updates** - Know what's happening when it happens

## Tech Stack

We've chosen our tools carefully to ensure reliability, scalability, and developer happiness:

- **Flask** - The lightweight Python web framework that just works
- **Flask-RESTful** - RESTful API development made simple
- **SQLAlchemy** - Database ORM that speaks your language
- **PostgreSQL** - Robust, reliable database for production
- **Flask-JWT-Extended** - JWT authentication with all the bells and whistles
- **Marshmallow** - Data serialization and validation that doesn't judge
- **Cloudinary** - Image management in the cloud
- **Flask-CORS** - Cross-origin requests without the headaches
- **Gunicorn** - Production-ready WSGI server

## Project Structure

```
EventRift-Server/
├── eventrift/                 # Main application package
│   ├── models/               # Database models
│   │   ├── user.py          # User model with roles
│   │   ├── event.py         # Event model with all the details
│   │   ├── ticket_attendance.py  # Ticketing system
│   │   ├── stall_booking.py # Vendor stall management
│   │   └── vendor_service.py # Vendor services
│   ├── routes/              # API endpoints
│   │   ├── auth_routes.py   # Authentication endpoints
│   │   ├── event_routes.py  # Event management
│   │   ├── ticket_routes.py # Ticketing system
│   │   ├── user_routes.py   # User management
│   │   ├── vendor_routes.py # Vendor operations
│   │   └── payments_routes.py # Payment processing
│   ├── schemas/             # Data validation schemas
│   │   ├── event_schema.py  # Event data validation
│   │   ├── pagination_schema.py # Pagination helpers
│   │   └── ticket_schemas.py # Ticket validation
│   ├── utils/               # Utility functions
│   │   ├── cloudinary_upload.py # Image upload handling
│   │   ├── email_service.py # Email notifications
│   │   └── daraja_api.py    # M-Pesa integration
│   ├── config.py           # Configuration management
│   └── extensions.py       # Flask extensions setup
├── app.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # You are here!
```

##  Getting Started

### Prerequisites

Before you dive in, make sure you have:
- Python 3.8+ (because we like modern features)
- PostgreSQL (for production-grade data storage)
- A Cloudinary account (for image magic)
- M-Pesa developer account (for payments)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Katua007/EventRift-Server.git
   cd EventRift-Server
   ```

2. **Create a virtual environment** (trust us, you want this)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Database
   DATABASE_URL=postgresql://username:password@localhost/eventrift_db
   
   # JWT Secret (make it strong!)
   JWT_SECRET_KEY=your-super-secret-jwt-key
   SECRET_KEY=your-flask-secret-key
   
   # Cloudinary (for image uploads)
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   
   # M-Pesa (for payments)
   MPESA_CONSUMER_KEY=your-consumer-key
   MPESA_CONSUMER_SECRET=your-consumer-secret
   MPESA_SHORTCODE=your-shortcode
   MPESA_PASSKEY=your-passkey
   
   # Email (for notifications)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the server**
   ```bash
   python app.py
   ```

Your server will be running at `http://localhost:5555` 

##  API Endpoints

### Authentication
- `POST /api/auth/register` - Create a new account
- `POST /api/auth/login` - Sign in to your account
- `POST /api/auth/logout` - Sign out securely

### Events
- `GET /api/events` - List all active events (with pagination!)
- `GET /api/events/<id>` - Get event details
- `POST /api/events` - Create a new event (Organizers only)
- `PUT /api/events/<id>` - Update event details
- `DELETE /api/events/<id>` - Remove an event

### Tickets
- `GET /api/tickets` - List available tickets
- `POST /api/tickets/book` - Book tickets for an event
- `GET /api/tickets/my-bookings` - View your bookings

### Payments
- `POST /api/payments/mpesa` - Process M-Pesa payment
- `GET /api/payments/status/<id>` - Check payment status

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile information

##  Configuration

The application supports multiple environments:

- **Development** - SQLite database, debug mode enabled
- **Production** - PostgreSQL database, optimized for performance
- **Testing** - In-memory database for fast tests

Environment variables control the behavior:
- `FLASK_ENV` - Set to 'development' or 'production'
- `DATABASE_URL` - Database connection string
- `JWT_SECRET_KEY` - Secret for JWT token signing

##  Deployment

### Render Deployment (Recommended)

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy with these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Python Version**: 3.8+

### Manual Deployment

1. **Set up production database**
   ```bash
   # Create PostgreSQL database
   createdb eventrift_production
   ```

2. **Set production environment variables**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@host/eventrift_production
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## Testing

We believe in code that works, so we test everything:

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=eventrift

# Run specific test file
python -m pytest tests/test_events.py
```

## Datuthentication & Authorization
- **JWT-based authentication** - Secure and stateless
- **Role-based access control** - Organizers, Attendees, and Admins each have their place
- **Password hashing** - Your secrets stay secret

### abase Schema

Our database is designed for scalability and performance:

### Users Table
- Stores user information with role-based access
- Supports Organizers, Attendees, and Admins

### Events Table
- Complete event information with status tracking
- Supports image uploads and categorization

### Tickets Table
- Flexible ticketing system with inventory management
- Supports multiple ticket types per event

### Bookings Table
- Tracks all ticket purchases and attendance
- Integrates with payment processing

##  Security Features

Security isn't an afterthought - it's built in:

- **JWT Authentication** - Stateless and secure
- **Password Hashing** - Using industry-standard bcrypt
- **CORS Protection** - Controlled cross-origin access
- **Input Validation** - Marshmallow schemas validate all input
- **SQL Injection Prevention** - SQLAlchemy ORM protects us
- **Rate Limiting** - Prevents abuse and DoS attacks

## Contributing

We love contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** (because untested code is broken code)
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Style

We follow PEP 8 with a few additions:
- Line length: 88 characters (Black formatter)
- Use type hints where possible
- Write docstrings for all public functions
- Keep functions small and focused

##  Troubleshooting

### Common Issues

**Database Connection Errors**
- Check your DATABASE_URL environment variable
- Ensure PostgreSQL is running
- Verify database credentials

**CORS Errors**
- Check that your frontend URL is in the CORS origins list
- Ensure you're using the correct protocol (http/https)

**JWT Token Issues**
- Verify JWT_SECRET_KEY is set
- Check token expiration settings
- Ensure proper token format in requests

**Image Upload Failures**
- Verify Cloudinary credentials
- Check file size limits
- Ensure supported file formats

### Getting Help

- Check the [Issues](https://github.com/Katua007/EventRift-Server/issues) page
- Join our community discussions
- Contact the maintainers

##  Performance

We've optimized for performance:
- **Database indexing** on frequently queried fields
- **Pagination** for large datasets
- **Caching** for static content
- **Connection pooling** for database efficiency

##  Future Plans

We're always improving:
- [ ] GraphQL API support
- [ ] Real-time notifications with WebSockets
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app API enhancements
- [ ] AI-powered event recommendations

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- The Flask community for an amazing framework
- Our beta testers who found all the bugs we missed
- Coffee, for making this all possible ☕

##  Contact

- **Project Maintainer**: [Katua007](https://github.com/Katua007)
- **Email**: support@eventrift.com
- **Website**: [EventRift](https://eventrift.com)

## TEAM 
Cyril Katua
Collins Opiayo
Muzna Mohamed
Abubakar Sheikh

---

Built in Kenya 

*Ready to create amazing events? Let's make it happen!* 