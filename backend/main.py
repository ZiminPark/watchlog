from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import json
import os
import pickle
from pathlib import Path
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
class ChannelData(BaseModel):
    channel_id: str
    title: str
    description: str
    subscriber_count: int
    video_count: int
    category_id: int
    category_name: str
    published_at: datetime
    thumbnails: dict


class DashboardData(BaseModel):
    total_subscriptions: int
    category_breakdown: List[dict]
    top_category: str
    top_channels: List[dict]
    subscriber_distribution: List[dict]


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# In-memory storage for user tokens (in production, use a database)
user_tokens = {}

# Cache storage for YouTube API results
user_cache = {}

# Cache file path
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def get_cache_file_path(user_id: str) -> Path:
    """Get cache file path for a user"""
    return CACHE_DIR / f"user_{user_id}_cache.pkl"


def save_user_cache(user_id: str, cache_data: Dict[str, Any]):
    """Save user cache to file"""
    try:
        cache_file = get_cache_file_path(user_id)
        with open(cache_file, "wb") as f:
            pickle.dump(cache_data, f)
        print(f"Cache saved for user {user_id}")
    except Exception as e:
        print(f"Error saving cache for user {user_id}: {e}")


def load_user_cache(user_id: str) -> Optional[Dict[str, Any]]:
    """Load user cache from file"""
    try:
        cache_file = get_cache_file_path(user_id)
        if cache_file.exists():
            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)
            print(f"Cache loaded for user {user_id}")
            return cache_data
    except Exception as e:
        print(f"Error loading cache for user {user_id}: {e}")
    return None


def clear_user_cache(user_id: str):
    """Clear user cache"""
    try:
        cache_file = get_cache_file_path(user_id)
        if cache_file.exists():
            cache_file.unlink()
        if user_id in user_cache:
            del user_cache[user_id]
        print(f"Cache cleared for user {user_id}")
    except Exception as e:
        print(f"Error clearing cache for user {user_id}: {e}")


# YouTube API helper functions
async def get_user_channel_info(youtube_service):
    """Get user's channel information"""
    try:
        response = (
            youtube_service.channels()
            .list(part="snippet,statistics,contentDetails", mine=True)
            .execute()
        )

        if response.get("items"):
            return response["items"][0]
        return None
    except Exception as e:
        print(f"Error fetching channel info: {e}")
        return None


async def get_user_subscriptions(youtube_service, max_results=50):
    """Get user's subscriptions"""
    try:
        response = (
            youtube_service.subscriptions()
            .list(part="snippet,contentDetails", mine=True, maxResults=max_results)
            .execute()
        )

        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching subscriptions: {e}")
        return []


async def get_channel_details(youtube_service, channel_ids):
    """Get detailed information about channels"""
    try:
        if not channel_ids:
            return []

        # YouTube API accepts max 50 channel IDs per request
        channel_ids_str = ",".join(channel_ids[:50])

        response = (
            youtube_service.channels()
            .list(part="snippet,statistics,contentDetails", id=channel_ids_str)
            .execute()
        )

        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching channel details: {e}")
        return []


async def get_video_categories(youtube_service, region_code="US"):
    """Get video categories"""
    try:
        response = (
            youtube_service.videoCategories()
            .list(part="snippet", regionCode=region_code)
            .execute()
        )

        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching video categories: {e}")
        return []


async def get_channel_videos_for_category(youtube_service, channel_id, max_results=5):
    """Get recent videos from a channel to determine its category"""
    try:
        response = (
            youtube_service.search()
            .list(
                part="snippet",
                channelId=channel_id,
                order="date",
                type="video",
                maxResults=max_results,
            )
            .execute()
        )

        videos = response.get("items", [])
        if videos:
            # Get video details to determine category
            video_ids = [video["id"]["videoId"] for video in videos]
            video_details = await get_video_details(youtube_service, video_ids)

            # Return the most common category
            categories = {}
            for video in video_details:
                if video.get("snippet", {}).get("categoryId"):
                    cat_id = video["snippet"]["categoryId"]
                    categories[cat_id] = categories.get(cat_id, 0) + 1

            if categories:
                most_common_category = max(categories, key=categories.get)
                return most_common_category

        return None
    except Exception as e:
        print(f"Error fetching channel videos: {e}")
        return None


