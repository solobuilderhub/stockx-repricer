"""Product data model for MongoDB."""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class Product(Document):
    """Product document model - customize fields as needed."""

    product_id: str = Field(..., description="Unique product identifier")
    name: str
    # Add more fields as needed

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"
        indexes = ["product_id"]
