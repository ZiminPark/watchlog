from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Import authentication module
from auth import (
    get_authorization_url,
    exchange_code_for_tokens,
    create_access_token,
    get_current_user,
    TokenData,
    get_youtube_service,
    refresh_access_token,
)


app = FastAPI(title="WatchLog Insights API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class VideoData(BaseModel):
    video_id: str
    title: str
    channel_name: str
    category_id: int
    category_name: str
    watch_time_minutes: int
    watched_at: datetime


class DashboardData(BaseModel):
    total_watch_time: int
    daily_average: float
    top_category: str
    category_breakdown: List[dict]
    top_channels: List[dict]
    daily_pattern: List[dict]


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# In-memory storage for user tokens (in production, use a database)
user_tokens = {}


# Mock data generation
def generate_mock_videos(days: int = 30) -> List[VideoData]:
    categories = [
        (1, "Film & Animation"),
        (2, "Autos & Vehicles"),
        (10, "Music"),
        (15, "Pets & Animals"),
        (17, "Sports"),
        (19, "Travel & Events"),
        (20, "Gaming"),
        (22, "People & Blogs"),
        (23, "Comedy"),
        (24, "Entertainment"),
        (25, "News & Politics"),
        (26, "Howto & Style"),
        (27, "Education"),
        (28, "Science & Technology"),
        (29, "Nonprofits & Activism"),
    ]

    channels = [
        "TechCrunch",
        "Verge",
        "Marques Brownlee",
        "Linus Tech Tips",
        "Kurzgesagt",
        "CGP Grey",
        "Vsauce",
        "Numberphile",
        "Tom Scott",
        "Computerphile",
        "3Blue1Brown",
        "Veritasium",
        "CrashCourse",
        "Khan Academy",
        "MIT OpenCourseWare",
    ]

    videos = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for i in range(random.randint(50, 150)):
        category_id, category_name = random.choice(categories)
        channel_name = random.choice(channels)
        watch_time = random.randint(5, 120)
        watched_at = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )

        video = VideoData(
            video_id=f"video_{i}",
            title=f"Sample Video {i} by {channel_name}",
            channel_name=channel_name,
            category_id=category_id,
            category_name=category_name,
            watch_time_minutes=watch_time,
            watched_at=watched_at,
        )
        videos.append(video)

    return videos


def analyze_watch_data(videos: List[VideoData]) -> DashboardData:
    # Calculate total watch time
    total_watch_time = sum(video.watch_time_minutes for video in videos)

    # Calculate daily average
    if videos:
        date_range = max(video.watched_at for video in videos) - min(
            video.watched_at for video in videos
        )
        days = max(1, date_range.days + 1)
        daily_average = total_watch_time / days
    else:
        daily_average = 0

    # Category breakdown
    category_times = {}
    for video in videos:
        if video.category_name not in category_times:
            category_times[video.category_name] = 0
        category_times[video.category_name] += video.watch_time_minutes

    category_breakdown = [
        {
            "category": cat,
            "minutes": time,
            "percentage": (
                (time / total_watch_time * 100) if total_watch_time > 0 else 0
            ),
        }
        for cat, time in sorted(
            category_times.items(), key=lambda x: x[1], reverse=True
        )
    ]

    # Top category
    top_category = (
        category_breakdown[0]["category"] if category_breakdown else "No data"
    )

    # Top channels
    channel_times = {}
    for video in videos:
        if video.channel_name not in channel_times:
            channel_times[video.channel_name] = 0
        channel_times[video.channel_name] += video.watch_time_minutes

    top_channels = [
        {"channel": channel, "minutes": time}
        for channel, time in sorted(
            channel_times.items(), key=lambda x: x[1], reverse=True
        )[:5]
    ]

    # Daily pattern
    daily_pattern = []
    for i in range(7):
        day_name = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ][i]
        day_videos = [v for v in videos if v.watched_at.weekday() == i]
        day_total = sum(v.watch_time_minutes for v in day_videos)
        daily_pattern.append({"day": day_name, "minutes": day_total})

    return DashboardData(
        total_watch_time=total_watch_time,
        daily_average=round(daily_average, 1),
        top_category=top_category,
        category_breakdown=category_breakdown,
        top_channels=top_channels,
        daily_pattern=daily_pattern,
    )


