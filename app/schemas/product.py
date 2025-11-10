"""Product and Variant API schemas for core application."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CreateProductRequest(BaseModel):
    """Schema for creating a product."""
    product_id: str = Field(..., description="StockX product UUID", min_length=36, max_length=36)

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "73e10325-c58f-419c-b7df-81142f77d154"
            }
        }


class CreateProductVariantRequest(BaseModel):
    """Schema for creating product and variant."""
    product_id: str = Field(..., description="StockX product UUID", min_length=36, max_length=36)
    variant_id: str = Field(..., description="StockX variant UUID", min_length=36, max_length=36)

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                "variant_id": "23687534-53ce-4e14-a16a-5f3c66a393d1"
            }
        }


class ProductResponseSchema(BaseModel):
    """Schema for product response."""
    id: str = Field(..., description="MongoDB document ID")
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
                "id": "507f1f77bcf86cd799439011",
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


class VariantResponseSchema(BaseModel):
    """Schema for variant response."""
    id: str = Field(..., description="MongoDB document ID")
    variant_id: str = Field(..., description="Unique variant identifier")
    product_id: str = Field(..., description="Reference to parent product")
    variant_name: str = Field(..., description="Variant name")
    variant_value: str = Field(..., description="Variant value (size, color, etc.)")
    upc: Optional[str] = Field(None, description="UPC barcode")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "variant_id": "23687534-53ce-4e14-a16a-5f3c66a393d1",
                "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                "variant_value": "5W",
                "upc": "195244883486",
                "created_at": "2024-11-03T10:00:00",
                "updated_at": "2024-11-03T10:00:00"
            }
        }


class CreateProductVariantResponse(BaseModel):
    """Schema for create product and variant response."""
    product: ProductResponseSchema = Field(..., description="Created product")
    variant: VariantResponseSchema = Field(..., description="Created variant")

    class Config:
        json_schema_extra = {
            "example": {
                "product": {
                    "id": "507f1f77bcf86cd799439011",
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
                "variant": {
                    "id": "507f1f77bcf86cd799439012",
                    "variant_id": "23687534-53ce-4e14-a16a-5f3c66a393d1",
                    "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                    "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                    "variant_value": "5W",
                    "upc": "195244883486",
                    "created_at": "2024-11-03T10:00:00",
                    "updated_at": "2024-11-03T10:00:00"
                }
            }
        }


class AddVariantRequest(BaseModel):
    """Schema for adding a variant to an existing product."""
    product_id: str = Field(..., description="StockX product UUID", min_length=36, max_length=36)
    variant_id: str = Field(..., description="StockX variant UUID", min_length=36, max_length=36)

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                "variant_id": "ab123456-78cd-90ef-1234-567890abcdef"
            }
        }


class AddVariantResponse(BaseModel):
    """Schema for add variant response."""
    variant: VariantResponseSchema = Field(..., description="Created variant")

    class Config:
        json_schema_extra = {
            "example": {
                "variant": {
                    "id": "507f1f77bcf86cd799439013",
                    "variant_id": "ab123456-78cd-90ef-1234-567890abcdef",
                    "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                    "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                    "variant_value": "6W",
                    "upc": "195244883487",
                    "created_at": "2024-11-03T10:00:00",
                    "updated_at": "2024-11-03T10:00:00"
                }
            }
        }


class CreateProductWithVariantsRequest(BaseModel):
    """Schema for creating a product with multiple variants."""
    product_id: str = Field(..., description="StockX product UUID", min_length=36, max_length=36)
    variant_ids: List[str] = Field(..., description="List of StockX variant UUIDs", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                "variant_ids": [
                    "23687534-53ce-4e14-a16a-5f3c66a393d1",
                    "ab123456-78cd-90ef-1234-567890abcdef",
                    "cd789012-34ef-5678-90ab-cdef12345678"
                ]
            }
        }


class CreateProductWithVariantsResponse(BaseModel):
    """Schema for create product with variants response."""
    product: ProductResponseSchema = Field(..., description="Created product")
    variants: List[VariantResponseSchema] = Field(..., description="Created variants")

    class Config:
        json_schema_extra = {
            "example": {
                "product": {
                    "id": "507f1f77bcf86cd799439011",
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
                        "id": "507f1f77bcf86cd799439012",
                        "variant_id": "23687534-53ce-4e14-a16a-5f3c66a393d1",
                        "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                        "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                        "variant_value": "5W",
                        "upc": "195244883486",
                        "created_at": "2024-11-03T10:00:00",
                        "updated_at": "2024-11-03T10:00:00"
                    },
                    {
                        "id": "507f1f77bcf86cd799439013",
                        "variant_id": "ab123456-78cd-90ef-1234-567890abcdef",
                        "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                        "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                        "variant_value": "6W",
                        "upc": "195244883487",
                        "created_at": "2024-11-03T10:00:00",
                        "updated_at": "2024-11-03T10:00:00"
                    }
                ]
            }
        }


class ProductWithVariantsResponse(BaseModel):
    """Schema for product with its variants."""
    product: ProductResponseSchema = Field(..., description="Product data")
    variants: List[VariantResponseSchema] = Field(..., description="List of variants for this product")

    class Config:
        json_schema_extra = {
            "example": {
                "product": {
                    "id": "507f1f77bcf86cd799439011",
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
                        "id": "507f1f77bcf86cd799439012",
                        "variant_id": "23687534-53ce-4e14-a16a-5f3c66a393d1",
                        "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                        "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                        "variant_value": "5W",
                        "upc": "195244883486",
                        "created_at": "2024-11-03T10:00:00",
                        "updated_at": "2024-11-03T10:00:00"
                    },
                    {
                        "id": "507f1f77bcf86cd799439013",
                        "variant_id": "ab123456-78cd-90ef-1234-567890abcdef",
                        "product_id": "73e10325-c58f-419c-b7df-81142f77d154",
                        "variant_name": "Nike-Air-Max-Pre-Day-Optimism-W:0",
                        "variant_value": "6W",
                        "upc": "195244883487",
                        "created_at": "2024-11-03T10:00:00",
                        "updated_at": "2024-11-03T10:00:00"
                    }
                ]
            }
        }


class GetAllProductsResponse(BaseModel):
    """Schema for get all products response with pagination info."""
    products: List[ProductWithVariantsResponse] = Field(..., description="List of products with their variants")
    total: int = Field(..., description="Total number of products returned")
    skip: int = Field(..., description="Number of products skipped")
    limit: int = Field(..., description="Maximum number of products requested")

    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "product": {
                            "id": "507f1f77bcf86cd799439011",
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
                                "id": "507f1f77bcf86cd799439012",
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
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }
