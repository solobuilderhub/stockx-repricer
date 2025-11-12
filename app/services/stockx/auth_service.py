"""StockX OAuth authentication service."""
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.exceptions import APIClientException
from app.core.logging import LoggerMixin


class StockXAuthService(LoggerMixin):
    """Service for handling StockX OAuth authentication."""

    def __init__(self):
        self.auth_url = settings.stockx_auth_url or ""
        self.client_id = settings.stockx_client_id
        self.client_secret = settings.stockx_client_secret
        self.refresh_token = settings.stockx_refresh_token
        self.grant_type = settings.stockx_grant_type
        self.audience = settings.stockx_audience

        # Cache for access token
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    async def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """Get a valid access token, refreshing if necessary.

        Args:
            force_refresh: Force token refresh even if cached token is valid

        Returns:
            Valid access token

        Raises:
            APIClientException: If token acquisition fails
        """
        # Check if we have a valid cached token
        if not force_refresh and self._is_token_valid():
            self.logger.debug("Using cached access token")
            return self._access_token

        # Fetch new token
        self.logger.info("Fetching new access token from StockX")
        token_data = await self._fetch_access_token()

        # Cache the token
        self._access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 3600)  # Default 1 hour

        # Set expiry with 5 minute buffer
        self._token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 300)

        self.logger.info(f"Access token acquired, expires in {expires_in} seconds")
        return self._access_token

    async def _fetch_access_token(self) -> Dict[str, Any]:
        """Fetch access token from StockX OAuth endpoint.

        Returns:
            Token response data

        Raises:
            APIClientException: If token request fails
        """
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise APIClientException(
                "Missing StockX OAuth credentials. Please set STOCKX_CLIENT_ID, "
                "STOCKX_CLIENT_SECRET, and STOCKX_REFRESH_TOKEN in .env file"
            )

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": self.audience,
            "refresh_token": self.refresh_token
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.auth_url,
                    headers=headers,
                    data=data
                )

                response.raise_for_status()
                token_data = response.json()

                if "access_token" not in token_data:
                    raise APIClientException("Invalid token response: missing access_token")

                return token_data

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            self.logger.error(
                f"OAuth token request failed: {e.response.status_code} - {error_detail}"
            )
            raise APIClientException(
                f"Failed to obtain access token: {e.response.status_code}",
                details={"error": error_detail}
            )
        except httpx.RequestError as e:
            self.logger.error(f"OAuth request error: {str(e)}")
            raise APIClientException(f"Failed to connect to auth server: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error during token fetch: {str(e)}")
            raise APIClientException(f"Token acquisition failed: {str(e)}")

    def _is_token_valid(self) -> bool:
        """Check if the cached token is still valid.

        Returns:
            True if token exists and hasn't expired
        """
        if not self._access_token or not self._token_expiry:
            return False

        return datetime.utcnow() < self._token_expiry

    def clear_token_cache(self) -> None:
        """Clear the cached access token."""
        self._access_token = None
        self._token_expiry = None
        self.logger.info("Access token cache cleared")


# Singleton instance
auth_service = StockXAuthService()
