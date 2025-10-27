# EventRift Backend-Frontend Integration

## 🔗 **Integration Status: READY**

Your backend is now configured to work seamlessly with your Vercel frontend at:
**https://event-rift-client.vercel.app**

## 🌐 **API Endpoints**

### Base URL
- **Development**: `http://localhost:5000`
- **Production**: `https://your-render-app.onrender.com`

### Authentication
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "email": "user@example.com",
    "role": "user"
  }
}
```

### Events
```http
GET /api/events

Response:
{
  "success": true,
  "events": [
    {
      "id": 1,
      "title": "Tech Conference 2024",
      "date": "2024-06-15",
      "location": "Nairobi"
    }
  ]
}
```

### Health Check
```http
GET /api/health

Response:
{
  "status": "healthy",
  "message": "EventRift API is running"
}
```

### CORS Test
```http
GET /api/test

Response:
{
  "success": true,
  "message": "CORS is working!",
  "frontend_url": "https://event-rift-client.vercel.app"
}
```

## 🔧 **CORS Configuration**

✅ **Allowed Origins:**
- `http://localhost:3000` (React dev)
- `http://localhost:5173` (Vite dev)
- `https://event-rift-client.vercel.app` (Production)
- `https://*.vercel.app` (Vercel previews)

✅ **Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS
✅ **Allowed Headers:** Content-Type, Authorization
✅ **Credentials Support:** Enabled

## 📱 **Frontend Integration Code**

### JavaScript/React Example
```javascript
// API Base URL
const API_BASE_URL = 'https://your-render-app.onrender.com';

// Login function
async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  if (data.success) {
    localStorage.setItem('token', data.access_token);
    return data.user;
  }
  throw new Error(data.message);
}

// Get events function
async function getEvents() {
  const response = await fetch(`${API_BASE_URL}/api/events`);
  const data = await response.json();
  return data.events;
}

// Authenticated request example
async function makeAuthenticatedRequest(url) {
  const token = localStorage.getItem('token');
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  return response.json();
}
```

## 🚀 **Deployment Status**

✅ **Backend**: Ready for Render deployment
✅ **CORS**: Configured for Vercel frontend
✅ **API Routes**: Working and tested
✅ **Authentication**: JWT tokens ready
✅ **Error Handling**: Proper HTTP status codes

## 🔄 **Next Steps**

1. **Deploy Backend to Render**:
   ```bash
   git add .
   git commit -m "Backend ready for frontend integration"
   git push origin main
   ```

2. **Update Frontend API URLs**:
   - Replace localhost URLs with your Render deployment URL
   - Test CORS with: `GET /api/test`

3. **Test Integration**:
   - Login from frontend should work
   - Events should load from backend
   - CORS headers should be present

Your backend and frontend are now ready to communicate seamlessly! 🎉