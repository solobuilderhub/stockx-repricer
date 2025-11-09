"""
Domain models package.

This package contains the core domain models following Domain-Driven Design principles.

Exports:
    - Value Objects: Money, ProductId, VariantId, etc.
    - Entities: Product, Variant, Listing
    - Aggregates: ProductAggregate, ListingAggregate
    - Factories: ProductFactory, VariantFactory, ListingFactory
"""

# Value Objects
from app.domain.value_objects import (
    Money,
    ProductId,
    VariantId,
    StyleId,
    UPC,
    ListingStatus,
    InventoryType,
    BatchStatus,
    MarketData,
    TimeRange
)

# Entities
from app.domain.product import Product
from app.domain.variant import Variant
from app.domain.listing import Listing

# Aggregates
from app.domain.aggregates import (
    ProductAggregate,
    ListingAggregate
)

# Factories
from app.domain.factories import (
    ProductFactory,
    VariantFactory,
    ListingFactory,
    MarketDataFactory
)

__all__ = [
    # Value Objects
    "Money",
    "ProductId",
    "VariantId",
    "StyleId",
    "UPC",
    "ListingStatus",
    "InventoryType",
    "BatchStatus",
    "MarketData",
    "TimeRange",
    # Entities
    "Product",
    "Variant",
    "Listing",
    # Aggregates
    "ProductAggregate",
    "ListingAggregate",
    # Factories
    "ProductFactory",
    "VariantFactory",
    "ListingFactory",
    "MarketDataFactory",
]
