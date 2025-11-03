"""Variant data model for MongoDB."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from beanie import Document, Link
from pydantic import Field

if TYPE_CHECKING:
    from app.models.product import Product


class Variant(Document):
    """Product variant document model.
    
    Each product can have multiple variants (e.g., different sizes, colors).
    """

    variant_id: str = Field(..., description="Unique variant identifier")
    product_id: str = Field(..., description="Reference to parent product")
    product: Link["Product"] = Field(..., description="Reference to parent product")
    variant_name: str = Field(..., description="Variant name")
    variant_value: str = Field(..., description="Variant value")
    upc: Optional[str] = Field(default=None, description="UPC code")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "variants"
        indexes = [
            "variant_id",
            "product",
            "upc"
        ]
