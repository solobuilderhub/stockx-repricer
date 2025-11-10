"""
External StockX Market Data API Client.
Handles requests to the external StockX data API for market data like sales, bids, asks.
"""
import httpx
from typing import Dict, Any
from app.core.logging import LoggerMixin
from app.core.exceptions import APIClientException
from app.core.config import settings


class ExternalStockXClient(LoggerMixin):
    """
    Client for external StockX market data API.

    Fetches market data including sales, bids, asks, and historical data
    from an external API service.
    """

    def __init__(self):
        """Initialize the external API client."""
        self.base_url = "https://stockxbackend.solobuilderhub.com"
        self.bearer_token = settings.external_stockx_api_token
        self.timeout = 30.0

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to external API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: JSON payload for request body

        Returns:
            Response data as dictionary

        Raises:
            APIClientException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                self.logger.info(f"Making {method} request to {url}")

                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json
                )

                if response.status_code != 200:
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    self.logger.error(error_msg)
                    raise APIClientException(error_msg)

                data = response.json()
                self.logger.info(f"Successfully fetched data from {endpoint}")
                return data

        except httpx.TimeoutException as e:
            error_msg = f"Request timeout: {e}"
            self.logger.error(error_msg)
            raise APIClientException(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Request error: {e}"
            self.logger.error(error_msg)
            raise APIClientException(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error(error_msg)
            raise APIClientException(error_msg)

    async def fetch_sales_data(
        self,
        product_id: str,
        is_variant: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch sales data for a StockX product or variant.

        Args:
            product_id: StockX product or variant UUID
            is_variant: Whether the ID is for a variant (True) or product (False)

        Returns:
            Sales data dictionary with edges containing sale nodes

        Raises:
            APIClientException: If API request fails
        """
        self.logger.info(f"Fetching sales data for product_id={product_id}, is_variant={is_variant}")

        payload = {
            "productId": product_id,
            "type": "sales",
            "isVariant": is_variant
        }

        endpoint = "/api/stockx-clean/market-data"
        data = await self._make_request("POST", endpoint, json=payload)

        return data

    async def fetch_bids_data(
        self,
        product_id: str,
        is_variant: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch bids data for a StockX product or variant.

        Args:
            product_id: StockX product or variant UUID
            is_variant: Whether the ID is for a variant (True) or product (False)

        Returns:
            Bids data dictionary with edges containing bid price level nodes

        Raises:
            APIClientException: If API request fails
        """
        self.logger.info(f"Fetching bids data for product_id={product_id}, is_variant={is_variant}")

        payload = {
            "productId": product_id,
            "type": "bid",
            "isVariant": is_variant
        }

        endpoint = "/api/stockx-clean/market-data"
        data = await self._make_request("POST", endpoint, json=payload)

        return data

    async def fetch_asks_data(
        self,
        product_id: str,
        is_variant: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch asks data for a StockX product or variant.

        Args:
            product_id: StockX product or variant UUID
            is_variant: Whether the ID is for a variant (True) or product (False)

        Returns:
            Asks data dictionary with edges containing ask price level nodes

        Raises:
            APIClientException: If API request fails
        """
        self.logger.info(f"Fetching asks data for product_id={product_id}, is_variant={is_variant}")

        payload = {
            "productId": product_id,
            "type": "ask",
            "isVariant": is_variant
        }

        endpoint = "/api/stockx-clean/market-data"
        data = await self._make_request("POST", endpoint, json=payload)

        return data

    async def fetch_historical_sales_data(
        self,
        product_id: str,
        is_variant: bool = True,
        intervals: int = 400,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Fetch historical sales data for a StockX product or variant.

        Args:
            product_id: StockX product or variant UUID
            is_variant: Whether the ID is for a variant (True) or product (False)
            intervals: Number of data points to return (default: 400)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            Historical sales data dictionary with series containing time-series data points

        Raises:
            APIClientException: If API request fails
        """
        self.logger.info(
            f"Fetching historical sales for product_id={product_id}, is_variant={is_variant}, "
            f"intervals={intervals}, start_date={start_date}, end_date={end_date}"
        )

        payload = {
            "productId": product_id,
            "type": "historical",
            "isVariant": is_variant,
            "intervals": intervals
        }

        # Add optional date parameters
        if start_date:
            payload["startDate"] = start_date
        if end_date:
            payload["endDate"] = end_date

        endpoint = "/api/stockx-clean/market-data"
        data = await self._make_request("POST", endpoint, json=payload)

        return data


# Singleton instance
external_stockx_client = ExternalStockXClient()
