"""
API routes for external StockX market data.
Handles fetching sales, bids, asks, and historical data from external service.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.stockx import (
    SalesResponse, SaleResponse,
    BidsResponse, BidResponse,
    AsksResponse, AskResponse,
    HistoricalSalesResponse, HistoricalSaleResponse
)
from app.services.external_stockx import external_stockx_service
from app.core.exceptions import APIClientException

router = APIRouter()


def get_external_stockx_service():
    """Dependency for external StockX service."""
    return external_stockx_service


@router.get("/{product_id}/sales", response_model=SalesResponse)
async def get_sales(
    product_id: str,
    is_variant: bool = True,
    service = Depends(get_external_stockx_service)
):
    """
    Fetch sales data for a StockX product or variant from external API.

    This endpoint fetches historical sales data including prices and timestamps
    from an external market data service.

    Args:
        product_id: StockX product or variant UUID
        is_variant: Whether the ID is for a variant (default: True) or product (False)

    Returns:
        List of sales with prices and timestamps

    Raises:
        500: API error or service unavailable
    """
    try:
        # Fetch sales from external service
        sales = await service.get_sales(product_id, is_variant)

        # Convert domain models to response schemas
        sale_responses = [SaleResponse(**sale.to_dict()) for sale in sales]

        return SalesResponse(
            sales=sale_responses,
            total_count=len(sale_responses)
        )

    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sales data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{product_id}/bids", response_model=BidsResponse)
async def get_bids(
    product_id: str,
    is_variant: bool = True,
    service = Depends(get_external_stockx_service)
):
    """
    Fetch bids data for a StockX product or variant from external API.

    This endpoint fetches current bid price levels including the number of bids
    at each price level from an external market data service.

    Args:
        product_id: StockX product or variant UUID
        is_variant: Whether the ID is for a variant (default: True) or product (False)

    Returns:
        List of bids with price levels and counts

    Raises:
        500: API error or service unavailable
    """
    try:
        # Fetch bids from external service
        bids = await service.get_bids(product_id, is_variant)

        # Convert domain models to response schemas
        bid_responses = [BidResponse(**bid.to_dict()) for bid in bids]

        return BidsResponse(
            bids=bid_responses,
            total_count=len(bid_responses)
        )

    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch bids data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{product_id}/asks", response_model=AsksResponse)
async def get_asks(
    product_id: str,
    is_variant: bool = True,
    service = Depends(get_external_stockx_service)
):
    """
    Fetch asks data for a StockX product or variant from external API.

    This endpoint fetches current ask price levels including the number of asks
    at each price level from an external market data service.

    Args:
        product_id: StockX product or variant UUID
        is_variant: Whether the ID is for a variant (default: True) or product (False)

    Returns:
        List of asks with price levels and counts

    Raises:
        500: API error or service unavailable
    """
    try:
        # Fetch asks from external service
        asks = await service.get_asks(product_id, is_variant)

        # Convert domain models to response schemas
        ask_responses = [AskResponse(**ask.to_dict()) for ask in asks]

        return AsksResponse(
            asks=ask_responses,
            total_count=len(ask_responses)
        )

    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch asks data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{product_id}/historical-sales", response_model=HistoricalSalesResponse)
async def get_historical_sales(
    product_id: str,
    is_variant: bool = True,
    intervals: int = Query(default=400, ge=1, le=1000, description="Number of data points to return"),
    start_date: Optional[str] = Query(default=None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(default=None, description="End date in YYYY-MM-DD format"),
    service = Depends(get_external_stockx_service)
):
    """
    Fetch historical sales data for a StockX product or variant from external API.

    This endpoint fetches time-series historical sales data showing price trends
    over time from an external market data service.

    Args:
        product_id: StockX product or variant UUID
        is_variant: Whether the ID is for a variant (default: True) or product (False)
        intervals: Number of data points to return (default: 400, max: 1000)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        List of historical sales data points with timestamps and prices

    Raises:
        500: API error or service unavailable
    """
    try:
        # Fetch historical sales from external service
        historical_sales = await service.get_historical_sales(
            product_id, is_variant, intervals, start_date, end_date
        )

        # Convert domain models to response schemas
        historical_sale_responses = [
            HistoricalSaleResponse(**historical_sale.to_dict())
            for historical_sale in historical_sales
        ]

        return HistoricalSalesResponse(
            historical_sales=historical_sale_responses,
            total_count=len(historical_sale_responses)
        )

    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical sales data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
