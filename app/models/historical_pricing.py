"""Historical pricing data model for MongoDB Time Series Collection."""
from datetime import datetime
from beanie import Document
from pydantic import Field


class HistoricalPricing(Document):
    """Historical pricing document model using MongoDB Time Series Collection.

    Optimized for time-series storage and queries.
    Represents price data points with automatic compression and bucketing.

    Note: Time series collections don't support Beanie Links.
    We store variant_db_id as a string field for manual reference linking.
    """

    # Time series field (REQUIRED)
    date: datetime = Field(..., description="Timestamp of data point - timeField")

    # Metadata fields (for grouping/filtering)
    variant_id: str = Field(..., description="StockX variant identifier - metaField")
    variant_db_id: str = Field(..., description="MongoDB ID of variant (string reference, not Beanie Link)")
    product_id: str = Field(..., description="StockX product identifier")

    # Measurement field
    price: float = Field(..., description="Price at this timestamp")

    # Additional metadata
    is_variant: bool = Field(default=True, description="Whether this is variant pricing")

    class Settings:
        name = "historical_pricing"
        timeseries = {
            "time_field": "date",           # REQUIRED: timestamp field
            "meta_field": "variant_id",     # Groups data by variant for better performance
            "granularity": "hours"          # Data bucketing: seconds/minutes/hours
        }
        # Note: Time series collections are automatically indexed on time_field
