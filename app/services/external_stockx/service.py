"""
External StockX Service Wrapper.
Orchestrates API calls to external service and transforms responses into domain models.
"""
from typing import List, Optional
from app.services.external_stockx.api_client import external_stockx_client
from app.services.external_stockx.mapper import ExternalStockXMapper
from app.core.logging import LoggerMixin
from app.core.exceptions import APIClientException
from app.domain.external_market_data import Sale, Bid, Ask, HistoricalSale


class ExternalStockXService(LoggerMixin):
    """
    Wrapper service for external StockX market data API.

    Provides clean interface for fetching sales, bids, asks, and historical data.
    """

    def __init__(self):
        """Initialize the external StockX service."""
        self.api_client = external_stockx_client
        self.mapper = ExternalStockXMapper()

    async def get_sales(
        self,
        product_id: str,
        is_variant: bool = True
    ) -> List[Sale]:
        """
        Fetch sales data for a StockX product or variant.

        Args:
            product_id: StockX product or variant UUID
            is_variant: Whether the ID is for a variant (True) or product (False)

        Returns:
            List of Sale domain model instances

        Raises:
            APIClientException: If API call fails or response is invalid
        """
        self.logger.info(f"Fetching sales for product_id={product_id}, is_variant={is_variant}")

        try:
            # Fetch raw data from external API
            api_response = await self.api_client.fetch_sales_data(product_id, is_variant)

            # Transform to domain models
            sales = self.mapper.to_sales(api_response, product_id, is_variant)

            self.logger.info(
                f"Successfully fetched and transformed {len(sales)} sales for {product_id}"
            )

            return sales

        except APIClientException as e:
            self.logger.error(f"Failed to fetch sales for {product_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching sales for {product_id}: {e}")
            raise APIClientException(f"Failed to fetch sales: {e}")

    async def get_bids(
        self,
        product_id: str,
        is_variant: bool = True
    ) -> List[Bid]:
        """
        Fetch bids data for a StockX product or variant.

        Args:
            product_id: StockX product or variant UUID
            is_variant: Whether the ID is for a variant (True) or product (False)

        Returns:
            List of Bid domain model instances

        Raises:
            APIClientException: If API call fails or response is invalid
        """
        self.logger.info(f"Fetching bids for product_id={product_id}, is_variant={is_variant}")

        try:
            # Fetch raw data from external API
            api_response = await self.api_client.fetch_bids_data(product_id, is_variant)

            # Transform to domain models
            bids = self.mapper.to_bids(api_response, product_id, is_variant)

            self.logger.info(
                f"Successfully fetched and transformed {len(bids)} bids for {product_id}"
            )

            return bids

        except APIClientException as e:
            self.logger.error(f"Failed to fetch bids for {product_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching bids for {product_id}: {e}")
            raise APIClientException(f"Failed to fetch bids: {e}")

    async def get_asks(
        self,
        product_id: str,
        is_variant: bool = True
    ) -> List[Ask]:
        """
        Fetch asks data for a StockX product or variant.

        Args:
            product_id: StockX product or variant UUID
            is_variant: Whether the ID is for a variant (True) or product (False)

        Returns:
            List of Ask domain model instances

        Raises:
            APIClientException: If API call fails or response is invalid
        """
        self.logger.info(f"Fetching asks for product_id={product_id}, is_variant={is_variant}")

        try:
            # Fetch raw data from external API
            api_response = await self.api_client.fetch_asks_data(product_id, is_variant)

            # Transform to domain models
            asks = self.mapper.to_asks(api_response, product_id, is_variant)

            self.logger.info(
                f"Successfully fetched and transformed {len(asks)} asks for {product_id}"
            )

            return asks

        except APIClientException as e:
            self.logger.error(f"Failed to fetch asks for {product_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching asks for {product_id}: {e}")
            raise APIClientException(f"Failed to fetch asks: {e}")

    async def get_historical_sales(
        self,
        product_id: str,
        is_variant: bool = True,
        intervals: int = 400,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[HistoricalSale]:
        """
        Fetch historical sales data for a StockX product or variant.

        Args:
            product_id: StockX product or variant UUID
            is_variant: Whether the ID is for a variant (True) or product (False)
            intervals: Number of data points to return (default: 400)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of HistoricalSale domain model instances

        Raises:
            APIClientException: If API call fails or response is invalid
        """
        self.logger.info(
            f"Fetching historical sales for product_id={product_id}, is_variant={is_variant}, "
            f"intervals={intervals}, start_date={start_date}, end_date={end_date}"
        )

        try:
            # Fetch raw data from external API
            api_response = await self.api_client.fetch_historical_sales_data(
                product_id, is_variant, intervals, start_date, end_date
            )

            # Transform to domain models
            historical_sales = self.mapper.to_historical_sales(api_response, product_id, is_variant)

            self.logger.info(
                f"Successfully fetched and transformed {len(historical_sales)} historical sales for {product_id}"
            )

            return historical_sales

        except APIClientException as e:
            self.logger.error(f"Failed to fetch historical sales for {product_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching historical sales for {product_id}: {e}")
            raise APIClientException(f"Failed to fetch historical sales: {e}")


# Singleton instance
external_stockx_service = ExternalStockXService()
