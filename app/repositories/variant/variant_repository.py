"""Variant repository for database operations."""
from typing import Optional, List
from app.repositories.base import BaseRepository
from app.models.variant import Variant
from app.core.logging import LoggerMixin


class VariantRepository(BaseRepository[Variant], LoggerMixin):
    """Repository for Variant document operations."""

    def __init__(self):
        """Initialize variant repository."""
        super().__init__(Variant)

    async def get_by_variant_id(self, variant_id: str) -> Optional[Variant]:
        """
        Get a variant by its StockX variant ID.

        Args:
            variant_id: StockX variant UUID

        Returns:
            Variant document or None if not found
        """
        return await self.get_by_field("variant_id", variant_id)

    async def get_by_product_id(self, product_id: str) -> List[Variant]:
        """
        Get all variants for a specific product.

        Args:
            product_id: StockX product UUID

        Returns:
            List of variant documents
        """
        try:
            return await self.model.find({"product_id": product_id}).to_list()
        except Exception as e:
            self.logger.error(f"Error fetching variants for product {product_id}: {str(e)}")
            return []

    async def get_by_upc(self, upc: str) -> Optional[Variant]:
        """
        Get a variant by its UPC code.

        Args:
            upc: UPC barcode

        Returns:
            Variant document or None if not found
        """
        return await self.get_by_field("upc", upc)

    async def variant_exists(self, variant_id: str) -> bool:
        """
        Check if a variant exists by variant ID.

        Args:
            variant_id: StockX variant UUID

        Returns:
            True if variant exists, False otherwise
        """
        variant = await self.get_by_variant_id(variant_id)
        return variant is not None


# Singleton instance
variant_repository = VariantRepository()