# Authentication endpoints
@app.get("/api/auth/login")
async def login():
    """Get Google OAuth2 authorization URL"""
    try:
        auth_url = get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate auth URL: {str(e)}"
        )


@app.get("/api/auth/callback")
async def auth_callback(code: str):
    """Handle OAuth2 callback and exchange code for tokens"""
    try:
        # Exchange authorization code for tokens
        user_info = exchange_code_for_tokens(code)

        # Create JWT access token
        access_token = create_access_token(
            data={
                "sub": user_info.id,
                "email": user_info.email,
                "name": user_info.name,
                "picture": user_info.picture,
            }
        )

        # Store user tokens (in production, use a database)
        user_tokens[user_info.id] = {
            "access_token": user_info.access_token,
            "refresh_token": user_info.refresh_token,
            "token_expiry": (
                user_info.token_expiry.isoformat() if user_info.token_expiry else None
            ),
        }

        # Redirect to frontend with token
        frontend_url = "http://localhost:3000"
        return RedirectResponse(
            url=f"{frontend_url}/dashboard?token={access_token}&user={user_info.id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.post("/api/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        result = refresh_access_token(request.refresh_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")


@app.get("/api/auth/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
    }


# Protected API endpoints
@app.get("/")
async def root():
    return {"message": "WatchLog Insights API", "version": "1.0.0"}


@app.get("/api/dashboard")
async def get_dashboard(
    days: int = 30, current_user: TokenData = Depends(get_current_user)
):
    """Get dashboard data for the specified number of days"""
    try:
        videos = generate_mock_videos(days)
        dashboard_data = analyze_watch_data(videos)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos")
async def get_videos(
    days: int = 30, limit: int = 50, current_user: TokenData = Depends(get_current_user)
):
    """Get raw video data for the specified number of days"""
    try:
        videos = generate_mock_videos(days)
        return videos[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories")
async def get_categories(current_user: TokenData = Depends(get_current_user)):
    """Get available video categories"""
    categories = [
        {"id": 1, "name": "Film & Animation"},
        {"id": 2, "name": "Autos & Vehicles"},
        {"id": 10, "name": "Music"},
        {"id": 15, "name": "Pets & Animals"},
        {"id": 17, "name": "Sports"},
        {"id": 19, "name": "Travel & Events"},
        {"id": 20, "name": "Gaming"},
        {"id": 22, "name": "People & Blogs"},
        {"id": 23, "name": "Comedy"},
        {"id": 24, "name": "Entertainment"},
        {"id": 25, "name": "News & Politics"},
        {"id": 26, "name": "Howto & Style"},
        {"id": 27, "name": "Education"},
        {"id": 28, "name": "Science & Technology"},
        {"id": 29, "name": "Nonprofits & Activism"},
    ]
    return categories


@app.post("/api/sync-youtube-data")
async def sync_youtube_data(current_user: TokenData = Depends(get_current_user)):
    """Sync YouTube watch history data"""
    try:
        # Get user's stored tokens
        user_token_data = user_tokens.get(current_user.user_id)
        if not user_token_data:
            raise HTTPException(status_code=401, detail="No stored tokens found")

        # Create YouTube service
        youtube_service = get_youtube_service(user_token_data["access_token"])

        # Get watch history (this is a placeholder - actual implementation would be more complex)
        # Note: YouTube Data API v3 doesn't provide direct access to watch history
        # This would require additional implementation or different approach

        return {
            "message": "YouTube data sync initiated",
            "status": "success",
            "note": "YouTube Data API v3 doesn't provide direct watch history access",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
