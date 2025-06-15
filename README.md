# WatchLog Insights

A data-driven YouTube watching habit analysis tool that helps users understand their viewing patterns and make more conscious media consumption decisions through **real YouTube API integration** and enhanced mock data.

## 🚀 Features

- **🔐 Google OAuth2 Integration**: Secure login with Google account
- **📊 Real YouTube Data**: Fetches actual channel info, subscriptions, playlists, and categories
- **📈 Interactive Dashboard**: Visualize your watching patterns with charts and metrics
- **🎯 Category Breakdown**: See which content categories you spend most time on
- **📺 Channel Insights**: Discover your most-watched channels (from your subscriptions)
- **📅 Daily Patterns**: Understand your weekly watching behavior
- **⏱️ Time Range Filtering**: Analyze data for different time periods (7, 30, 90 days)
- **🔄 Data Sync**: Manual sync button to refresh YouTube data
- **📱 Responsive Design**: Works perfectly on desktop and mobile

## 🎯 Data Sources

### Real Data (from YouTube API)
- ✅ **Channel Information**: Your YouTube channel details
- ✅ **Subscriptions**: Channels you subscribe to
- ✅ **Playlists**: Your created playlists and their videos
- ✅ **Video Categories**: Official YouTube categories
- ✅ **Video Metadata**: Titles, descriptions, categories from your playlists

### Simulated Data (for MVP demonstration)
- 🎭 **Watch History**: Due to YouTube API privacy restrictions
- 🎭 **Watch Times**: Simulated viewing durations
- 🎭 **View Timestamps**: Simulated viewing dates/times

> **Note**: YouTube Data API v3 doesn't provide access to personal watch history for privacy reasons. The app uses your real subscription and playlist data combined with simulated viewing patterns to create realistic analytics.

## 🏗️ Project Structure

```
watchlog/
├── backend/                    # FastAPI backend server
│   ├── main.py                # Main API server with YouTube integration
│   ├── auth.py                # OAuth2 authentication logic
│   └── env.example           # Environment variables template
├── frontend/                  # Next.js frontend
│   ├── app/                  # Next.js app directory
│   │   ├── dashboard/        # Main dashboard page
│   │   └── login/           # OAuth login page
│   └── package.json         # Node.js dependencies
├── documentation/            # Project documentation
│   ├── PRD.md               # Product Requirements Document
│   └── DATA_SOURCES.md      # Data sources documentation
└── OAUTH_SETUP.md           # OAuth setup guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- Google Cloud Console account (for YouTube API access)

### 1. OAuth2 Setup

First, follow the **[OAuth Setup Guide](OAUTH_SETUP.md)** to:
1. Create Google Cloud Console project
2. Enable YouTube Data API v3
3. Configure OAuth2 credentials
4. Set up OAuth consent screen

### 2. Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   # or with pip: pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your Google OAuth2 credentials
   ```

4. **Start the backend server:**
   ```bash
   python main.py
   ```

   The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

### 4. Using the Application

1. Open `http://localhost:3000`
2. Click "Sign in with Google"
3. Complete OAuth2 authorization
4. View your personalized YouTube insights dashboard
5. Click "Sync Data" to refresh with latest YouTube information

## 🔌 API Endpoints

### Authentication Endpoints
- `GET /api/auth/login` - Get Google OAuth2 authorization URL
- `GET /api/auth/callback` - Handle OAuth2 callback
- `GET /api/auth/me` - Get current user information
- `POST /api/auth/refresh` - Refresh access token

### Protected Endpoints (require authentication)
- `GET /api/dashboard?days={number}` - Get dashboard data
- `GET /api/videos?days={number}&limit={number}` - Get video data
- `GET /api/categories` - Get video categories (real from YouTube API)
- `POST /api/sync-youtube-data` - Sync YouTube data

### Example API Response

