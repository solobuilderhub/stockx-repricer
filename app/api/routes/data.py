"""Data collection API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.pricing import (
    DataCollectionRequest,
    DataCollectionResponse,
    HistoricalPriceResponse
)
from app.services.data_collector import DataCollectionService
from app.repositories.pricing_repository import PricingRepository
from app.api.dependencies import get_data_collector, get_pricing_repository

router = APIRouter(prefix="/api/v1/data", tags=["Data Collection"])


@router.post("/collect", response_model=DataCollectionResponse)
async def collect_historical_data(
    request: DataCollectionRequest,
    collector: DataCollectionService = Depends(get_data_collector)
):
    """
    Trigger collection of historical pricing data from external API.

    This endpoint fetches historical price data for the specified products
    and stores it in the database for analysis.
    """
    try:
        results = await collector.collect_historical_data(
            product_ids=request.product_ids,
            days_back=request.days_back
        )

        return DataCollectionResponse(
            status="success" if not results["errors"] else "partial_success",
            products_processed=results["products_processed"],
            records_created=results["records_created"],
            message=f"Processed {results['products_processed']} products, "
                   f"created {results['records_created']} records. "
                   f"Errors: {len(results['errors'])}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data collection failed: {str(e)}"
        )


@router.get("/historical/{product_id}", response_model=List[HistoricalPriceResponse])
async def get_historical_prices(
    product_id: str,
    limit: int = 100,
    pricing_repo: PricingRepository = Depends(get_pricing_repository)
):
    """
    Retrieve historical pricing data for a specific product.

    Returns a list of historical price records sorted by timestamp (newest first).
    """
    try:
        prices = await pricing_repo.get_historical_prices_by_product(
            product_id=product_id,
            limit=limit
        )

        return [
            HistoricalPriceResponse(
                product_id=price.product_id,
                price=price.price,
                timestamp=price.timestamp,
                created_at=price.created_at
            )
            for price in prices
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical data: {str(e)}"
        )
