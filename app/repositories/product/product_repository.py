"""Product repository for database operations."""
from typing import Optional
from app.repositories.base import BaseRepository
from app.models.product import Product
from app.core.logging import LoggerMixin


class ProductRepository(BaseRepository[Product], LoggerMixin):
    """Repository for Product document operations."""

    def __init__(self):
        """Initialize product repository."""
        super().__init__(Product)

    async def get_by_product_id(self, product_id: str) -> Optional[Product]:
        """
        Get a product by its StockX product ID.

        Args:
            product_id: StockX product UUID

        Returns:
            Product document or None if not found
        """
        return await self.get_by_field("product_id", product_id)

    async def get_by_style_id(self, style_id: str) -> Optional[Product]:
        """
        Get a product by its style ID.

        Args:
            style_id: Product style/SKU ID

        Returns:
            Product document or None if not found
        """
        return await self.get_by_field("style_id", style_id)

    async def product_exists(self, product_id: str) -> bool:
        """
        Check if a product exists by product ID.

        Args:
            product_id: StockX product UUID

        Returns:
            True if product exists, False otherwise
        """
        product = await self.get_by_product_id(product_id)
        return product is not None


# Singleton instance
product_repository = ProductRepository()