```json
{
  "total_watch_time": 1200,
  "daily_average": 40.0,
  "top_category": "Science & Technology",
  "category_breakdown": [
    {
      "category": "Science & Technology", 
      "minutes": 300,
      "percentage": 25.0
    }
  ],
  "top_channels": [
    {
      "channel": "Real Subscribed Channel",
      "minutes": 120
    }
  ],
  "daily_pattern": [
    {
      "day": "Monday", 
      "minutes": 60
    }
  ]
}
```

## ✅ Features Implemented

### 🎯 MVP Features (from PRD)

1. **✅ YouTube Account Integration**: Google OAuth2 with YouTube readonly scope
2. **✅ Real Data Synchronization**: Fetches actual user data from YouTube API
3. **✅ Enhanced Mock Data**: Combines real channel/category data with simulated viewing
4. **✅ Data Analysis Dashboard**: Complete analytics with real and simulated data
5. **✅ Manual Sync**: User-triggered data synchronization
6. **✅ Transparent Data Sources**: Clear indication of real vs simulated data

### 🎨 UI/UX Features

- **🔐 Secure Authentication**: OAuth2 flow with proper token management
- **📱 Responsive Design**: Works on desktop and mobile
- **🎨 Modern UI**: Clean, professional design with Tailwind CSS
- **📊 Interactive Charts**: Hover tooltips and responsive visualizations
- **⏳ Loading States**: Proper loading and error handling
- **🔄 Sync Notifications**: Clear feedback on data synchronization status
- **ℹ️ Data Transparency**: Information panel explaining data sources
- **🕐 Time Formatting**: Human-readable time display (hours and minutes)

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API docs
- **Google APIs Client**: YouTube Data API v3 integration
- **OAuth2**: Google OAuth2 authentication
- **Pydantic**: Data validation and serialization
- **python-jose**: JWT token handling
- **Uvicorn**: ASGI server

### Frontend
- **Next.js 14**: React framework with app router
- **TypeScript**: Type safety throughout the application
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Beautiful, responsive chart library
- **Axios**: HTTP client for API communication
- **Lucide React**: Comprehensive icon library

## 📚 Documentation

- **[Product Requirements Document](documentation/PRD.md)**: Complete MVP specification
- **[OAuth Setup Guide](OAUTH_SETUP.md)**: Step-by-step OAuth2 configuration
- **[Data Sources Documentation](documentation/DATA_SOURCES.md)**: Detailed explanation of real vs mock data

## 🔄 Data Synchronization

The application intelligently combines real YouTube data with simulated analytics:

1. **Real Data Collection**: Fetches your actual subscriptions, playlists, channel info
2. **Enhanced Simulation**: Uses real channel names and categories in mock viewing data
3. **Graceful Fallback**: Falls back to full mock data if API calls fail
4. **User Transparency**: Always informs users about data sources

## 🚧 Known Limitations

- **Watch History**: YouTube API doesn't provide access to personal watch history
- **Actual View Times**: Real viewing durations are not available via API
- **Privacy Restrictions**: Some YouTube data is intentionally restricted for user privacy

## 🔮 Future Enhancements

### Post-MVP Features (from PRD)
- **📈 Advanced Analytics**: Time-based patterns, repeat viewing analysis
- **🎯 Goal Setting**: Daily/weekly viewing time goals with tracking
- **🤖 Auto Sync**: Background data synchronization
- **🏷️ Custom Tags**: User-defined video categorization
- **📊 Diagnostic Insights**: AI-powered viewing pattern analysis

### Alternative Data Sources
- **📥 Google Takeout**: Import actual watch history from Google data export
- **🔌 Browser Extension**: Client-side viewing time tracking
- **📝 Manual Entry**: User-input viewing data for accurate analytics

## 🤝 Contributing

This project was developed as a 1-person MVP but is structured for easy extension. Key areas for contribution:
- Additional YouTube API data integration
- Alternative data source implementations
- Advanced analytics features
- UI/UX improvements

## 📄 License

This project is for educational and personal use. Please respect YouTube's Terms of Service and API usage policies.

---

**Built with ❤️ for conscious media consumption** 