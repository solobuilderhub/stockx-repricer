"""
Sale domain entity.
Represents a completed sale transaction for a StockX product variant.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.value_objects import Money


class Sale(BaseModel):
    """
    Sale entity representing a completed transaction.

    Contains information about the sale price, timestamp, and associated product/variant.
    Immutable record of a historical sale.
    """
    amount: Money = Field(..., description="Sale price")
    created_at: datetime = Field(..., description="When the sale occurred")
    product_id: str = Field(..., description="Product or variant ID (depends on is_variant)")
    is_variant: bool = Field(..., description="Whether product_id is a variant ID (True) or product ID (False)")
    size: Optional[str] = Field(None, description="Size of the item sold")
    order_type: Optional[str] = Field(None, description="Order type (STANDARD, etc.)")

    class Config:
        frozen = True  # Sales are immutable historical records
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
            "created_at": self.created_at.isoformat(),
            "product_id": self.product_id,
            "is_variant": self.is_variant,
            "size": self.size,
            "order_type": self.order_type
        }

    def __eq__(self, other):
        """Equality based on product_id, amount, and timestamp."""
        if not isinstance(other, Sale):
            return False
        return (
            self.product_id == other.product_id
            and self.amount == other.amount
            and self.created_at == other.created_at
        )

    def __hash__(self):
        """Hash based on product_id, amount, and timestamp."""
        return hash((self.product_id, self.amount.amount, self.created_at))
