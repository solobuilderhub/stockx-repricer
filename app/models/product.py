"""Product data model for MongoDB."""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class Product(Document):
    """Product document model - customize fields as needed."""

    product_id: str = Field(..., description="Unique product identifier")
    title: str = Field(..., description="Product title")
    brand: str = Field(..., description="Product brand")
    product_type: Optional[str] = Field(..., description="Product type")
    style_id: str = Field(..., description="Product style id")
    url_key: Optional[str] = Field(default=None, description="Product url key")
    retail_price: Optional[float] = Field(default=None, description="Product retail price")
    release_date: Optional[datetime] = Field(default=None, description="Product release date")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"
        indexes = [
            "product_id",
            "style_id"
        ]
