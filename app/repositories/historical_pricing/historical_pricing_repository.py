"""Historical pricing repository for MongoDB Time Series Collection operations."""
from typing import List, Optional
from datetime import datetime
from app.models.historical_pricing import HistoricalPricing
from app.repositories.base import BaseRepository
from app.core.exceptions import DatabaseException


class HistoricalPricingRepository(BaseRepository[HistoricalPricing]):
    """Repository for HistoricalPricing time series data."""

    def __init__(self):
        super().__init__(HistoricalPricing)

    async def get_by_variant_db_id(
        self,
        variant_db_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HistoricalPricing]:
        """Get historical pricing for a variant, optionally filtered by date range.

        Args:
            variant_db_id: MongoDB ID of the variant
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of HistoricalPricing documents

        Raises:
            DatabaseException: If query fails
        """
        try:
            query: dict = {"variant_db_id": variant_db_id}
            if start_date or end_date:
                date_condition: dict = {}
                if start_date:
                    date_condition["$gte"] = start_date
                if end_date:
                    date_condition["$lte"] = end_date
                query["date"] = date_condition

            return await HistoricalPricing.find(query).to_list()
        except Exception as e:
            self.logger.error(f"Failed to fetch historical pricing: {e}")
            raise DatabaseException(f"Failed to fetch historical pricing: {e}")

    async def pricing_exists(
        self,
        variant_db_id: str,
        date: datetime
    ) -> bool:
        """Check if pricing data exists for specific variant and date.

        Args:
            variant_db_id: MongoDB ID of the variant
            date: Date of the pricing data point

        Returns:
            True if pricing exists, False otherwise

        Raises:
            DatabaseException: If query fails
        """
        try:
            pricing = await HistoricalPricing.find_one({
                "variant_db_id": variant_db_id,
                "date": date
            })
            return pricing is not None
        except Exception as e:
            self.logger.error(f"Failed to check pricing existence: {e}")
            raise DatabaseException(f"Failed to check pricing existence: {e}")

    async def bulk_create(self, pricing_data: List[dict]) -> List[HistoricalPricing]:
        """Bulk insert historical pricing (optimized for time series).

        Args:
            pricing_data: List of dictionaries containing pricing data

        Returns:
            List of created HistoricalPricing documents

        Raises:
            DatabaseException: If bulk insert fails
        """
        try:
            if not pricing_data:
                return []

            pricing_records = [HistoricalPricing(**data) for data in pricing_data]
            await HistoricalPricing.insert_many(pricing_records)
            self.logger.info(f"Bulk created {len(pricing_records)} historical pricing records")
            return pricing_records
        except Exception as e:
            self.logger.error(f"Failed to bulk create historical pricing: {e}")
            raise DatabaseException(f"Failed to bulk create historical pricing: {e}")


# Singleton instance
historical_pricing_repository = HistoricalPricingRepository()
