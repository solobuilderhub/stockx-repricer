"""
Variant domain entity.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.value_objects import VariantId, ProductId, UPC, MarketData, Money


class Variant(BaseModel):
    """
    Variant entity representing a specific product variant (e.g., size, color).

    Identified by variant_id and belongs to a Product.
    Implements proper encapsulation and business rules.
    """
    variant_id: VariantId = Field(..., description="Unique variant identifier")
    product_id: ProductId = Field(..., description="Parent product identifier")
    variant_name: str = Field(..., min_length=1, max_length=200, description="Variant attribute name")
    variant_value: str = Field(..., min_length=1, max_length=100, description="Variant attribute value")
    upc: Optional[UPC] = Field(None, description="Universal Product Code")
    market_data: Optional[MarketData] = Field(None, description="Current market data snapshot")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        frozen = False
        extra = "forbid"
        use_enum_values = True
        validate_assignment = True

    @field_validator('variant_name', 'variant_value')
    @classmethod
    def string_must_not_be_empty(cls, v):
        """Ensure strings are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    # Business logic methods

    def update_market_data(self, market_data: MarketData) -> None:
        """
        Update market data snapshot.

        Args:
            market_data: New market data
        """
        self.market_data = market_data
        self.updated_at = datetime.utcnow()

    def clear_market_data(self) -> None:
        """Clear market data (e.g., if stale)."""
        self.market_data = None
        self.updated_at = datetime.utcnow()

    def belongs_to_product(self, product_id: ProductId) -> bool:
        """
        Check if this variant belongs to a specific product.

        Args:
            product_id: Product ID to check

        Returns:
            True if variant belongs to product
        """
        return self.product_id == product_id

    def has_market_data(self) -> bool:
        """Check if variant has market data available."""
        return self.market_data is not None

    def is_market_data_stale(self, max_age_seconds: int = 3600) -> bool:
        """
        Check if market data is stale.

        Args:
            max_age_seconds: Maximum age in seconds before considering stale

        Returns:
            True if data is stale or missing
        """
        if not self.market_data:
            return True

        age = (datetime.utcnow() - self.market_data.snapshot_time).total_seconds()
        return age > max_age_seconds

    def get_lowest_ask(self) -> Optional[Money]:
        """Get lowest ask from market data if available."""
        if self.market_data:
            return self.market_data.lowest_ask
        return None

    def get_highest_bid(self) -> Optional[Money]:
        """Get highest bid from market data if available."""
        if self.market_data:
            return self.market_data.highest_bid
        return None

    # Persistence methods

    def to_dict(self) -> dict:
        """
        Convert to dictionary for API responses.

        Prevents data leakage by explicitly controlling serialization.

        Returns:
            Dictionary safe for API responses
        """
        return {
            "variant_id": str(self.variant_id.value),
            "product_id": str(self.product_id.value),
            "variant_name": self.variant_name,
            "variant_value": self.variant_value,
            "upc": str(self.upc.value) if self.upc else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Variant':
        """
        Create Variant from dictionary.

        Args:
            data: Dictionary with variant data

        Returns:
            Variant instance
        """
        # Convert value objects
        if 'variant_id' in data and isinstance(data['variant_id'], str):
            data['variant_id'] = VariantId(value=data['variant_id'])
        if 'product_id' in data and isinstance(data['product_id'], str):
            data['product_id'] = ProductId(value=data['product_id'])
        if 'upc' in data and data['upc'] is not None and isinstance(data['upc'], str):
            data['upc'] = UPC(value=data['upc'])
        if 'market_data' in data and data['market_data'] is not None:
            if isinstance(data['market_data'], dict):
                data['market_data'] = MarketData(**data['market_data'])

        # Parse dates
        for date_field in ['created_at', 'updated_at']:
            if date_field in data and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(data[date_field])

        return cls(**data)

    # Equality and hashing

    def __eq__(self, other):
        """Variants are equal if they have the same ID."""
        if not isinstance(other, Variant):
            return False
        return self.variant_id == other.variant_id

    def __hash__(self):
        """Hash based on variant ID."""
        return hash(self.variant_id)

    def __str__(self) -> str:
        """String representation."""
        return f"Variant({self.variant_id}: {self.variant_name}={self.variant_value})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<Variant id={self.variant_id} product_id={self.product_id} {self.variant_name}={self.variant_value}>"
