"""Pricing-related API routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.pricing import OptimalPriceResponse
from app.services.pricing_service import PricingService
from app.repositories.pricing_repository import PricingRepository
from app.api.dependencies import get_pricing_service, get_pricing_repository
from app.core.exceptions import DataNotFoundException, PricingCalculationException

router = APIRouter(prefix="/api/v1/pricing", tags=["Pricing"])


@router.get("/{product_id}/optimal", response_model=OptimalPriceResponse)
async def get_optimal_price(
    product_id: str,
    days_back: int = 30,
    pricing_service: PricingService = Depends(get_pricing_service)
):
    """
    Calculate and return the optimal price for a product.

    The optimal price is calculated based on historical pricing data
    using the configured pricing algorithm.
    """
    try:
        result = await pricing_service.calculate_optimal_price(
            product_id=product_id,
            days_back=days_back
        )

        return OptimalPriceResponse(**result)

    except DataNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message)
        )
    except PricingCalculationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e.message)
        )


@router.get("/{product_id}/statistics")
async def get_price_statistics(
    product_id: str,
    days: int = 30,
    pricing_repo: PricingRepository = Depends(get_pricing_repository)
):
    """
    Get price statistics for a product over a specified period.

    Returns min, max, average prices and data point count.
    """
    try:
        stats = await pricing_repo.get_price_statistics(
            product_id=product_id,
            days=days
        )

        return {
            "product_id": product_id,
            "period_days": days,
            **stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate statistics: {str(e)}"
        )
