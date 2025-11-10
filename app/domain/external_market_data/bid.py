"""
Bid domain entity.
Represents a bid price level for a StockX product variant.
"""
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.value_objects import Money


class Bid(BaseModel):
    """
    Bid entity representing a price level with bid count.

    Contains information about the bid amount, count of bids at that price,
    and whether it's available for flex fulfillment.
    Immutable record of a bid price level.
    """
    amount: Money = Field(..., description="Bid price")
    count: int = Field(..., ge=0, description="Number of bids at this price level")
    own_count: int = Field(..., ge=0, description="Number of user's own bids at this price level")
    product_id: str = Field(..., description="Product or variant ID (depends on is_variant)")
    is_variant: bool = Field(..., description="Whether product_id is a variant ID (True) or product ID (False)")
    size: Optional[str] = Field(None, description="Size of the item")
    available_for_flex: bool = Field(False, description="Whether bid is available for flex fulfillment")

    class Config:
        frozen = True  # Bids are immutable snapshots
        extra = "forbid"

    def to_dict(self) -> dict:
        """
        Convert to dictionary for API responses.

        Returns:
            Dictionary representation with serialized values
        """
        return {
            "amount": float(self.amount.amount),
            "currency_code": self.amount.currency_code,
            "count": self.count,
            "own_count": self.own_count,
            "product_id": self.product_id,
            "is_variant": self.is_variant,
            "size": self.size,
            "available_for_flex": self.available_for_flex
        }

    def __eq__(self, other):
        """Equality based on product_id and amount."""
        if not isinstance(other, Bid):
            return False
        return (
            self.product_id == other.product_id
            and self.amount == other.amount
        )

    def __hash__(self):
        """Hash based on product_id and amount."""
        return hash((self.product_id, self.amount.amount))
