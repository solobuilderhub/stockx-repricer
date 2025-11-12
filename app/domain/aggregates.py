"""
Domain aggregates (aggregate roots).

Aggregates ensure consistency boundaries and enforce invariants across
related entities.
"""
from typing import List, Optional, Dict
from datetime import datetime
from app.domain.product import Product
from app.domain.variant import Variant
from app.domain.listing import Listing
from app.domain.value_objects import ProductId, VariantId, Money


class ProductAggregate:
    """
    Aggregate root for Product with its Variants.

    Ensures consistency across product and its variants.
    All modifications go through this aggregate.
    """

    def __init__(self, product: Product, variants: Optional[List[Variant]] = None):
        """
        Initialize product aggregate.

        Args:
            product: Product entity (aggregate root)
            variants: List of variants belonging to this product
        """
        self._product = product
        self._variants: Dict[VariantId, Variant] = {}

        if variants:
            for variant in variants:
                if not variant.belongs_to_product(product.product_id):
                    raise ValueError(
                        f"Variant {variant.variant_id} does not belong to product {product.product_id}"
                    )
                self._variants[variant.variant_id] = variant

    @property
    def product(self) -> Product:
        """Get the product (aggregate root)."""
        return self._product

    @property
    def product_id(self) -> ProductId:
        """Get product ID."""
        return self._product.product_id

    @property
    def variants(self) -> List[Variant]:
        """Get all variants."""
        return list(self._variants.values())

    def variant_count(self) -> int:
        """Get number of variants."""
        return len(self._variants)

    def has_variants(self) -> bool:
        """Check if product has any variants."""
        return len(self._variants) > 0

    # Variant management

    def add_variant(self, variant: Variant) -> None:
        """
        Add a variant to this product.

        Args:
            variant: Variant to add

        Raises:
            ValueError: If variant doesn't belong to this product or already exists
        """
        if not variant.belongs_to_product(self.product_id):
            raise ValueError(f"Variant {variant.variant_id} does not belong to this product")

        if variant.variant_id in self._variants:
            raise ValueError(f"Variant {variant.variant_id} already exists")

        self._variants[variant.variant_id] = variant
        self._product.updated_at = datetime.utcnow()

    def remove_variant(self, variant_id: VariantId) -> None:
        """
        Remove a variant from this product.

        Args:
            variant_id: ID of variant to remove

        Raises:
            ValueError: If variant doesn't exist
        """
        if variant_id not in self._variants:
            raise ValueError(f"Variant {variant_id} not found")

        del self._variants[variant_id]
        self._product.updated_at = datetime.utcnow()

    def get_variant(self, variant_id: VariantId) -> Optional[Variant]:
        """
        Get a specific variant.

        Args:
            variant_id: Variant ID

        Returns:
            Variant if found, None otherwise
        """
        return self._variants.get(variant_id)

    def find_variant_by_value(self, variant_value: str) -> Optional[Variant]:
        """
        Find variant by its value (e.g., size).

        Args:
            variant_value: Value to search for

        Returns:
            First matching variant or None
        """
        for variant in self._variants.values():
            if variant.variant_value == variant_value:
                return variant
        return None

    def find_variants_by_name(self, variant_name: str) -> List[Variant]:
        """
        Find all variants with specific name.

        Args:
            variant_name: Name to search for

        Returns:
            List of matching variants
        """
        return [
            variant for variant in self._variants.values()
            if variant.variant_name == variant_name
        ]

    # Market data management

    def get_variants_with_stale_market_data(self, max_age_seconds: int = 3600) -> List[Variant]:
        """
        Get variants that need market data refresh.

        Args:
            max_age_seconds: Maximum age before considering stale

        Returns:
            List of variants with stale or missing market data
        """
        return [
            variant for variant in self._variants.values()
            if variant.is_market_data_stale(max_age_seconds)
        ]

    # Price analysis

    def get_lowest_ask_across_variants(self) -> Optional[Money]:
        """
        Get the lowest ask price across all variants.

        Returns:
            Lowest ask Money or None if no market data
        """
        lowest = None
        for variant in self._variants.values():
            ask = variant.get_lowest_ask()
            if ask:
                if lowest is None or ask.amount < lowest.amount:
                    lowest = ask
        return lowest

    def get_highest_bid_across_variants(self) -> Optional[Money]:
        """
        Get the highest bid price across all variants.

        Returns:
            Highest bid Money or None if no market data
        """
        highest = None
        for variant in self._variants.values():
            bid = variant.get_highest_bid()
            if bid:
                if highest is None or bid.amount > highest.amount:
                    highest = bid
        return highest

    # Persistence

    def to_dict(self) -> Dict:
        """
        Convert aggregate to dictionary for persistence.

        Returns:
            Dictionary with product and variants
        """
        return {
            "product": self._product.to_dict(),
            "variants": [variant.to_dict() for variant in self._variants.values()]
        }

    def __eq__(self, other):
        """Aggregates are equal if their root entities are equal."""
        if not isinstance(other, ProductAggregate):
            return False
        return self.product_id == other.product_id

    def __hash__(self):
        return hash(self.product_id)

    def __str__(self) -> str:
        return f"ProductAggregate({self.product_id}: {self.variant_count()} variants)"

    def __repr__(self) -> str:
        return (
            f"<ProductAggregate product_id={self.product_id} "
            f"title='{self._product.title[:30]}...' variants={self.variant_count()}>"
        )


