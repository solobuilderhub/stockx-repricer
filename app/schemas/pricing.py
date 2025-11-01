"""Pricing schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class HistoricalPriceCreate(BaseModel):
    """Schema for creating historical price data."""
    product_id: str
    price: float
    timestamp: Optional[datetime] = None


class HistoricalPriceResponse(BaseModel):
    """Schema for historical price response."""
    product_id: str
    price: float
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class OptimalPriceResponse(BaseModel):
    """Schema for optimal price calculation response."""
    product_id: str
    optimal_price: float
    confidence_score: Optional[float] = None
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    data_points_used: int = 0


class DataCollectionRequest(BaseModel):
    """Schema for triggering data collection."""
    product_ids: List[str] = Field(..., description="List of product IDs to collect data for")
    days_back: Optional[int] = Field(default=30, description="Number of days of historical data")


class DataCollectionResponse(BaseModel):
    """Schema for data collection response."""
    status: str
    products_processed: int
    records_created: int
    message: str
