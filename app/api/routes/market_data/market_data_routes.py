"""API routes for market data operations."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.market_data import (
    StoreMarketDataRequest,
    StoreMarketDataResponse,
    StoredSaleResponse,
    StoredHistoricalPricingResponse,
    GetSalesResponse,
    GetHistoricalPricingResponse
)
from app.services.market_data.market_data_service import market_data_service
from app.core.exceptions import APIClientException, DatabaseException


router = APIRouter(prefix="/market-data", tags=["Market Data"])


def get_market_data_service():
    """Dependency for market data service."""
    return market_data_service


@router.post(
    "/variants/{variant_db_id}/store",
    response_model=StoreMarketDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Store sales and historical pricing data for a variant"
)
async def store_variant_market_data(
    variant_db_id: str,
    request: StoreMarketDataRequest,
    service = Depends(get_market_data_service)
):
    """
    Fetch and store sales and historical pricing data for a variant.

    This endpoint will:
    1. Validate that the variant exists in the database
    2. Fetch sales data from StockX API
    3. Fetch historical pricing data from StockX API with configurable parameters
    4. Filter out records that already exist (idempotent)
    5. Store new records in MongoDB Time Series Collections
    6. Return the list of newly stored records

    Args:
        variant_db_id: MongoDB ID of the variant
        request: Configuration for historical pricing fetch (intervals, date range)

    Returns:
        List of newly stored sales and pricing records with counts

    Raises:
        400: Variant not found
        500: External API error or database error
    """
    try:
        # Fetch and store market data
        sales, pricing, sales_count, pricing_count = await service.fetch_and_store_variant_market_data(
            variant_db_id=variant_db_id,
            intervals=request.intervals,
            start_date=request.start_date,
            end_date=request.end_date
        )

        # Convert domain models to response schemas
        sales_responses = [
            StoredSaleResponse(
                id=str(sale.product_id),  # Using product_id as placeholder for ID
                variant_id=sale.product_id,
                sale_date=sale.created_at,
                amount=float(sale.amount.amount),
                currency_code=sale.amount.currency_code,
                size=sale.size,
                order_type=sale.order_type
            )
            for sale in sales
        ]

        pricing_responses = [
            StoredHistoricalPricingResponse(
                id=str(pricing_item.product_id),  # Using product_id as placeholder for ID
                variant_id=pricing_item.product_id,
                date=pricing_item.date,
                price=pricing_item.price
            )
            for pricing_item in pricing
        ]

        return StoreMarketDataResponse(
            sales=sales_responses,
            historical_pricing=pricing_responses,
            sales_stored_count=sales_count,
            pricing_stored_count=pricing_count,
            message=f"Successfully stored {sales_count} sales and {pricing_count} pricing records"
        )

    except ValueError as e:
        # Variant not found
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except APIClientException as e:
        # External API error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data from StockX API: {str(e)}"
        )
    except DatabaseException as e:
        # Database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation failed: {str(e)}"
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/variants/{variant_db_id}/sales",
    response_model=GetSalesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get sales data for a variant"
)
async def get_variant_sales(
    variant_db_id: str,
    start_date: Optional[str] = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date filter (YYYY-MM-DD)"),
    service = Depends(get_market_data_service)
):
    """
    Get sales data for a variant from the database.

    This endpoint will:
    1. Validate that the variant exists in the database
    2. Fetch sales records from MongoDB Time Series Collection
    3. Optionally filter by date range
    4. Return the sales data

    Args:
        variant_db_id: MongoDB ID of the variant
        start_date: Optional start date filter (YYYY-MM-DD format)
        end_date: Optional end date filter (YYYY-MM-DD format)

    Returns:
        Sales records with total count

    Raises:
        400: Variant not found
        500: Database error
    """
    try:
        # Fetch sales from database with variant and product details
        sales_db, variant, product = await service.get_sales_by_variant(
            variant_db_id=variant_db_id,
            start_date=start_date,
            end_date=end_date
        )

        # Convert DB models to response schemas
        sales_responses = [
            StoredSaleResponse(
                id=str(sale.id),
                variant_id=sale.variant_id,
                sale_date=sale.sale_date,
                amount=sale.amount,
                currency_code=sale.currency_code,
                size=sale.size,
                order_type=sale.order_type
            )
            for sale in sales_db
        ]

        # Convert variant and product to response schemas
        from app.schemas.product import ProductResponseSchema, VariantResponseSchema

        variant_response = VariantResponseSchema(
            id=str(variant.id),
            variant_id=variant.variant_id,
            product_id=variant.product_id,
            variant_name=variant.variant_name,
            variant_value=variant.variant_value,
            upc=variant.upc,
            created_at=variant.created_at,
            updated_at=variant.updated_at
        )

        product_response = ProductResponseSchema(
            id=str(product.id),
            product_id=product.product_id,
            title=product.title,
            brand=product.brand,
            product_type=product.product_type,
            style_id=product.style_id,
            url_key=product.url_key,
            retail_price=product.retail_price,
            release_date=product.release_date,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

        return GetSalesResponse(
            sales=sales_responses,
            total_count=len(sales_responses),
            variant=variant_response,
            product=product_response
        )

    except ValueError as e:
        # Variant not found
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseException as e:
        # Database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation failed: {str(e)}"
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/variants/{variant_db_id}/historical-pricing",
    response_model=GetHistoricalPricingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get historical pricing data for a variant"
)
async def get_variant_historical_pricing(
    variant_db_id: str,
    start_date: Optional[str] = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date filter (YYYY-MM-DD)"),
    service = Depends(get_market_data_service)
):
    """
    Get historical pricing data for a variant from the database.

    This endpoint will:
    1. Validate that the variant exists in the database
    2. Fetch historical pricing records from MongoDB Time Series Collection
    3. Optionally filter by date range
    4. Return the pricing data

    Args:
        variant_db_id: MongoDB ID of the variant
        start_date: Optional start date filter (YYYY-MM-DD format)
        end_date: Optional end date filter (YYYY-MM-DD format)

    Returns:
        Historical pricing records with total count

    Raises:
        400: Variant not found
        500: Database error
    """
    try:
        # Fetch historical pricing from database with variant and product details
        pricing_db, variant, product = await service.get_historical_pricing_by_variant(
            variant_db_id=variant_db_id,
            start_date=start_date,
            end_date=end_date
        )

        # Convert DB models to response schemas
        pricing_responses = [
            StoredHistoricalPricingResponse(
                id=str(pricing.id),
                variant_id=pricing.variant_id,
                date=pricing.date,
                price=pricing.price
            )
            for pricing in pricing_db
        ]

        # Convert variant and product to response schemas
        from app.schemas.product import ProductResponseSchema, VariantResponseSchema

        variant_response = VariantResponseSchema(
            id=str(variant.id),
            variant_id=variant.variant_id,
            product_id=variant.product_id,
            variant_name=variant.variant_name,
            variant_value=variant.variant_value,
            upc=variant.upc,
            created_at=variant.created_at,
            updated_at=variant.updated_at
        )

        product_response = ProductResponseSchema(
            id=str(product.id),
            product_id=product.product_id,
            title=product.title,
            brand=product.brand,
            product_type=product.product_type,
            style_id=product.style_id,
            url_key=product.url_key,
            retail_price=product.retail_price,
            release_date=product.release_date,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

        return GetHistoricalPricingResponse(
            historical_pricing=pricing_responses,
            total_count=len(pricing_responses),
            variant=variant_response,
            product=product_response
        )

    except ValueError as e:
        # Variant not found
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseException as e:
        # Database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation failed: {str(e)}"
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