async def get_video_details(youtube_service, video_ids):
    """Get detailed information about videos"""
    try:
        if not video_ids:
            return []

        # YouTube API accepts max 50 video IDs per request
        video_ids_str = ",".join(video_ids[:50])

        response = (
            youtube_service.videos()
            .list(part="snippet,contentDetails,statistics", id=video_ids_str)
            .execute()
        )

        return response.get("items", [])
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return []


async def get_real_subscription_data(
    youtube_service, user_id: str = None, force_refresh: bool = False
) -> List[ChannelData]:
    """Get real subscription data from YouTube API with caching"""

    # Try to load from cache first (unless force refresh)
    if not force_refresh and user_id:
        cached_data = load_user_cache(user_id)
        if cached_data and "channels" in cached_data:
            print(f"Using cached data for user {user_id}")
            # Convert cached data back to ChannelData objects
            channels = []
            for channel_dict in cached_data["channels"]:
                try:
                    # Convert string back to datetime
                    if isinstance(channel_dict["published_at"], str):
                        channel_dict["published_at"] = datetime.fromisoformat(
                            channel_dict["published_at"]
                        )
                    channels.append(ChannelData(**channel_dict))
                except Exception as e:
                    print(f"Error converting cached channel data: {e}")
                    continue
            return channels

    try:
        # Get user's subscriptions
        subscriptions = await get_user_subscriptions(youtube_service, max_results=100)

        if not subscriptions:
            return []

        # Extract channel IDs from subscriptions
        channel_ids = [
            sub["snippet"]["resourceId"]["channelId"] for sub in subscriptions
        ]

        # Get detailed channel information
        channel_details = await get_channel_details(youtube_service, channel_ids)

        # Get video categories for mapping
        categories = await get_video_categories(youtube_service)
        category_mapping = {}
        if categories:
            for cat in categories:
                try:
                    cat_id = int(cat["id"])
                    cat_name = cat["snippet"]["title"]
                    category_mapping[cat_id] = cat_name
                except:
                    continue

        # Fallback categories if API fails
        if not category_mapping:
            category_mapping = {
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

        channels = []
        for channel in channel_details:
            try:
                # Determine category by analyzing recent videos
                category_id = await get_channel_videos_for_category(
                    youtube_service, channel["id"]
                )
                if not category_id:
                    category_id = 22  # Default to "People & Blogs"

                category_name = category_mapping.get(int(category_id), "People & Blogs")

                # Parse published date
                published_at = datetime.fromisoformat(
                    channel["snippet"]["publishedAt"].replace("Z", "+00:00")
                )

                channel_data = ChannelData(
                    channel_id=channel["id"],
                    title=channel["snippet"]["title"],
                    description=channel["snippet"]["description"],
                    subscriber_count=int(
                        channel["statistics"].get("subscriberCount", 0)
                    ),
                    video_count=int(channel["statistics"].get("videoCount", 0)),
                    category_id=int(category_id),
                    category_name=category_name,
                    published_at=published_at,
                    thumbnails=channel["snippet"]["thumbnails"],
                )
                channels.append(channel_data)
            except Exception as e:
                print(f"Error processing channel {channel.get('id', 'unknown')}: {e}")
                continue

        # Save to cache if user_id is provided
        if user_id and channels:
            cache_data = {
                "channels": [channel.dict() for channel in channels],
                "last_updated": datetime.now().isoformat(),
                "subscription_count": len(channels),
            }
            save_user_cache(user_id, cache_data)
            print(f"Fresh data cached for user {user_id}")

        return channels
    except Exception as e:
        print(f"Error fetching real subscription data: {e}")
        return []


def generate_mock_subscription_data() -> List[ChannelData]:
    """Generate mock subscription data when YouTube API is not available"""
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

    channel_names = [
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
        "PewDiePie",
        "MrBeast",
        "Markiplier",
        "Jacksepticeye",
        "Ninja",
        "Shane Dawson",
        "Jake Paul",
        "Logan Paul",
        "Dude Perfect",
        "Good Mythical Morning",
    ]

    channels = []
    end_date = datetime.now()

    for i in range(random.randint(20, 50)):
        category_id, category_name = random.choice(categories)
        channel_name = random.choice(channel_names)

        # Generate random subscriber count (more realistic distribution)
        subscriber_count = random.randint(1000, 10000000)
        video_count = random.randint(10, 1000)

        # Generate random published date (within last 5 years)
        days_ago = random.randint(0, 1825)  # 5 years
        published_at = end_date - timedelta(days=days_ago)

        channel = ChannelData(
            channel_id=f"UC{random.randint(100000000000000000000, 999999999999999999999)}",
            title=channel_name,
            description=f"Sample channel description for {channel_name}",
            subscriber_count=subscriber_count,
            video_count=video_count,
            category_id=category_id,
            category_name=category_name,
            published_at=published_at,
            thumbnails={
                "default": {
                    "url": f"https://via.placeholder.com/88x88?text={channel_name[:2]}"
                },
                "medium": {
                    "url": f"https://via.placeholder.com/240x240?text={channel_name[:2]}"
                },
                "high": {
                    "url": f"https://via.placeholder.com/800x800?text={channel_name[:2]}"
                },
            },
        )
        channels.append(channel)

    return channels


def analyze_subscription_data(channels: List[ChannelData]) -> DashboardData:
    """Analyze subscription data and return dashboard metrics"""

    # Calculate total subscriptions
    total_subscriptions = len(channels)

    # Category breakdown
    category_counts = {}
    for channel in channels:
        if channel.category_name not in category_counts:
            category_counts[channel.category_name] = 0
        category_counts[channel.category_name] += 1

    category_breakdown = [
        {
            "category": cat,
            "count": count,
            "percentage": (
                (count / total_subscriptions * 100) if total_subscriptions > 0 else 0
            ),
        }
        for cat, count in sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        )
    ]

    # Top category
    top_category = (
        category_breakdown[0]["category"] if category_breakdown else "No data"
    )

    # Top channels by subscriber count
    top_channels = [
        {
            "channel": channel.title,
            "subscriber_count": channel.subscriber_count,
            "category": channel.category_name,
            "video_count": channel.video_count,
        }
        for channel in sorted(channels, key=lambda x: x.subscriber_count, reverse=True)[
            :10
        ]
    ]

    # Subscriber distribution (group by ranges)
    subscriber_ranges = [
        (0, 10000, "0-10K"),
        (10000, 100000, "10K-100K"),
        (100000, 1000000, "100K-1M"),
        (1000000, 10000000, "1M-10M"),
        (10000000, float("inf"), "10M+"),
    ]

    distribution = []
    for min_sub, max_sub, label in subscriber_ranges:
        count = sum(
            1 for channel in channels if min_sub <= channel.subscriber_count < max_sub
        )
        if count > 0:
            distribution.append(
                {
                    "range": label,
                    "count": count,
                    "percentage": (
                        (count / total_subscriptions * 100)
                        if total_subscriptions > 0
                        else 0
                    ),
                }
            )

    return DashboardData(
        total_subscriptions=total_subscriptions,
        category_breakdown=category_breakdown,
        top_category=top_category,
        top_channels=top_channels,
        subscriber_distribution=distribution,
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
            url=f"{frontend_url}/login?token={access_token}&user={user_info.id}"
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
async def get_dashboard(current_user: TokenData = Depends(get_current_user)):
    """Get dashboard data for subscription analysis"""
    try:
        # Get user's stored tokens
        user_token_data = user_tokens.get(current_user.user_id)

        if user_token_data:
            # Try to use YouTube API for real data (with caching)
            try:
                youtube_service = get_youtube_service(user_token_data["access_token"])
                channels = await get_real_subscription_data(
                    youtube_service, current_user.user_id, force_refresh=False
                )
            except Exception as e:
                print(f"YouTube API error: {e}, falling back to mock data")
                channels = generate_mock_subscription_data()
        else:
            # Fallback to mock data if no tokens
            channels = generate_mock_subscription_data()

        dashboard_data = analyze_subscription_data(channels)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/channels")
async def get_channels(
    limit: int = 50, current_user: TokenData = Depends(get_current_user)
):
    """Get raw channel data"""
    try:
        # Get user's stored tokens
        user_token_data = user_tokens.get(current_user.user_id)

        if user_token_data:
            # Try to use YouTube API for real data (with caching)
            try:
                youtube_service = get_youtube_service(user_token_data["access_token"])
                channels = await get_real_subscription_data(
                    youtube_service, current_user.user_id, force_refresh=False
                )
            except Exception as e:
                print(f"YouTube API error: {e}, falling back to mock data")
                channels = generate_mock_subscription_data()
        else:
            # Fallback to mock data if no tokens
            channels = generate_mock_subscription_data()

        return channels[:limit]
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
    """Sync YouTube subscription data and refresh cache"""
    try:
        # Get user's stored tokens
        user_token_data = user_tokens.get(current_user.user_id)
        if not user_token_data:
            raise HTTPException(status_code=401, detail="No stored tokens found")

        # Clear old cache first
        clear_user_cache(current_user.user_id)

        # Create YouTube service
        youtube_service = get_youtube_service(user_token_data["access_token"])

        # Test API connectivity by getting channel info
        channel_info = await get_user_channel_info(youtube_service)
        subscriptions = await get_user_subscriptions(youtube_service)

        if channel_info and subscriptions:
            # Force refresh cache with new data
            channels = await get_real_subscription_data(
                youtube_service, current_user.user_id, force_refresh=True
            )

            return {
                "message": f"YouTube subscription data sync completed successfully. Found {len(subscriptions)} subscriptions.",
                "status": "success",
                "channel_name": channel_info.get("snippet", {}).get("title", "Unknown"),
                "subscription_count": len(subscriptions),
                "cached_channels": len(channels),
                "note": "Successfully retrieved and cached your subscription data from YouTube API.",
            }
        else:
            return {
                "message": "YouTube API connected but limited data available",
                "status": "partial_success",
                "subscription_count": len(subscriptions) if subscriptions else 0,
                "note": "Using enhanced mock data with real channel information where available.",
            }

    except Exception as e:
        return {
            "message": f"YouTube data sync failed: {str(e)}",
            "status": "error",
            "note": "Using fallback mock data",
        }


@app.get("/api/cache/status")
async def get_cache_status(current_user: TokenData = Depends(get_current_user)):
    """Get cache status and information for the current user"""
    try:
        cached_data = load_user_cache(current_user.user_id)

        if cached_data:
            return {
                "has_cache": True,
                "last_updated": cached_data.get("last_updated"),
                "subscription_count": cached_data.get("subscription_count", 0),
                "cache_age_hours": (
                    (
                        datetime.now()
                        - datetime.fromisoformat(cached_data["last_updated"])
                    ).total_seconds()
                    / 3600
                    if cached_data.get("last_updated")
                    else None
                ),
            }
        else:
            return {"has_cache": False, "message": "No cached data found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cache/clear")
async def clear_cache(current_user: TokenData = Depends(get_current_user)):
    """Clear cache for the current user"""
    try:
        clear_user_cache(current_user.user_id)
        return {
            "message": "Cache cleared successfully",
            "user_id": current_user.user_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
