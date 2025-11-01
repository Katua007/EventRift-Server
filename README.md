# EventRift Server

A Flask-based backend server for the EventRift event management platform.

## Environment Variables

### Required Environment Variables

- `FRONTEND_URL`: The URL of the frontend application that will connect to this server. This is used for CORS configuration.
  - **Production**: Set to `https://event-rift-client.vercel.app`
  - **Development**: Can be set to your local frontend URL (e.g., `http://localhost:5174`)

### Setting FRONTEND_URL on Render

1. Go to your Render dashboard
2. Select your EventRift Server service
3. Navigate to the "Environment" tab
4. Add a new environment variable:
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://event-rift-client.vercel.app`
5. Save and redeploy the service

### Other Environment Variables

- `DATABASE_URL`: Database connection string (automatically set by Render for PostgreSQL)
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `SECRET_KEY`: Flask secret key for session management

## CORS Configuration

The server is configured to handle CORS preflight requests properly:
- Only allows requests from the specified `FRONTEND_URL`
- Supports credentials (cookies)
- Allows common headers: `Content-Type`, `Authorization`, `X-Requested-With`, `Accept`
- Allows methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`
- Returns HTTP 204 status for OPTIONS preflight requests

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables in `.env` file:
   ```
   FRONTEND_URL=http://localhost:5174
   JWT_SECRET_KEY=your-dev-secret
   SECRET_KEY=your-dev-secret
   ```

3. Run the server:
   ```bash
   python app.py
   ```

The server will run on port 5555 by default.

## Deployment

The server is configured for deployment on Render using the `render.yaml` configuration file.