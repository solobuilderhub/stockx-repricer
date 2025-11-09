"""StockX API schemas for requests and responses."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    """Schema for StockX product API responses."""
    product_id: str = Field(..., description="Unique product identifier")
    title: str = Field(..., description="Product title")
    brand: str = Field(..., description="Product brand")
    product_type: Optional[str] = Field(None, description="Product type/category")
    style_id: str = Field(..., description="Product style ID")
    url_key: Optional[str] = Field(None, description="URL key for product page")
    retail_price: Optional[float] = Field(None, description="MSRP/retail price")
    release_date: Optional[datetime] = Field(None, description="Product release date")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                "title": "Nike Air Max Pre-Day Optimism (Women's)",
                "brand": "Nike",
                "product_type": "sneakers",
                "style_id": "DO6716-700",
                "url_key": "nike-air-max-pre-day-optimism-w",
                "retail_price": 140.0,
                "release_date": "2020-12-11T00:00:00",
                "created_at": "2024-11-03T10:00:00",
                "updated_at": "2024-11-03T10:00:00"
            }
        }


class VariantResponse(BaseModel):
    """Schema for StockX variant API responses."""
    variant_id: str = Field(..., description="Unique variant identifier")
    product_id: str = Field(..., description="Reference to parent product")
    variant_name: str = Field(..., description="Variant name (e.g., 'Size', 'Color')")
    variant_value: str = Field(..., description="Variant value (e.g., '10.5', 'Red')")
    upc: Optional[str] = Field(None, description="UPC barcode")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "variant_id": "23687534-53ce-4e14-a16a-5f3c66a393d1",
                "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                "variant_value": "5W",
                "upc": "195244883486",
                "created_at": "2024-11-03T10:00:00",
                "updated_at": "2024-11-03T10:00:00"
            }
        }


class ProductWithVariantsResponse(BaseModel):
    """Schema for product with its variants."""
    product: ProductResponse = Field(..., description="Product details")
    variants: List[VariantResponse] = Field(..., description="List of product variants")

    class Config:
        json_schema_extra = {
            "example": {
                "product": {
                    "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                    "title": "Nike Air Max Pre-Day Optimism (Women's)",
                    "brand": "Nike",
                    "product_type": "sneakers",
                    "style_id": "DO6716-700",
                    "url_key": "nike-air-max-pre-day-optimism-w",
                    "retail_price": 140.0,
                    "release_date": "2020-12-11T00:00:00",
                    "created_at": "2024-11-03T10:00:00",
                    "updated_at": "2024-11-03T10:00:00"
                },
                "variants": [
                    {
                        "variant_id": "23687534-53ce-4e14-a16a-5f3c66a393d1",
                        "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                        "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                        "variant_value": "5W",
                        "upc": "195244883486",
                        "created_at": "2024-11-03T10:00:00",
                        "updated_at": "2024-11-03T10:00:00"
                    }
                ]
            }
        }


class MarketDataResponse(BaseModel):
    """Schema for StockX market data API responses."""
    product_id: str = Field(..., description="Product identifier")
    variant_id: str = Field(..., description="Variant identifier")
    currency_code: str = Field(..., description="Currency code (e.g., USD)")
    highest_bid_amount: Optional[float] = Field(None, description="Highest bid amount")
    lowest_ask_amount: Optional[float] = Field(None, description="Lowest ask amount")
    flex_lowest_ask_amount: Optional[float] = Field(None, description="Flex lowest ask amount")
    earn_more_amount: Optional[float] = Field(None, description="Earn more amount")
    sell_faster_amount: Optional[float] = Field(None, description="Sell faster amount")

    # Standard market data
    standard_lowest_ask: Optional[float] = Field(None, description="Standard lowest ask price")
    standard_highest_bid: Optional[float] = Field(None, description="Standard highest bid price")
    standard_sell_faster: Optional[float] = Field(None, description="Standard sell faster price")
    standard_earn_more: Optional[float] = Field(None, description="Standard earn more price")
    standard_beat_us: Optional[float] = Field(None, description="Standard beat US price")

    # Flex market data
    flex_lowest_ask: Optional[float] = Field(None, description="Flex lowest ask price")
    flex_highest_bid: Optional[float] = Field(None, description="Flex highest bid price")
    flex_sell_faster: Optional[float] = Field(None, description="Flex sell faster price")
    flex_earn_more: Optional[float] = Field(None, description="Flex earn more price")
    flex_beat_us: Optional[float] = Field(None, description="Flex beat US price")

    # Direct market data
    direct_lowest_ask: Optional[float] = Field(None, description="Direct lowest ask price")
    direct_highest_bid: Optional[float] = Field(None, description="Direct highest bid price")
    direct_sell_faster: Optional[float] = Field(None, description="Direct sell faster price")
    direct_earn_more: Optional[float] = Field(None, description="Direct earn more price")
    direct_beat_us: Optional[float] = Field(None, description="Direct beat US price")

    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "product_id": "b80ff5b5-98ab-40ff-a58c-83f6962fe8aa",
                "variant_id": "a09ff70f-48ca-4abd-a23a-a0fd716a4dff",
                "currency_code": "USD",
                "highest_bid_amount": 58.0,
                "lowest_ask_amount": 215.0,
                "flex_lowest_ask_amount": None,
                "earn_more_amount": 209.0,
                "sell_faster_amount": 105.0,
                "standard_lowest_ask": 215.0,
                "standard_highest_bid": 58.0,
                "standard_sell_faster": 105.0,
                "standard_earn_more": 209.0,
                "standard_beat_us": None,
                "flex_lowest_ask": None,
                "flex_highest_bid": 58.0,
                "flex_sell_faster": 236.0,
                "flex_earn_more": 247.0,
                "flex_beat_us": None,
                "direct_lowest_ask": None,
                "direct_highest_bid": 58.0,
                "direct_sell_faster": 236.0,
                "direct_earn_more": 247.0,
                "direct_beat_us": None,
                "created_at": "2024-11-03T10:00:00",
                "updated_at": "2024-11-03T10:00:00"
            }
        }


class ListingResponse(BaseModel):
    """Schema for StockX listing API responses."""
    listing_id: str = Field(..., description="Unique listing identifier")
    amount: Optional[float] = Field(None, description="Listing amount/price")
    currency_code: Optional[str] = Field(None, description="Currency code")
    status: Optional[str] = Field(None, description="Listing status (e.g., ACTIVE)")
    inventory_type: Optional[str] = Field(None, description="Inventory type (e.g., STANDARD)")
    created_at: Optional[datetime] = Field(None, description="Listing creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Listing update timestamp")

    # Ask details
    ask_id: Optional[str] = Field(None, description="Ask identifier")
    ask_created_at: Optional[datetime] = Field(None, description="Ask creation timestamp")
    ask_updated_at: Optional[datetime] = Field(None, description="Ask update timestamp")
    ask_expires_at: Optional[datetime] = Field(None, description="Ask expiration timestamp")

    # Product details
    product_id: Optional[str] = Field(None, description="Product identifier")
    product_name: Optional[str] = Field(None, description="Product name")
    style_id: Optional[str] = Field(None, description="Product style ID")

    # Variant details
    variant_id: Optional[str] = Field(None, description="Variant identifier")
    variant_name: Optional[str] = Field(None, description="Variant name")
    variant_value: Optional[str] = Field(None, description="Variant value (size)")

    # Batch details
    batch_id: Optional[str] = Field(None, description="Batch identifier")
    task_id: Optional[str] = Field(None, description="Task identifier")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "listing_id": "b541cad1-a607-4cba-996b-20e99f81706c",
                "amount": 188.0,
                "currency_code": "USD",
                "status": "ACTIVE",
                "inventory_type": "STANDARD",
                "created_at": "2025-10-22T14:24:45.422Z",
                "updated_at": "2025-10-22T23:29:07.581Z",
                "ask_id": "14773538979930997587",
                "ask_created_at": "2025-10-22T14:24:46.000Z",
                "ask_updated_at": "2025-10-22T14:24:46.000Z",
                "ask_expires_at": "2026-10-22T23:29:04.000Z",
                "product_id": "f1a93305-162c-42ee-be98-eac560097f7e",
                "product_name": "Nike Air Force 1 Low White Black (2018)",
                "style_id": "AO2423-101",
                "variant_id": "7bd1da1c-1ebc-4d00-8bf0-a023d608e2b2",
                "variant_name": "Nike-Air-Force-1-Low-White-Black-2018:6",
                "variant_value": "10",
                "batch_id": "35bf0c79-ae48-44de-85d8-7ba16b8fb54d",
                "task_id": "269932ee-2a44-43d7-9379-8d3974d0cce4"
            }
        }


class ListingsResponse(BaseModel):
    """Schema for paginated listings response."""
    listings: List[ListingResponse] = Field(..., description="List of listings")
    total_count: int = Field(..., description="Total number of listings returned")

    class Config:
        json_schema_extra = {
            "example": {
                "listings": [
                    {
                        "listing_id": "b541cad1-a607-4cba-996b-20e99f81706c",
                        "amount": 188.0,
                        "currency_code": "USD",
                        "status": "ACTIVE",
                        "inventory_type": "STANDARD",
                        "created_at": "2025-10-22T14:24:45.422Z",
                        "updated_at": "2025-10-22T23:29:07.581Z",
                        "product_id": "f1a93305-162c-42ee-be98-eac560097f7e",
                        "product_name": "Nike Air Force 1 Low White Black (2018)",
                        "variant_id": "7bd1da1c-1ebc-4d00-8bf0-a023d608e2b2",
                        "variant_value": "10"
                    }
                ],
                "total_count": 3
            }
        }


class CreateListingRequest(BaseModel):
    """Schema for create listing request."""
    variantId: str = Field(..., description="Variant identifier")
    amount: str = Field(..., description="Listing amount/price")
    currencyCode: str = Field(default="USD", description="Currency code")
    active: bool = Field(default=True, description="Active status")
    quantity: int = Field(default=1, description="Quantity")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "variantId": "7bd1da1c-1ebc-4d00-8bf0-a023d608e2b2",
                "amount": "188.0",
                "currencyCode": "USD",
                "active": True,
                "quantity": 1
            }
        }


class CreateBatchListingsRequest(BaseModel):
    """Schema for create batch listings request."""
    items: List[CreateListingRequest] = Field(..., description="List of listings")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "variantId": "7bd1da1c-1ebc-4d00-8bf0-a023d608e2b2",
                        "amount": "188.0",
                        "currencyCode": "USD",
                        "active": True,
                        "quantity": 1 
                    }
                ]
            }
        }

class CreateBatchListingsResponse(BaseModel):
    """Schema for create batch listings response."""
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="Status")
    total_items: int = Field(..., description="Total items")

    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "35bf0c79-ae48-44de-85d8-7ba16b8fb54d",
                "status": "COMPLETED",
                "total_items": 1
            }
        }


class UpdateListingRequest(BaseModel):
    """Schema for update listing request."""
    listingId: str = Field(..., description="Listing identifier")
    amount: str = Field(..., description="Listing amount/price")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "listingId": "b541cad1-a607-4cba-996b-20e99f81706c",
                "amount": "188.0",
            }
        }

class UpdateBatchListingsRequest(BaseModel):
    """Schema for update batch listings request."""
    items: List[UpdateListingRequest] = Field(..., description="List of listings")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "listingId": "b541cad1-a607-4cba-996b-20e99f81706c",
                        "amount": "188.0",
                    }
                ]
            }
        }
    
class UpdateBatchListingsResponse(BaseModel):
    """Schema for update batch listings response."""
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="Status")
    total_items: int = Field(..., description="Total items")

    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "35bf0c79-ae48-44de-85d8-7ba16b8fb54d",
                "status": "COMPLETED",
                "total_items": 1
            }
        }