class ListingAggregate:
    """
    Aggregate for managing multiple listings for a variant.

    Useful for batch operations and ensuring consistency.
    """

    def __init__(self, variant_id: VariantId, listings: Optional[List[Listing]] = None):
        """
        Initialize listing aggregate.

        Args:
            variant_id: Variant these listings belong to
            listings: Initial list of listings
        """
        self._variant_id = variant_id
        self._listings: Dict[str, Listing] = {}

        if listings:
            for listing in listings:
                if not listing.belongs_to_variant(variant_id):
                    raise ValueError(f"Listing {listing.listing_id} does not belong to variant {variant_id}")
                self._listings[listing.listing_id] = listing

    @property
    def variant_id(self) -> VariantId:
        """Get variant ID."""
        return self._variant_id

    @property
    def listings(self) -> List[Listing]:
        """Get all listings."""
        return list(self._listings.values())

    def listing_count(self) -> int:
        """Get number of listings."""
        return len(self._listings)

    def add_listing(self, listing: Listing) -> None:
        """Add a listing."""
        if not listing.belongs_to_variant(self._variant_id):
            raise ValueError(f"Listing does not belong to variant {self._variant_id}")

        if listing.listing_id in self._listings:
            raise ValueError(f"Listing {listing.listing_id} already exists")

        self._listings[listing.listing_id] = listing

    def remove_listing(self, listing_id: str) -> None:
        """Remove a listing."""
        if listing_id not in self._listings:
            raise ValueError(f"Listing {listing_id} not found")
        del self._listings[listing_id]

    def get_listing(self, listing_id: str) -> Optional[Listing]:
        """Get specific listing."""
        return self._listings.get(listing_id)

    def get_active_listings(self) -> List[Listing]:
        """Get all active listings."""
        return [listing for listing in self._listings.values() if listing.is_active()]

    def get_sold_listings(self) -> List[Listing]:
        """Get all sold listings."""
        return [listing for listing in self._listings.values() if listing.is_sold()]

    def cancel_all_active(self) -> int:
        """
        Cancel all active listings.

        Returns:
            Number of listings cancelled
        """
        count = 0
        for listing in self._listings.values():
            if listing.is_active():
                listing.cancel()
                count += 1
        return count

    def update_all_prices(self, new_amount: Money) -> int:
        """
        Update price for all modifiable listings.

        Args:
            new_amount: New price

        Returns:
            Number of listings updated
        """
        count = 0
        for listing in self._listings.values():
            if listing.is_modifiable():
                try:
                    listing.update_price(new_amount)
                    count += 1
                except ValueError:
                    # Skip if can't update (e.g., currency mismatch)
                    pass
        return count

    def total_quantity(self) -> int:
        """Get total quantity across all active listings."""
        return sum(
            listing.quantity for listing in self._listings.values()
            if listing.is_active()
        )

    def __str__(self) -> str:
        return f"ListingAggregate({self._variant_id}: {self.listing_count()} listings)"

    def __repr__(self) -> str:
        active = len(self.get_active_listings())
        return f"<ListingAggregate variant_id={self._variant_id} total={self.listing_count()} active={active}>"
