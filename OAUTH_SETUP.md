# OAuth2 Setup Guide for WatchLog Insights

This guide will help you set up OAuth2 authentication with Google/YouTube for the WatchLog Insights application.

## Prerequisites

1. A Google Cloud Platform account
2. Python 3.13+ installed
3. Node.js 18+ installed

## Step 1: Google Cloud Console Setup

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - YouTube Data API v3
   - Google+ API (if available)

### 1.2 Configure OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Configure the following:
   - **Name**: WatchLog Insights
   - **Authorized JavaScript origins**: `http://localhost:3000`
   - **Authorized redirect URIs**: `http://localhost:3000/api/auth/callback`
5. Click "Create"
6. Copy the **Client ID** and **Client Secret**

### 1.3 Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in the required information:
   - App name: WatchLog Insights
   - User support email: Your email
   - Developer contact information: Your email
4. Add the following scopes:
   - `https://www.googleapis.com/auth/youtube.readonly`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `https://www.googleapis.com/auth/userinfo.email`
5. Add test users (your email address)
6. Save and continue

## Step 2: Backend Configuration

### 2.1 Install Dependencies

```bash
# From the project root
uv sync
```

### 2.2 Environment Variables

1. Copy the environment template:
   ```bash
   cp backend/env.example backend/.env
   ```

2. Edit `backend/.env` and add your Google OAuth2 credentials:
   ```env
   GOOGLE_CLIENT_ID=your_actual_client_id
   GOOGLE_CLIENT_SECRET=your_actual_client_secret
   JWT_SECRET_KEY=your_secure_jwt_secret_key
   ```

### 2.3 Start the Backend Server

```bash
# From the project root
cd backend
python main.py
```

The backend will be available at `http://localhost:8000`

## Step 3: Frontend Configuration

### 3.1 Install Dependencies

```bash
# From the project root
cd frontend
npm install
```

### 3.2 Start the Frontend Server

```bash
# From the frontend directory
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Step 4: Testing the Authentication

1. Open `http://localhost:3000` in your browser
2. You should be redirected to the login page
3. Click "Sign in with Google"
4. Complete the OAuth2 flow
5. You should be redirected to the dashboard with your YouTube insights

## API Endpoints

### Authentication Endpoints

- `GET /api/auth/login` - Get Google OAuth2 authorization URL
- `GET /api/auth/callback` - Handle OAuth2 callback and exchange code for tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user information

### Protected Endpoints (require authentication)

- `GET /api/dashboard` - Get dashboard data
- `GET /api/videos` - Get video data
- `GET /api/categories` - Get video categories
- `POST /api/sync-youtube-data` - Sync YouTube data

## Security Notes

1. **JWT Secret**: Use a strong, random secret key for JWT_SECRET_KEY
2. **HTTPS**: In production, always use HTTPS
3. **Environment Variables**: Never commit `.env` files to version control
4. **Token Storage**: In production, use a secure database instead of in-memory storage
5. **CORS**: Configure CORS properly for production domains

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI" error**
   - Make sure the redirect URI in Google Cloud Console matches exactly: `http://localhost:3000/api/auth/callback`

2. **"OAuth consent screen not configured" error**
   - Complete the OAuth consent screen setup in Google Cloud Console
   - Add your email as a test user

3. **"YouTube Data API not enabled" error**
   - Enable YouTube Data API v3 in Google Cloud Console

4. **CORS errors**
   - Make sure the backend CORS configuration includes `http://localhost:3000`

### Debug Mode

To enable debug logging, add this to your backend `.env`:
```env
DEBUG=true
```

## Production Deployment

For production deployment, you'll need to:

1. Update the OAuth2 redirect URIs to your production domain
2. Use a proper database for token storage
3. Configure HTTPS
4. Set up proper CORS for your production domain
5. Use environment-specific configuration
6. Implement proper error handling and logging

## Support

If you encounter issues, check:
1. Google Cloud Console logs
2. Backend server logs
3. Browser developer console
4. Network tab for API requests 