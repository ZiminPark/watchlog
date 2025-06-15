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


# YouTube API helper functions
async def get_user_channel_info(youtube_service):
    """Get user's channel information"""
    try:
        response = youtube_service.channels().list(
            part="snippet,statistics,contentDetails",
            mine=True
        ).execute()
        
        if response.get("items"):
            return response["items"][0]
        return None
    except Exception as e:
        print(f"Error fetching channel info: {e}")
        return None


async def get_user_playlists(youtube_service):
    """Get user's playlists"""
    try:
        response = youtube_service.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50
        ).execute()
        
        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching playlists: {e}")
        return []


async def get_playlist_videos(youtube_service, playlist_id, max_results=50):
    """Get videos from a playlist"""
    try:
        response = youtube_service.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=max_results
        ).execute()
        
        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching playlist videos: {e}")
        return []


async def get_video_details(youtube_service, video_ids):
    """Get detailed information about videos"""
    try:
        if not video_ids:
            return []
            
        # YouTube API accepts max 50 video IDs per request
        video_ids_str = ",".join(video_ids[:50])
        
        response = youtube_service.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_ids_str
        ).execute()
        
        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return []


async def get_video_categories(youtube_service, region_code="US"):
    """Get video categories"""
    try:
        response = youtube_service.videoCategories().list(
            part="snippet",
            regionCode=region_code
        ).execute()
        
        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching video categories: {e}")
        return []


async def get_user_subscriptions(youtube_service):
    """Get user's subscriptions"""
    try:
        response = youtube_service.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=50
        ).execute()
        
        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching subscriptions: {e}")
        return []


# Enhanced mock data generation with real YouTube data integration
async def generate_enhanced_videos(youtube_service, days: int = 30) -> List[VideoData]:
    """Generate mock video data enhanced with real YouTube API data"""
    
    # Get real data from YouTube API
    channel_info = await get_user_channel_info(youtube_service)
    playlists = await get_user_playlists(youtube_service)
    subscriptions = await get_user_subscriptions(youtube_service)
    categories = await get_video_categories(youtube_service)
    
    # Create category mapping from real data
    real_categories = {}
    if categories:
        for cat in categories:
            try:
                cat_id = int(cat["id"])
                cat_name = cat["snippet"]["title"]
                real_categories[cat_id] = cat_name
            except:
                continue
    
    # Fallback to predefined categories if API fails
    if not real_categories:
        real_categories = {
            1: "Film & Animation",
            2: "Autos & Vehicles", 
            10: "Music",
            15: "Pets & Animals",
            17: "Sports",
            19: "Travel & Events",
            20: "Gaming",
            22: "People & Blogs",
            23: "Comedy",
            24: "Entertainment",
            25: "News & Politics",
            26: "Howto & Style",
            27: "Education",
            28: "Science & Technology",
            29: "Nonprofits & Activism",
        }
    
    # Get real channel names from subscriptions
    real_channels = []
    if subscriptions:
        real_channels = [sub["snippet"]["title"] for sub in subscriptions]
    
    # Fallback channels if no subscriptions
    fallback_channels = [
        "TechCrunch", "Verge", "Marques Brownlee", "Linus Tech Tips",
        "Kurzgesagt", "CGP Grey", "Vsauce", "Numberphile", "Tom Scott",
        "Computerphile", "3Blue1Brown", "Veritasium", "CrashCourse",
        "Khan Academy", "MIT OpenCourseWare"
    ]
    
    channels = real_channels if real_channels else fallback_channels
    
    # Try to get some real video data from user's playlists
    real_videos = []
    for playlist in playlists[:5]:  # Limit to first 5 playlists
        playlist_videos = await get_playlist_videos(youtube_service, playlist["id"])
        real_videos.extend(playlist_videos)
    
    # Generate mock videos with enhanced data
    videos = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    num_videos = random.randint(50, 150)
    
    for i in range(num_videos):
        # Use real video data if available, otherwise generate mock
        if i < len(real_videos) and real_videos[i].get("snippet"):
            real_video = real_videos[i]["snippet"]
            title = real_video.get("title", f"Sample Video {i}")
            channel_name = real_video.get("channelTitle", random.choice(channels))
            
            # Try to get video details for category
            video_id = real_video.get("resourceId", {}).get("videoId")
            category_id = 27  # Default to Education
            if video_id:
                video_details = await get_video_details(youtube_service, [video_id])
                if video_details and video_details[0].get("snippet", {}).get("categoryId"):
                    try:
                        category_id = int(video_details[0]["snippet"]["categoryId"])
                    except:
                        pass
        else:
            # Generate mock data
            title = f"Sample Video {i} - {random.choice(['Tutorial', 'Review', 'News', 'Entertainment'])}"
            channel_name = random.choice(channels)
            category_id = random.choice(list(real_categories.keys()))
        
        category_name = real_categories.get(category_id, "Education")
        
        # Mock data for watch time and timestamp (not available from API)
        watch_time = random.randint(5, 120)
        watched_at = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        video = VideoData(
            video_id=f"video_{i}",
            title=title,
            channel_name=channel_name,
            category_id=category_id,
            category_name=category_name,
            watch_time_minutes=watch_time,
            watched_at=watched_at,
        )
        videos.append(video)
    
    return videos


