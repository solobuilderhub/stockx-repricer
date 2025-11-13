"""Sale data model for MongoDB Time Series Collection."""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class Sale(Document):
    """Sale document model using MongoDB Time Series Collection.

    Optimized for time-series storage and queries.
    Represents completed sale transactions with automatic compression.

    Note: Time series collections don't support Beanie Links.
    We store variant_db_id as a string field for manual reference linking.
    """

    # Time series field (REQUIRED)
    sale_date: datetime = Field(..., description="When the sale occurred - timeField")

    # Metadata fields (for grouping/filtering)
    variant_id: str = Field(..., description="StockX variant identifier - metaField")
    variant_db_id: str = Field(..., description="MongoDB ID of variant (string reference, not Beanie Link)")
    product_id: str = Field(..., description="StockX product identifier")

    # Measurement fields
    amount: float = Field(..., description="Sale price amount")
    currency_code: str = Field(default="USD", description="Currency code")

    # Optional details
    size: Optional[str] = Field(default=None, description="Size of the item sold")
    order_type: Optional[str] = Field(default=None, description="Order type")
    is_variant: bool = Field(default=True, description="Whether this is variant sale")

    class Settings:
        name = "sales"
        timeseries = {
            "time_field": "sale_date",      # REQUIRED: timestamp field
            "meta_field": "variant_id",     # Groups data by variant for better performance
            "granularity": "hours"          # Data bucketing: seconds/minutes/hours
        }
        # Note: Time series collections are automatically indexed on time_field
