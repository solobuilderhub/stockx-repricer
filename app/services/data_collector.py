"""Data collection service for fetching and storing historical data."""
from typing import List, Dict, Any
from datetime import datetime

from app.core.exceptions import APIClientException, DatabaseException
from app.core.logging import LoggerMixin
from app.repositories.pricing_repository import PricingRepository, ProductRepository
from app.services.api_client import api_client


class DataCollectionService(LoggerMixin):
    """Service for collecting historical pricing data from external APIs."""

    def __init__(self):
        self.pricing_repo = PricingRepository()
        self.product_repo = ProductRepository()
        self.api_client = api_client

    async def collect_historical_data(
        self,
        product_ids: List[str],
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Collect historical pricing data for multiple products.

        Args:
            product_ids: List of product identifiers
            days_back: Number of days of historical data to collect

        Returns:
            Dictionary with collection results
        """
        self.logger.info(f"Starting data collection for {len(product_ids)} products")

        results = {
            "products_processed": 0,
            "records_created": 0,
            "errors": []
        }

        for product_id in product_ids:
            try:
                records_count = await self._collect_product_data(product_id, days_back)
                results["products_processed"] += 1
                results["records_created"] += records_count

            except Exception as e:
                self.logger.error(f"Failed to collect data for {product_id}: {str(e)}")
                results["errors"].append({
                    "product_id": product_id,
                    "error": str(e)
                })

        self.logger.info(
            f"Data collection completed. Processed: {results['products_processed']}, "
            f"Records: {results['records_created']}, Errors: {len(results['errors'])}"
        )

        return results

    async def _collect_product_data(self, product_id: str, days_back: int) -> int:
        """Collect data for a single product.

        Args:
            product_id: Product identifier
            days_back: Number of days to collect

        Returns:
            Number of records created
        """
        self.logger.info(f"Collecting data for product: {product_id}")

        # Fetch product information
        try:
            product_data = await self.api_client.fetch_product_data(product_id)
            await self._ensure_product_exists(product_id, product_data)
        except APIClientException as e:
            self.logger.warning(f"Could not fetch product info for {product_id}: {str(e)}")

        # Fetch historical prices
        historical_data = await self.api_client.fetch_historical_prices(
            product_id=product_id,
            days_back=days_back
        )

        # Store historical data
        records_created = 0
        for price_data in historical_data:
            try:
                await self.pricing_repo.create({
                    "product_id": product_id,
                    "price": price_data.get("price"),
                    "timestamp": price_data.get("timestamp", datetime.utcnow()),
                    "created_at": datetime.utcnow()
                })
                records_created += 1
            except DatabaseException as e:
                self.logger.warning(f"Failed to store price record: {str(e)}")

        self.logger.info(f"Created {records_created} records for {product_id}")
        return records_created

    async def _ensure_product_exists(
        self,
        product_id: str,
        product_data: Dict[str, Any]
    ) -> None:
        """Ensure product exists in database, create if not.

        Args:
            product_id: Product identifier
            product_data: Product information from API
        """
        existing_product = await self.product_repo.get_by_product_id(product_id)

        if not existing_product:
            await self.product_repo.create({
                "product_id": product_id,
                "name": product_data.get("name", "Unknown Product"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            self.logger.info(f"Created product record for {product_id}")


# Singleton instance
data_collector = DataCollectionService()