# Keep original mock function as fallback
def generate_mock_videos(days: int = 30) -> List[VideoData]:
    """Fallback mock data generation when YouTube API is not available"""
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
        # Get user's stored tokens
        user_token_data = user_tokens.get(current_user.user_id)
        
        if user_token_data:
            # Try to use YouTube API for enhanced data
            try:
                youtube_service = get_youtube_service(user_token_data["access_token"])
                videos = await generate_enhanced_videos(youtube_service, days)
            except Exception as e:
                print(f"YouTube API error: {e}, falling back to mock data")
                videos = generate_mock_videos(days)
        else:
            # Fallback to mock data if no tokens
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
        # Get user's stored tokens
        user_token_data = user_tokens.get(current_user.user_id)
        
        if user_token_data:
            # Try to use YouTube API for enhanced data
            try:
                youtube_service = get_youtube_service(user_token_data["access_token"])
                videos = await generate_enhanced_videos(youtube_service, days)
            except Exception as e:
                print(f"YouTube API error: {e}, falling back to mock data")
                videos = generate_mock_videos(days)
        else:
            # Fallback to mock data if no tokens
            videos = generate_mock_videos(days)
            
        return videos[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories")
async def get_categories(current_user: TokenData = Depends(get_current_user)):
    """Get available video categories from YouTube API or fallback"""
    try:
        # Get user's stored tokens
        user_token_data = user_tokens.get(current_user.user_id)
        
        if user_token_data:
            try:
                youtube_service = get_youtube_service(user_token_data["access_token"])
                real_categories = await get_video_categories(youtube_service)
                
                if real_categories:
                    return [
                        {"id": int(cat["id"]), "name": cat["snippet"]["title"]}
                        for cat in real_categories
                    ]
            except Exception as e:
                print(f"YouTube API error: {e}, falling back to predefined categories")
        
        # Fallback to predefined categories
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sync-youtube-data")
async def sync_youtube_data(current_user: TokenData = Depends(get_current_user)):
    """Sync YouTube data and refresh cache"""
    try:
        # Get user's stored tokens
        user_token_data = user_tokens.get(current_user.user_id)
        if not user_token_data:
            raise HTTPException(status_code=401, detail="No stored tokens found")

        # Create YouTube service
        youtube_service = get_youtube_service(user_token_data["access_token"])
        
        # Test API connectivity by getting channel info
        channel_info = await get_user_channel_info(youtube_service)
        
        if channel_info:
            return {
                "message": "YouTube data sync completed successfully",
                "status": "success",
                "channel_name": channel_info.get("snippet", {}).get("title", "Unknown"),
                "note": "Watch history is not available via YouTube API due to privacy restrictions. Using enhanced mock data with real channel/category information."
            }
        else:
            return {
                "message": "YouTube API connected but no channel data found",
                "status": "partial_success",
                "note": "Using fallback mock data"
            }
            
    except Exception as e:
        return {
            "message": f"YouTube data sync failed: {str(e)}",
            "status": "error",
            "note": "Using fallback mock data"
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
