"""Authentication testing routes."""
from fastapi import APIRouter, HTTPException, status

from app.services.stockx.auth_service import auth_service
from app.core.exceptions import APIClientException

router = APIRouter(prefix="/api/v1/stockx/auth", tags=["Stockx Authentication Routes"])


@router.get("/test-token")
async def test_token():
    """
    Test StockX OAuth authentication.

    This endpoint attempts to get an access token and returns its status.
    Useful for verifying that OAuth credentials are configured correctly.
    """
    try:
        access_token = await auth_service.get_access_token()

        # Don't return the full token for security, just confirmation
        token_preview = f"{access_token[:10]}...{access_token[-10:]}" if len(access_token) > 20 else "***"

        return {
            "status": "success",
            "message": "Successfully obtained access token",
            "token_preview": token_preview,
            "token_cached": auth_service._is_token_valid()
        }

    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Authentication failed",
                "message": str(e.message),
                "details": e.details
            }
        )


@router.post("/refresh-token")
async def refresh_token():
    """
    Force refresh the access token.

    Clears the cached token and fetches a new one from StockX.
    """
    try:
        # Clear cache
        auth_service.clear_token_cache()

        # Get fresh token
        access_token = await auth_service.get_access_token(force_refresh=True)

        token_preview = f"{access_token[:10]}...{access_token[-10:]}" if len(access_token) > 20 else "***"

        return {
            "status": "success",
            "message": "Token refreshed successfully",
            "token_preview": token_preview
        }

    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Token refresh failed",
                "message": str(e.message),
                "details": e.details
            }
        )


@router.get("/status")
async def auth_status():
    """
    Check authentication configuration status.

    Returns information about whether OAuth credentials are configured.
    """
    from app.core.config import settings

    return {
        "auth_url_configured": bool(settings.stockx_auth_url),
        "client_id_configured": bool(settings.stockx_client_id),
        "client_secret_configured": bool(settings.stockx_client_secret),
        "refresh_token_configured": bool(settings.stockx_refresh_token),
        "token_cached": auth_service._is_token_valid(),
        "api_url": settings.stockx_api_url
    }
