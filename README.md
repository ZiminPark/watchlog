# WatchLog Insights

A data-driven YouTube watching habit analysis tool that helps users understand their viewing patterns and make more conscious media consumption decisions.

## Features

- **YouTube Data Analysis**: Analyze your YouTube watching habits with mock data
- **Interactive Dashboard**: Visualize your watching patterns with charts and metrics
- **Category Breakdown**: See which content categories you spend most time on
- **Channel Insights**: Discover your most-watched channels
- **Daily Patterns**: Understand your weekly watching behavior
- **Time Range Filtering**: Analyze data for different time periods (7, 30, 90 days)

## Project Structure

```
watchlog/
├── backend/                 # FastAPI backend server
│   ├── main.py             # Main API server
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js app directory
│   ├── package.json       # Node.js dependencies
│   └── ...               # Next.js config files
└── README.md              # This file
```

## Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server:**
   ```bash
   python main.py
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

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

## API Endpoints

### Backend API (http://localhost:8000)

- `GET /` - API health check
- `GET /api/dashboard?days={number}` - Get dashboard data for specified days
- `GET /api/videos?days={number}&limit={number}` - Get raw video data
- `GET /api/categories` - Get available video categories

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
      "channel": "TechCrunch",
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

## Features Implemented

### ✅ MVP Features (from PRD)

1. **Mock Data Generation**: Realistic YouTube watching data with various categories and channels
2. **Data Analysis**: Automatic categorization and time calculation
3. **Dashboard Visualization**: 
   - Key metrics cards (Total time, Daily average, Top category)
   - Category breakdown pie chart
   - Top channels bar chart
   - Daily pattern analysis
   - Key insights summary

### 🎨 UI/UX Features

- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Clean, professional design with Tailwind CSS
- **Interactive Charts**: Hover tooltips and responsive charts
- **Loading States**: Proper loading and error handling
- **Time Formatting**: Human-readable time display (hours and minutes)

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Frontend
- **Next.js 14**: React framework with app router
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: React charting library
- **Axios**: HTTP client
- **Lucide React**: Icon library

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation. Visit `http://localhost:8000/docs` to see the interactive API documentation.

### Frontend Development

The frontend uses Next.js with hot reloading. Any changes to the code will automatically refresh the browser.

## Mock Data

The application currently uses mock data that includes:
- 15 different YouTube categories
- 15 popular tech/education channels
- Realistic watch times (5-120 minutes per video)
- Random distribution across time periods
- Proper data relationships and calculations

## Future Enhancements

Based on the PRD, future features could include:
- Real YouTube API integration
- User authentication with Google OAuth
- Goal setting and tracking
- Advanced analytics (time-based patterns, repeat viewing)
- Custom tagging system
- Automated data synchronization

## Contributing

This is a 1-person MVP project. The code is structured to be easily extensible for future features.

## License

This project is for educational and personal use. 