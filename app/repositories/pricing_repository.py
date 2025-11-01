"""Repository for pricing-related data operations."""
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.historical import HistoricalPrice
from app.models.product import Product
from app.repositories.base import BaseRepository
from app.core.exceptions import DatabaseException


class PricingRepository(BaseRepository[HistoricalPrice]):
    """Repository for historical pricing data with specialized queries."""

    def __init__(self):
        super().__init__(HistoricalPrice)

    async def get_historical_prices_by_product(
        self,
        product_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[HistoricalPrice]:
        """Get historical prices for a specific product.

        Args:
            product_id: Product identifier
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            limit: Maximum number of records to return

        Returns:
            List of historical price records
        """
        try:
            query = {"product_id": product_id}

            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date

            return await self.model.find(query).sort("-timestamp").limit(limit).to_list()

        except Exception as e:
            self.logger.error(f"Error fetching historical prices: {str(e)}")
            raise DatabaseException(f"Failed to fetch historical prices: {str(e)}")

    async def get_latest_price(self, product_id: str) -> Optional[HistoricalPrice]:
        """Get the most recent price for a product.

        Args:
            product_id: Product identifier

        Returns:
            Latest price record or None
        """
        try:
            return await self.model.find_one(
                {"product_id": product_id}
            ).sort("-timestamp")
        except Exception as e:
            self.logger.error(f"Error fetching latest price: {str(e)}")
            return None

    async def get_price_statistics(self, product_id: str, days: int = 30) -> dict:
        """Calculate price statistics for a product over a period.

        Args:
            product_id: Product identifier
            days: Number of days to analyze

        Returns:
            Dictionary with min, max, avg prices
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            prices = await self.get_historical_prices_by_product(
                product_id=product_id,
                start_date=start_date
            )

            if not prices:
                return {"min": 0, "max": 0, "avg": 0, "count": 0}

            price_values = [p.price for p in prices]
            return {
                "min": min(price_values),
                "max": max(price_values),
                "avg": sum(price_values) / len(price_values),
                "count": len(price_values)
            }

        except Exception as e:
            self.logger.error(f"Error calculating price statistics: {str(e)}")
            raise DatabaseException(f"Failed to calculate statistics: {str(e)}")


class ProductRepository(BaseRepository[Product]):
    """Repository for product data operations."""

    def __init__(self):
        super().__init__(Product)

    async def get_by_product_id(self, product_id: str) -> Optional[Product]:
        """Get product by its product_id field.

        Args:
            product_id: Product identifier

        Returns:
            Product or None
        """
        return await self.get_by_field("product_id", product_id)
