"""Request and response schemas for market data endpoints."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.product import ProductResponseSchema, VariantResponseSchema


class StoreMarketDataRequest(BaseModel):
    """Request schema for storing market data."""

    intervals: int = Field(
        default=400,
        ge=1,
        le=1000,
        description="Number of historical pricing data points"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date filter (ISO format)"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date filter (ISO format)"
    )


class StoredSaleResponse(BaseModel):
    """Response schema for a stored sale record."""

    id: str = Field(..., description="MongoDB document ID")
    variant_id: str = Field(..., description="StockX variant identifier")
    sale_date: datetime = Field(..., description="When the sale occurred")
    amount: float = Field(..., description="Sale price amount")
    currency_code: str = Field(..., description="Currency code")
    size: Optional[str] = Field(None, description="Size sold")
    order_type: Optional[str] = Field(None, description="Order type")


class StoredHistoricalPricingResponse(BaseModel):
    """Response schema for a stored historical pricing record."""

    id: str = Field(..., description="MongoDB document ID")
    variant_id: str = Field(..., description="StockX variant identifier")
    date: datetime = Field(..., description="Data point timestamp")
    price: float = Field(..., description="Price at this timestamp")


class StoreMarketDataResponse(BaseModel):
    """Response schema for store market data endpoint."""

    sales: List[StoredSaleResponse] = Field(..., description="Newly stored sales")
    historical_pricing: List[StoredHistoricalPricingResponse] = Field(
        ...,
        description="Newly stored historical pricing records"
    )
    sales_stored_count: int = Field(..., description="Number of new sales stored")
    pricing_stored_count: int = Field(..., description="Number of new pricing records stored")
    message: str = Field(..., description="Success message")


class GetSalesResponse(BaseModel):
    """Response schema for get sales endpoint."""

    sales: List[StoredSaleResponse] = Field(..., description="Sales records")
    total_count: int = Field(..., description="Total number of sales returned")
    variant: VariantResponseSchema = Field(..., description="Variant details")
    product: ProductResponseSchema = Field(..., description="Product details")


class GetHistoricalPricingResponse(BaseModel):
    """Response schema for get historical pricing endpoint."""

    historical_pricing: List[StoredHistoricalPricingResponse] = Field(
        ...,
        description="Historical pricing records"
    )
    total_count: int = Field(..., description="Total number of pricing records returned")
    variant: VariantResponseSchema = Field(..., description="Variant details")
    product: ProductResponseSchema = Field(..., description="Product details")
