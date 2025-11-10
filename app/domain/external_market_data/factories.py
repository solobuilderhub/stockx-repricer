"""
Factories for creating external market data domain entities.
"""
from datetime import datetime
from typing import Dict, Any
from decimal import Decimal
from app.domain.external_market_data.sale import Sale
from app.domain.external_market_data.bid import Bid
from app.domain.external_market_data.ask import Ask
from app.domain.external_market_data.historical_sale import HistoricalSale
from app.domain.value_objects import Money


class SaleFactory:
    """Factory for creating Sale domain entities."""

    @staticmethod
    def from_external_api(api_data: Dict[str, Any], product_id: str, is_variant: bool) -> Sale:
        """
        Create Sale entity from external API node data.

        Args:
            api_data: Dictionary from external API (the "node" object)
            product_id: The product or variant ID this sale belongs to
            is_variant: Whether the product_id is a variant ID

        Returns:
            Sale domain entity

        Raises:
            ValueError: If required data is missing or invalid
        """
        # Extract sale amount
        amount_value = api_data.get('amount')
        if amount_value is None:
            raise ValueError("Sale amount is required")

        # Assuming USD currency - adjust if API provides currency
        amount = Money(
            amount=Decimal(str(amount_value)),
            currency_code='USD'
        )

        # Parse created_at timestamp
        created_at_str = api_data.get('createdAt')
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                created_at = datetime.utcnow()
        else:
            created_at = datetime.utcnow()

        # Extract associated variant size if available
        size = None
        associated_variant = api_data.get('associatedVariant', {})
        if associated_variant:
            traits = associated_variant.get('traits', {})
            size = traits.get('size')

        # Extract order type
        order_type = api_data.get('orderType')

        return Sale(
            amount=amount,
            created_at=created_at,
            product_id=product_id,
            is_variant=is_variant,
            size=size,
            order_type=order_type
        )


class BidFactory:
    """Factory for creating Bid domain entities."""

    @staticmethod
    def from_external_api(api_data: Dict[str, Any], product_id: str, is_variant: bool) -> Bid:
        """
        Create Bid entity from external API node data.

        Args:
            api_data: Dictionary from external API (the "node" object)
            product_id: The product or variant ID this bid belongs to
            is_variant: Whether the product_id is a variant ID

        Returns:
            Bid domain entity

        Raises:
            ValueError: If required data is missing or invalid
        """
        # Extract bid amount
        amount_value = api_data.get('amount')
        if amount_value is None:
            raise ValueError("Bid amount is required")

        # Assuming USD currency - adjust if API provides currency
        amount = Money(
            amount=Decimal(str(amount_value)),
            currency_code='USD'
        )

        # Extract bid counts
        count = api_data.get('count', 0)
        own_count = api_data.get('ownCount', 0)
        available_for_flex = api_data.get('availableForFlex', False)

        # Extract variant size if available
        size = None
        variant = api_data.get('variant', {})
        if variant:
            traits = variant.get('traits', {})
            size = traits.get('size')

        return Bid(
            amount=amount,
            count=count,
            own_count=own_count,
            product_id=product_id,
            is_variant=is_variant,
            size=size,
            available_for_flex=available_for_flex
        )


class AskFactory:
    """Factory for creating Ask domain entities."""

    @staticmethod
    def from_external_api(api_data: Dict[str, Any], product_id: str, is_variant: bool) -> Ask:
        """
        Create Ask entity from external API node data.

        Args:
            api_data: Dictionary from external API (the "node" object)
            product_id: The product or variant ID this ask belongs to
            is_variant: Whether the product_id is a variant ID

        Returns:
            Ask domain entity

        Raises:
            ValueError: If required data is missing or invalid
        """
        # Extract ask amount
        amount_value = api_data.get('amount')
        if amount_value is None:
            raise ValueError("Ask amount is required")

        # Assuming USD currency - adjust if API provides currency
        amount = Money(
            amount=Decimal(str(amount_value)),
            currency_code='USD'
        )

        # Extract ask counts
        count = api_data.get('count', 0)
        own_count = api_data.get('ownCount', 0)
        available_for_flex = api_data.get('availableForFlex', False)

        # Extract variant size if available
        size = None
        variant = api_data.get('variant', {})
        if variant:
            traits = variant.get('traits', {})
            size = traits.get('size')

        return Ask(
            amount=amount,
            count=count,
            own_count=own_count,
            product_id=product_id,
            is_variant=is_variant,
            size=size,
            available_for_flex=available_for_flex
        )


class HistoricalSaleFactory:
    """Factory for creating HistoricalSale domain entities."""

    @staticmethod
    def from_external_api(api_data: Dict[str, Any], product_id: str, is_variant: bool) -> HistoricalSale:
        """
        Create HistoricalSale entity from external API series data point.

        Args:
            api_data: Dictionary from external API (the series object with xValue and yValue)
            product_id: The product or variant ID this historical data belongs to
            is_variant: Whether the product_id is a variant ID

        Returns:
            HistoricalSale domain entity

        Raises:
            ValueError: If required data is missing or invalid
        """
        # Extract xValue (date)
        x_value_str = api_data.get('xValue')
        if not x_value_str:
            raise ValueError("Historical sale xValue (date) is required")

        # Parse xValue timestamp
        try:
            date = datetime.fromisoformat(x_value_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid xValue format: {e}")

        # Extract yValue (price)
        y_value = api_data.get('yValue')
        if y_value is None:
            raise ValueError("Historical sale yValue (price) is required")

        # Convert to float
        try:
            price = float(y_value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid yValue: {e}")

        return HistoricalSale(
            date=date,
            price=price,
            product_id=product_id,
            is_variant=is_variant
        )
