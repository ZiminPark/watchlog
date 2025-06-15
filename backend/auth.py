"""
OAuth2 authentication module for WatchLog Insights
Handles Google OAuth2 authentication and YouTube API authorization
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from jose import JWTError, jwt
from pydantic import BaseModel

# Security
security = HTTPBearer()

# OAuth2 configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24 * 7  # 7 days

# OAuth2 redirect URI - should be configurable
OAUTH2_REDIRECT_URI = os.getenv(
    "OAUTH2_REDIRECT_URI", "http://localhost:3000/api/auth/callback"
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# YouTube API scopes
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# OAuth2 flow configuration
OAUTH2_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [OAUTH2_REDIRECT_URI],
        "javascript_origins": [FRONTEND_URL],
    }
}


class TokenData(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        name: str = payload.get("name")
        picture: str = payload.get("picture")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(user_id=user_id, email=email, name=name, picture=picture)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """Get current authenticated user from JWT token"""
    return verify_token(credentials.credentials)


def create_oauth_flow() -> Flow:
    """Create OAuth2 flow for Google authentication"""
    flow = Flow.from_client_config(
        OAUTH2_CONFIG,
        scopes=SCOPES,
        redirect_uri=OAUTH2_REDIRECT_URI,
    )
    return flow


def get_authorization_url() -> str:
    """Generate Google OAuth2 authorization URL"""
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    return authorization_url


def exchange_code_for_tokens(code: str) -> UserInfo:
    """Exchange authorization code for access and refresh tokens"""
    flow = create_oauth_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials

    # Get user info from Google
    service = build("oauth2", "v2", credentials=credentials)
    user_info = service.userinfo().get().execute()

    return UserInfo(
        id=user_info["id"],
        email=user_info["email"],
        name=user_info["name"],
        picture=user_info.get("picture"),
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_expiry=credentials.expiry,
    )


def get_youtube_service(access_token: str):
    """Create YouTube API service with access token"""
    credentials = Credentials(access_token)
    return build("youtube", "v3", credentials=credentials)


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh access token using refresh token"""
    credentials = Credentials(
        None,  # No access token initially
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )

    credentials.refresh(Request())

    return {
        "access_token": credentials.token,
        "expires_at": credentials.expiry.isoformat() if credentials.expiry else None,
    }
