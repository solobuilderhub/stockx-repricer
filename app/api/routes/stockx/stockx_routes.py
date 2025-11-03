"""StockX product API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.schemas.stockx import (
    ProductResponse,
    VariantResponse,
    ProductWithVariantsResponse,
    MarketDataResponse,
    ListingsResponse,
    ListingResponse
)
from app.services.stockx import stockx_service
from app.core.exceptions import APIClientException

router = APIRouter(prefix="/api/stockx", tags=["StockX API Routes"])


def get_stockx_service():
    """Dependency for StockX service."""
    return stockx_service


@router.get("/products/{search_param}", response_model=ProductResponse)
async def get_product(
    search_param: str,
    service = Depends(get_stockx_service)
):
    """
    Fetch product information from StockX by style ID or UPC.

    Args:
        search_param: Product style ID (e.g., "DO6716-700") or UPC code

    Returns:
        Product details including title, brand, pricing, and release information

    Raises:
        404: Product not found
        500: API error or service unavailable
    """
    try:
        product = await service.get_product(search_param)

        # Product is now a dictionary, Pydantic will validate it
        return ProductResponse(**product)

    except APIClientException as e:
        if "No products found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product not found for search parameter: {search_param}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/products/{product_id}/variants", response_model=List[VariantResponse])
async def get_variants(
    product_id: str,
    service = Depends(get_stockx_service)
):
    """
    Fetch all variants (sizes) for a specific StockX product.

    Args:
        product_id: StockX product UUID

    Returns:
        List of product variants with size information and UPC codes

    Raises:
        500: API error or service unavailable
    """
    try:
        variants = await service.get_variants(product_id)

        # Variants are now dictionaries, Pydantic will validate them
        return [VariantResponse(**variant) for variant in variants]

    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch variants: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/products/{search_param}/with-variants", response_model=ProductWithVariantsResponse)
async def get_product_with_variants(
    search_param: str,
    service = Depends(get_stockx_service)
):
    """
    Fetch product and all its variants in a single request.

    This is a convenience endpoint that combines the product and variants
    endpoints to reduce the number of API calls needed.

    Args:
        search_param: Product style ID (e.g., "DO6716-700") or UPC code

    Returns:
        Product details along with all available variants

    Raises:
        404: Product not found
        500: API error or service unavailable
    """
    try:
        product, variants = await service.get_product_with_variants(search_param)

        # Product and variants are now dictionaries, Pydantic will validate them
        return ProductWithVariantsResponse(
            product=ProductResponse(**product),
            variants=[VariantResponse(**variant) for variant in variants]
        )

    except APIClientException as e:
        if "No products found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product not found for search parameter: {search_param}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product with variants: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/products/{product_id}/variants/{variant_id}/market-data",
    response_model=MarketDataResponse
)
async def get_market_data(
    product_id: str,
    variant_id: str,
    currency_code: str = Query(default="USD", description="Currency code (e.g., USD, EUR, GBP)"),
    service = Depends(get_stockx_service)
):
    """
    Fetch market data for a specific product variant.

    This endpoint provides current market pricing information including:
    - Highest bid and lowest ask prices
    - Standard, Flex, and Direct market data
    - Sell faster and earn more recommendations

    Args:
        product_id: StockX product UUID
        variant_id: StockX variant UUID (specific size/color)
        currency_code: Currency code for pricing (default: USD)

    Returns:
        Market data with bid/ask prices and market recommendations

    Raises:
        500: API error or service unavailable
    """
    try:
        market_data = await service.get_market_data(product_id, variant_id, currency_code)

        # Market data is a dictionary, Pydantic will validate it
        return MarketDataResponse(**market_data)

    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/listings", response_model=ListingsResponse)
async def get_listings(
    product_id: Optional[str] = Query(None, description="Product UUID (optional if variant_id provided)"),
    variant_id: Optional[str] = Query(None, description="Variant UUID (optional if product_id provided)"),
    from_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    listing_status: str = Query("ACTIVE", description="Listing status filter"),
    service = Depends(get_stockx_service)
):
    """
    Fetch listings from StockX selling API.

    This endpoint automatically fetches all pages of listings for the given product/variant.
    Either product_id or variant_id must be provided (or both).

    Args:
        product_id: StockX product UUID (optional if variant_id provided)
        variant_id: StockX variant UUID (optional if product_id provided)
        from_date: Filter listings created from this date (format: YYYY-MM-DD)
        listing_status: Filter by listing status (default: ACTIVE)

    Returns:
        All listings matching the criteria

    Raises:
        400: Neither product_id nor variant_id provided
        500: API error or service unavailable
    """
    try:
        # Validate that at least one ID is provided
        if not product_id and not variant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either product_id or variant_id must be provided"
            )

        # Fetch all listings (with automatic pagination)
        listings = await service.get_listings(
            product_id=product_id,
            variant_id=variant_id,
            from_date=from_date,
            listing_status=listing_status,
            fetch_all_pages=True
        )

        # Convert to response schema
        listing_responses = [ListingResponse(**listing) for listing in listings]

        return ListingsResponse(
            listings=listing_responses,
            total_count=len(listing_responses)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch listings: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
