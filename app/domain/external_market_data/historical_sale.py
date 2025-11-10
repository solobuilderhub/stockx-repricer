"""
HistoricalSale domain entity.
Represents a historical sales data point for a StockX product variant.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HistoricalSale(BaseModel):
    """
    HistoricalSale entity representing a time-series data point.

    Contains information about the sale price at a specific point in time.
    Immutable record of a historical sales data point.
    """
    date: datetime = Field(..., description="Timestamp of the data point")
    price: float = Field(..., description="Sale price at this timestamp")
    product_id: str = Field(..., description="Product or variant ID (depends on is_variant)")
    is_variant: bool = Field(..., description="Whether product_id is a variant ID (True) or product ID (False)")

    class Config:
        frozen = True  # HistoricalSales are immutable snapshots
        extra = "forbid"

    def to_dict(self) -> dict:
        """
        Convert to dictionary for API responses.

        Returns:
            Dictionary representation with serialized values
        """
        return {
            "date": self.date.isoformat(),
            "price": self.price,
            "product_id": self.product_id,
            "is_variant": self.is_variant
        }

    def __eq__(self, other):
        """Equality based on product_id and date."""
        if not isinstance(other, HistoricalSale):
            return False
        return (
            self.product_id == other.product_id
            and self.date == other.date
        )

    def __hash__(self):
        """Hash based on product_id and date."""
        return hash((self.product_id, self.date))
