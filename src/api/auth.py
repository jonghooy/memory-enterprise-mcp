"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict, Any

from src.core.config import settings

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint for token generation."""
    # TODO: Implement actual authentication
    # This is a placeholder for development

    if form_data.username == "test" and form_data.password == "test":
        return {
            "access_token": "test_token",
            "token_type": "bearer",
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth flow."""
    # TODO: Implement Google OAuth
    return {
        "login_url": f"https://accounts.google.com/oauth/authorize"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&scope={' '.join(settings.google_docs_scopes)}"
        f"&response_type=code"
    }


@router.get("/google/callback")
async def google_callback(code: str):
    """Handle Google OAuth callback."""
    # TODO: Exchange code for tokens
    # TODO: Create or update user
    # TODO: Generate JWT

    return {
        "message": "Google authentication successful",
        "code": code,
    }


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout endpoint."""
    # TODO: Invalidate token

    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user information."""
    # TODO: Decode token and get user

    return {
        "id": "test_user_id",
        "email": "test@example.com",
        "tenant_id": "test_tenant_id",
    }