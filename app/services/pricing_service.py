"""Pricing calculation and optimization service."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.exceptions import PricingCalculationException, DataNotFoundException
from app.core.logging import LoggerMixin
from app.repositories.pricing_repository import PricingRepository


class PricingService(LoggerMixin):
    """Service for calculating optimal prices based on historical data."""

    def __init__(self):
        self.pricing_repo = PricingRepository()

    async def calculate_optimal_price(
        self,
        product_id: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Calculate optimal price for a product based on historical data.

        Args:
            product_id: Product identifier
            days_back: Number of days to analyze

        Returns:
            Dictionary with optimal price and metadata

        Raises:
            DataNotFoundException: If no historical data exists
            PricingCalculationException: If calculation fails
        """
        try:
            self.logger.info(f"Calculating optimal price for {product_id}")

            # Get historical data
            start_date = datetime.utcnow() - timedelta(days=days_back)
            historical_prices = await self.pricing_repo.get_historical_prices_by_product(
                product_id=product_id,
                start_date=start_date
            )

            if not historical_prices:
                raise DataNotFoundException(
                    f"No historical price data found for product: {product_id}"
                )

            # Get statistics
            stats = await self.pricing_repo.get_price_statistics(
                product_id=product_id,
                days=days_back
            )

            # TODO: Implement your pricing algorithm here
            # This is a simple example - replace with your actual logic
            optimal_price = self._calculate_price_with_margin(
                avg_price=stats["avg"],
                min_price=stats["min"],
                max_price=stats["max"]
            )

            # Calculate confidence score based on data quality
            confidence_score = self._calculate_confidence_score(stats["count"], days_back)

            return {
                "product_id": product_id,
                "optimal_price": optimal_price,
                "confidence_score": confidence_score,
                "calculated_at": datetime.utcnow(),
                "data_points_used": stats["count"],
                "statistics": stats
            }

        except DataNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to calculate optimal price: {str(e)}")
            raise PricingCalculationException(f"Price calculation failed: {str(e)}")

    def _calculate_price_with_margin(
        self,
        avg_price: float,
        min_price: float,
        max_price: float
    ) -> float:
        """Calculate price with configured margin.

        Args:
            avg_price: Average historical price
            min_price: Minimum historical price
            max_price: Maximum historical price

        Returns:
            Calculated optimal price

        Note: This is a simple example. Implement your actual pricing logic here.
        """
        # Simple example: Use average price with a margin
        margin_multiplier = 1 + (settings.default_margin_percentage / 100)
        base_price = avg_price * margin_multiplier

        # Apply thresholds
        if base_price < settings.min_price_threshold:
            base_price = settings.min_price_threshold
        elif base_price > settings.max_price_threshold:
            base_price = settings.max_price_threshold

        return round(base_price, 2)

    def _calculate_confidence_score(self, data_points: int, days_requested: int) -> float:
        """Calculate confidence score based on data quality.

        Args:
            data_points: Number of data points available
            days_requested: Number of days analyzed

        Returns:
            Confidence score between 0 and 1
        """
        # Simple confidence calculation
        # More data points = higher confidence
        expected_points = days_requested
        score = min(data_points / expected_points, 1.0) if expected_points > 0 else 0.0

        return round(score, 2)


# Singleton instance
pricing_service = PricingService()
