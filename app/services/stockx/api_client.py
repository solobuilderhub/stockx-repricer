"""External API client service for fetching StockX data."""
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.exceptions import APIClientException
from app.core.logging import LoggerMixin
from app.services.stockx.auth_service import auth_service


class StockXAPIClient(LoggerMixin):
    """Client for interacting with StockX API with OAuth authentication."""

    def __init__(self):
        self.base_url = settings.stockx_api_url
        self.timeout = 30.0
        self.auth_service = auth_service

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        use_auth: bool = True,
        **kwargs
    ) -> Dict[Any, Any]:
        """Make an HTTP request to the StockX API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            use_auth: Whether to include OAuth token (default: True)
            **kwargs: Additional arguments for httpx

        Returns:
            JSON response data

        Raises:
            APIClientException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})

        # Add OAuth token if required
        if use_auth:
            try:
                access_token = await self.auth_service.get_access_token()
                headers["Authorization"] = f"Bearer {access_token}"
                headers["x-api-key"] = settings.stockx_api_key
            except APIClientException as e:
                self.logger.error(f"Failed to get access token: {str(e)}")
                raise

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            error_msg = e.response.text
            self.logger.error(
                f"API request failed with status {e.response.status_code}: {error_msg}"
            )

            # If 401, try refreshing token once
            if e.response.status_code == 401 and use_auth:
                self.logger.info("Received 401, attempting to refresh token")
                self.auth_service.clear_token_cache()

                # Retry with fresh token
                try:
                    access_token = await self.auth_service.get_access_token(force_refresh=True)
                    headers["Authorization"] = f"Bearer {access_token}"

                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.request(
                            method=method,
                            url=url,
                            headers=headers,
                            **kwargs
                        )
                        response.raise_for_status()
                        return response.json()
                except Exception as retry_error:
                    self.logger.error(f"Retry with fresh token failed: {str(retry_error)}")
                    raise APIClientException(
                        "Authentication failed even after token refresh",
                        details={"error": str(retry_error)}
                    )

            raise APIClientException(
                f"API request failed: {e.response.status_code}",
                details={"status_code": e.response.status_code, "error": error_msg}
            )
        except httpx.RequestError as e:
            self.logger.error(f"API request error: {str(e)}")
            raise APIClientException(f"Failed to connect to API: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected API error: {str(e)}")
            raise APIClientException(f"API request failed: {str(e)}")

    async def fetch_product_data(self, search_param: str) -> Dict[str, Any]:
        """Fetch product information from the API.

        Args:
            search_param: Product identifier -> style id, upc

        Returns:
            Product data dictionary

        Note: Customize based on actual API response structure
        """
        self.logger.info(f"Fetching product data for: {search_param}")

        endpoint = f"/v2/catalog/search?query={search_param}"

        try:
            data = await self._make_request("GET", endpoint)
            return data
        except APIClientException:
            self.logger.warning(f"Failed to fetch product data for {search_param}")
            raise

    async def fetch_variant_data(self, product_id: str) -> Dict[str, Any]:
        """Fetch variant information from the API.

        Args:
            product_id: Stockx Product identifier

        Returns:
            Variant data dictionary
        """
        self.logger.info(f"Fetching variant data for: {product_id}")

        endpoint = f"/v2/catalog/products/{product_id}/variants"

        try:
            data = await self._make_request("GET", endpoint)
            return data
        except APIClientException:
            self.logger.warning(f"Failed to fetch variant data for {product_id}")
            raise

    async def fetch_market_data(
        self,
        product_id: str,
        variant_id: str,
        currency_code: str = "USD"
    ) -> Dict[str, Any]:
        """Fetch market data for a specific product variant.

        Args:
            product_id: StockX Product identifier
            variant_id: StockX Variant identifier
            currency_code: Currency code for pricing (default: USD)

        Returns:
            Market data dictionary containing pricing and sales information

        Example:
            market_data = await api_client.fetch_market_data(
                "b80ff5b5-98ab-40ff-a58c-83f6962fe8aa",
                "a09ff70f-48ca-4abd-a23a-a0fd716a4dff",
                "USD"
            )
        """
        self.logger.info(
            f"Fetching market data for product {product_id}, variant {variant_id}, currency {currency_code}"
        )

        endpoint = f"/v2/catalog/products/{product_id}/variants/{variant_id}/market-data"
        params = {"currencyCode": currency_code}

        try:
            data = await self._make_request("GET", endpoint, params=params)
            return data
        except APIClientException:
            self.logger.warning(
                f"Failed to fetch market data for product {product_id}, variant {variant_id}"
            )
            raise

    async def fetch_listings(
        self,
        product_id: Optional[str] = None,
        variant_id: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 100,
        from_date: Optional[str] = None,
        listing_status: str = "ACTIVE"
    ) -> Dict[str, Any]:
        """Fetch listings from StockX selling API.

        Args:
            product_id: StockX Product identifier (optional if variant_id provided)
            variant_id: StockX Variant identifier (optional if product_id provided)
            page_number: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 100)
            from_date: Filter listings from this date (format: YYYY-MM-DD)
            listing_status: Filter by listing status (default: ACTIVE)

        Returns:
            Listings data dictionary with pagination info

        Raises:
            ValueError: If neither product_id nor variant_id is provided

        Example:
            listings = await api_client.fetch_listings(
                product_id="8b2a56c7-5ea5-4d8c-a001-38429b950a18",
                variant_id="7bd1da1c-1ebc-4d00-8bf0-a023d608e2b2",
                page_number=1,
                page_size=100,
                from_date="2025-01-01",
                listing_status="ACTIVE"
            )
        """
        # Validate that at least one ID is provided
        if not product_id and not variant_id:
            raise ValueError("Either product_id or variant_id must be provided")

        self.logger.info(
            f"Fetching listings for product={product_id}, variant={variant_id}, "
            f"page={page_number}, size={page_size}"
        )

        endpoint = "/v2/selling/listings"

        # Build query parameters
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "listingStatuses": listing_status
        }

        if product_id:
            params["productIds"] = product_id

        if variant_id:
            params["variantIds"] = variant_id

        if from_date:
            params["fromDate"] = from_date

        try:
            data = await self._make_request("GET", endpoint, params=params)
            return data
        except APIClientException:
            self.logger.warning(
                f"Failed to fetch listings for product={product_id}, variant={variant_id}"
            )
            raise


# Singleton instance
api_client = StockXAPIClient()
