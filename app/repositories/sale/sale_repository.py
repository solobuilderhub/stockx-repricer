"""Sale repository for MongoDB Time Series Collection operations."""
from typing import List, Optional
from datetime import datetime
from app.models.sale import Sale
from app.repositories.base import BaseRepository
from app.core.exceptions import DatabaseException


class SaleRepository(BaseRepository[Sale]):
    """Repository for Sale time series data."""

    def __init__(self):
        super().__init__(Sale)

    async def get_by_variant_db_id(
        self,
        variant_db_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Sale]:
        """Get sales for a variant, optionally filtered by date range.

        Args:
            variant_db_id: MongoDB ID of the variant
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of Sale documents

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
                query["sale_date"] = date_condition  # type: ignore

            return await Sale.find(query).to_list()
        except Exception as e:
            self.logger.error(f"Failed to fetch sales: {e}")
            raise DatabaseException(f"Failed to fetch sales: {e}")

    async def sale_exists(
        self,
        variant_db_id: str,
        sale_date: datetime,
        amount: float
    ) -> bool:
        """Check if a specific sale already exists.

        Args:
            variant_db_id: MongoDB ID of the variant
            sale_date: Date of the sale
            amount: Sale amount

        Returns:
            True if sale exists, False otherwise

        Raises:
            DatabaseException: If query fails
        """
        try:
            sale = await Sale.find_one({
                "variant_db_id": variant_db_id,
                "sale_date": sale_date,
                "amount": amount
            })
            return sale is not None
        except Exception as e:
            self.logger.error(f"Failed to check sale existence: {e}")
            raise DatabaseException(f"Failed to check sale existence: {e}")

    async def bulk_create(self, sales_data: List[dict]) -> List[Sale]:
        """Bulk insert sales (optimized for time series).

        Args:
            sales_data: List of dictionaries containing sale data

        Returns:
            List of created Sale documents

        Raises:
            DatabaseException: If bulk insert fails
        """
        try:
            if not sales_data:
                return []

            sales = [Sale(**data) for data in sales_data]
            await Sale.insert_many(sales)
            self.logger.info(f"Bulk created {len(sales)} sales")
            return sales
        except Exception as e:
            self.logger.error(f"Failed to bulk create sales: {e}")
            raise DatabaseException(f"Failed to bulk create sales: {e}")


# Singleton instance
sale_repository = SaleRepository()
