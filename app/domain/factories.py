"""
Domain factories for creating domain entities from external data.

Factories encapsulate the logic of creating complex domain objects,
ensuring all business rules and validations are applied.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from app.domain.product import Product
from app.domain.variant import Variant
from app.domain.listing import Listing
from app.domain.value_objects import (
    ProductId, VariantId, StyleId, UPC, Money,
    MarketData, ListingStatus, InventoryType
)


class ProductFactory:
    """Factory for creating Product domain entities."""

    @staticmethod
    def from_stockx_api(api_data: Dict[str, Any]) -> Product:
        """
        Create Product entity from StockX API response.

        Args:
            api_data: Dictionary from StockX API mapper

        Returns:
            Product domain entity

        Raises:
            ValueError: If required data is missing or invalid
        """
        # Create value objects with validation
        product_id = ProductId(value=api_data['product_id'])
        style_id = StyleId(value=api_data['style_id'])

        # Handle optional retail price
        retail_price = None
        if api_data.get('retail_price') is not None:
            retail_price = Money(
                amount=Decimal(str(api_data['retail_price'])),
                currency_code='USD'  # Default to USD, could be parameterized
            )

        # Parse dates
        release_date = None
        if api_data.get('release_date'):
            if isinstance(api_data['release_date'], str):
                release_date = datetime.fromisoformat(api_data['release_date'])
            elif isinstance(api_data['release_date'], datetime):
                release_date = api_data['release_date']

        created_at = api_data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()

        updated_at = api_data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.utcnow()

        return Product(
            product_id=product_id,
            title=api_data['title'],
            brand=api_data['brand'],
            style_id=style_id,
            product_type=api_data.get('product_type'),
            url_key=api_data.get('url_key'),
            retail_price=retail_price,
            release_date=release_date,
            created_at=created_at,
            updated_at=updated_at
        )

    @staticmethod
    def from_database(db_data: Dict[str, Any]) -> Product:
        """
        Create Product entity from database record.

        Args:
            db_data: Dictionary from database

        Returns:
            Product domain entity
        """
        # Remove MongoDB-specific fields
        clean_data = {k: v for k, v in db_data.items() if k not in ['id', '_id']}

        # Convert retail_price from float to Money object if present
        if 'retail_price' in clean_data and clean_data['retail_price'] is not None:
            if isinstance(clean_data['retail_price'], (int, float)):
                clean_data['retail_price'] = Money(
                    amount=Decimal(str(clean_data['retail_price'])),
                    currency_code='USD'
                )

        return Product.from_dict(clean_data)


class VariantFactory:
    """Factory for creating Variant domain entities."""

    @staticmethod
    def from_stockx_api(api_data: Dict[str, Any], include_market_data: bool = False) -> Variant:
        """
        Create Variant entity from StockX API response.

        Args:
            api_data: Dictionary from StockX API mapper
            include_market_data: Whether to include market data if present

        Returns:
            Variant domain entity

        Raises:
            ValueError: If required data is missing or invalid
        """
        # Create value objects
        variant_id = VariantId(value=api_data['variant_id'])
        product_id = ProductId(value=api_data['product_id'])

        # Handle optional UPC
        upc = None
        if api_data.get('upc'):
            try:
                upc = UPC(value=api_data['upc'])
            except ValueError:
                # Invalid UPC, skip it
                pass

        # Parse dates
        created_at = api_data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()

        updated_at = api_data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.utcnow()

        # Handle market data if requested
        market_data = None
        if include_market_data and api_data.get('market_data'):
            market_data = MarketData(**api_data['market_data'])

        return Variant(
            variant_id=variant_id,
            product_id=product_id,
            variant_name=api_data['variant_name'],
            variant_value=api_data['variant_value'],
            upc=upc,
            market_data=market_data,
            created_at=created_at,
            updated_at=updated_at
        )

    @staticmethod
    def from_database(db_data: Dict[str, Any]) -> Variant:
        """
        Create Variant entity from database record.

        Args:
            db_data: Dictionary from database

        Returns:
            Variant domain entity
        """
        # Remove MongoDB-specific fields and Beanie Link fields
        clean_data = {k: v for k, v in db_data.items() if k not in ['id', '_id', 'product']}

        return Variant.from_dict(clean_data)


class ListingFactory:
    """Factory for creating Listing domain entities."""

    @staticmethod
    def from_stockx_api(api_data: Dict[str, Any]) -> Listing:
        """
        Create Listing entity from StockX API response.

        Args:
            api_data: Dictionary from StockX API mapper

        Returns:
            Listing domain entity

        Raises:
            ValueError: If required data is missing or invalid
        """
        # Create value objects
        variant_id = VariantId(value=api_data['variant_id'])

        product_id = None
        if api_data.get('product_id'):
            product_id = ProductId(value=api_data['product_id'])

        # Create Money from amount
        currency_code = api_data.get('currency_code', 'USD')
        amount = Money(
            amount=Decimal(str(api_data['amount'])),
            currency_code=currency_code
        )

        # Parse status
        status_str = api_data.get('status', 'ACTIVE')
        try:
            status = ListingStatus(status_str)
        except ValueError:
            status = ListingStatus.ACTIVE  # Default fallback

        # Parse inventory type
        inventory_type_str = api_data.get('inventory_type', 'STANDARD')
        try:
            inventory_type = InventoryType(inventory_type_str)
        except ValueError:
            inventory_type = InventoryType.STANDARD  # Default fallback

        # Parse dates
        created_at = api_data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        elif created_at is None:
            created_at = datetime.utcnow()

        updated_at = api_data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        elif updated_at is None:
            updated_at = datetime.utcnow()

        ask_expires_at = None
        if api_data.get('ask_expires_at'):
            if isinstance(api_data['ask_expires_at'], str):
                ask_expires_at = datetime.fromisoformat(api_data['ask_expires_at'].replace('Z', '+00:00'))
            elif isinstance(api_data['ask_expires_at'], datetime):
                ask_expires_at = api_data['ask_expires_at']

        # Parse ask timestamps
        ask_created_at = None
        if api_data.get('ask_created_at'):
            if isinstance(api_data['ask_created_at'], str):
                ask_created_at = datetime.fromisoformat(api_data['ask_created_at'].replace('Z', '+00:00'))
            elif isinstance(api_data['ask_created_at'], datetime):
                ask_created_at = api_data['ask_created_at']

        ask_updated_at = None
        if api_data.get('ask_updated_at'):
            if isinstance(api_data['ask_updated_at'], str):
                ask_updated_at = datetime.fromisoformat(api_data['ask_updated_at'].replace('Z', '+00:00'))
            elif isinstance(api_data['ask_updated_at'], datetime):
                ask_updated_at = api_data['ask_updated_at']

        return Listing(
            listing_id=api_data['listing_id'],
            variant_id=variant_id,
            product_id=product_id,
            amount=amount,
            status=status,
            inventory_type=inventory_type,
            quantity=api_data.get('quantity', 1),
            # Ask details
            ask_id=api_data.get('ask_id'),
            ask_expires_at=ask_expires_at,
            ask_created_at=ask_created_at,
            ask_updated_at=ask_updated_at,
            # Denormalized product details
            product_name=api_data.get('product_name'),
            style_id=api_data.get('style_id'),
            # Denormalized variant details
            variant_name=api_data.get('variant_name'),
            variant_value=api_data.get('variant_value'),
            # Batch details
            batch_id=api_data.get('batch_id'),
            task_id=api_data.get('task_id'),
            created_at=created_at,
            updated_at=updated_at
        )

    @staticmethod
    def from_database(db_data: Dict[str, Any]) -> Listing:
        """
        Create Listing entity from database record.

        Args:
            db_data: Dictionary from database

        Returns:
            Listing domain entity
        """
        return Listing.from_dict(db_data)

    @staticmethod
    def create_new(
        variant_id: str,
        amount: str,
        currency_code: str = 'USD',
        inventory_type: str = 'STANDARD',
        quantity: int = 1
    ) -> Listing:
        """
        Create a new listing for submission to StockX.

        Args:
            variant_id: Variant UUID
            amount: Price as string
            currency_code: Currency code
            inventory_type: Inventory type
            quantity: Quantity to list

        Returns:
            New Listing entity in PENDING status

        Raises:
            ValueError: If validation fails
        """
        import uuid

        return Listing(
            listing_id=str(uuid.uuid4()),  # Generate temporary ID
            variant_id=VariantId(value=variant_id),
            product_id=None,  # Will be set later
            amount=Money(amount=Decimal(amount), currency_code=currency_code),
            status=ListingStatus.PENDING,
            inventory_type=InventoryType(inventory_type),
            quantity=quantity,
            ask_id=None,
            ask_expires_at=None,
            batch_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


class MarketDataFactory:
    """Factory for creating MarketData value objects."""

    @staticmethod
    def from_stockx_api(api_data: Dict[str, Any]) -> MarketData:
        """
        Create MarketData from StockX market data API response.

        Args:
            api_data: Dictionary from StockX market data API

        Returns:
            MarketData value object
        """
        currency_code = api_data.get('currencyCode', api_data.get('currency_code', 'USD'))

        # Helper to create Money if value exists
        def make_money(value: Optional[float]) -> Optional[Money]:
            if value is not None:
                return Money(amount=Decimal(str(value)), currency_code=currency_code)
            return None

        # Extract nested market data
        standard_data = api_data.get('standardMarketData', {})
        flex_data = api_data.get('flexMarketData', {})
        direct_data = api_data.get('directMarketData', {})

        return MarketData(
            product_id=ProductId(value=api_data['productId']) if api_data.get('productId') else None,
            variant_id=VariantId(value=api_data['variantId']) if api_data.get('variantId') else None,
            currency_code=currency_code,
            # Top-level
            highest_bid=make_money(api_data.get('highestBidAmount')),
            lowest_ask=make_money(api_data.get('lowestAskAmount')),
            flex_lowest_ask=make_money(api_data.get('flexLowestAskAmount')),
            earn_more=make_money(api_data.get('earnMoreAmount')),
            sell_faster=make_money(api_data.get('sellFasterAmount')),
            # Standard market data
            standard_lowest_ask=make_money(standard_data.get('lowestAsk')),
            standard_highest_bid=make_money(standard_data.get('highestBidAmount')),
            standard_sell_faster=make_money(standard_data.get('sellFaster')),
            standard_earn_more=make_money(standard_data.get('earnMore')),
            standard_beat_us=make_money(standard_data.get('beatUS')),
            # Flex market data
            flex_highest_bid=make_money(flex_data.get('highestBidAmount')),
            flex_sell_faster=make_money(flex_data.get('sellFaster')),
            flex_earn_more=make_money(flex_data.get('earnMore')),
            flex_beat_us=make_money(flex_data.get('beatUS')),
            # Direct market data
            direct_lowest_ask=make_money(direct_data.get('lowestAsk')),
            direct_highest_bid=make_money(direct_data.get('highestBidAmount')),
            direct_sell_faster=make_money(direct_data.get('sellFaster')),
            direct_earn_more=make_money(direct_data.get('earnMore')),
            direct_beat_us=make_money(direct_data.get('beatUS')),
            snapshot_time=datetime.utcnow()
        )
