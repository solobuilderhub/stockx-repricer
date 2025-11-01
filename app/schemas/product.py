"""Product schemas for API requests and responses."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema - customize as needed."""
    product_id: str
    name: str


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductResponse(ProductBase):
    """Schema for product API responses."""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
