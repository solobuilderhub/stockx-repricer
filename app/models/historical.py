"""Historical pricing data model for MongoDB."""
from datetime import datetime
from beanie import Document
from pydantic import Field


class HistoricalPrice(Document):
    """Historical price data document - customize fields as needed."""

    product_id: str = Field(..., description="Product identifier")
    price: float = Field(..., description="Historical price")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # Add more fields as needed (source, marketplace, etc.)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "historical_prices"
        indexes = [
            "product_id",
            "timestamp",
            [("product_id", 1), ("timestamp", -1)]
        ]
