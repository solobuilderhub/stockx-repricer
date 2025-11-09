"""
Listing domain entity.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.value_objects import (
    VariantId, ProductId, Money,
    ListingStatus, InventoryType
)


class Listing(BaseModel):
    """
    Listing entity representing an active or historical listing.

    A listing is an offer to sell a specific variant at a specific price.
    Implements business rules for listing lifecycle and state transitions.
    """
    listing_id: str = Field(..., min_length=1, description="Unique listing identifier")
    variant_id: VariantId = Field(..., description="Variant being listed")
    product_id: Optional[ProductId] = Field(None, description="Product identifier (denormalized for queries)")
    amount: Money = Field(..., description="Listing price")
    status: ListingStatus = Field(..., description="Current listing status")
    inventory_type: InventoryType = Field(default=InventoryType.STANDARD, description="Inventory fulfillment type")
    quantity: int = Field(default=1, ge=1, le=100, description="Quantity available")

    # Ask details
    ask_id: Optional[str] = Field(None, description="Associated ask ID from marketplace")
    ask_expires_at: Optional[datetime] = Field(None, description="When the ask expires")
    ask_created_at: Optional[datetime] = Field(None, description="When the ask was created")
    ask_updated_at: Optional[datetime] = Field(None, description="When the ask was updated")

    # Denormalized product details (for query performance)
    product_name: Optional[str] = Field(None, description="Product name (denormalized)")
    style_id: Optional[str] = Field(None, description="Product style ID (denormalized)")

    # Denormalized variant details (for query performance)
    variant_name: Optional[str] = Field(None, description="Variant name (denormalized)")
    variant_value: Optional[str] = Field(None, description="Variant value/size (denormalized)")

    # Batch details
    batch_id: Optional[str] = Field(None, description="Batch operation ID if created in batch")
    task_id: Optional[str] = Field(None, description="Task ID if created in batch")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        frozen = False
        extra = "forbid"
        use_enum_values = True
        validate_assignment = True

    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        """Ensure quantity is positive."""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        if v > 100:
            raise ValueError("Quantity cannot exceed 100")
        return v

    @field_validator('listing_id')
    @classmethod
    def listing_id_must_be_valid(cls, v):
        """Validate listing ID."""
        if not v or not v.strip():
            raise ValueError("Listing ID cannot be empty")
        return v.strip()

    # Business logic methods - State transitions

    def update_price(self, new_amount: Money) -> None:
        """
        Update listing price.

        Args:
            new_amount: New price

        Raises:
            ValueError: If currency mismatch or invalid state
        """
        if new_amount.currency_code != self.amount.currency_code:
            raise ValueError(
                f"Currency mismatch: listing is in {self.amount.currency_code}, "
                f"new amount is in {new_amount.currency_code}"
            )
        if self.status == ListingStatus.SOLD:
            raise ValueError("Cannot update price of a sold listing")
        if self.status == ListingStatus.CANCELLED:
            raise ValueError("Cannot update price of a cancelled listing")

        self.amount = new_amount
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """
        Activate the listing.

        Raises:
            ValueError: If listing cannot be activated
        """
        if self.status == ListingStatus.SOLD:
            raise ValueError("Cannot activate a sold listing")
        if self.status == ListingStatus.ACTIVE:
            return  # Already active, no-op

        self.status = ListingStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the listing (temporarily)."""
        if self.status == ListingStatus.SOLD:
            raise ValueError("Cannot deactivate a sold listing")
        if self.status == ListingStatus.CANCELLED:
            raise ValueError("Cannot deactivate a cancelled listing")

        self.status = ListingStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def mark_as_sold(self) -> None:
        """
        Mark listing as sold.

        This is a terminal state - cannot be undone.
        """
        if self.status == ListingStatus.CANCELLED:
            raise ValueError("Cannot mark cancelled listing as sold")

        self.status = ListingStatus.SOLD
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """
        Cancel the listing.

        This is typically a terminal state.

        Raises:
            ValueError: If listing cannot be cancelled
        """
        if self.status == ListingStatus.SOLD:
            raise ValueError("Cannot cancel a sold listing")
        if self.status == ListingStatus.CANCELLED:
            return  # Already cancelled, no-op

        self.status = ListingStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def expire(self) -> None:
        """Mark listing as expired."""
        if self.status in [ListingStatus.SOLD, ListingStatus.CANCELLED]:
            raise ValueError(f"Cannot expire a {self.status.value} listing")

        self.status = ListingStatus.EXPIRED
        self.updated_at = datetime.utcnow()

    def update_quantity(self, new_quantity: int) -> None:
        """
        Update quantity.

        Args:
            new_quantity: New quantity

        Raises:
            ValueError: If invalid quantity or state
        """
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")
        if new_quantity > 100:
            raise ValueError("Quantity cannot exceed 100")
        if self.status == ListingStatus.SOLD:
            raise ValueError("Cannot update quantity of sold listing")
        if self.status == ListingStatus.CANCELLED:
            raise ValueError("Cannot update quantity of cancelled listing")

        self.quantity = new_quantity
        self.updated_at = datetime.utcnow()

    # Query methods

    def is_active(self) -> bool:
        """Check if listing is currently active."""
        return self.status == ListingStatus.ACTIVE

    def is_sold(self) -> bool:
        """Check if listing has been sold."""
        return self.status == ListingStatus.SOLD

    def is_cancelled(self) -> bool:
        """Check if listing is cancelled."""
        return self.status == ListingStatus.CANCELLED

    def is_modifiable(self) -> bool:
        """Check if listing can be modified."""
        return self.status in [ListingStatus.ACTIVE, ListingStatus.INACTIVE, ListingStatus.PENDING]

    def is_expired(self) -> bool:
        """Check if the ask has expired based on timestamp."""
        if self.status == ListingStatus.EXPIRED:
            return True
        if self.ask_expires_at:
            return datetime.utcnow() > self.ask_expires_at
        return False

    def days_active(self) -> int:
        """Calculate how many days the listing has been active."""
        return (datetime.utcnow() - self.created_at).days

    def belongs_to_variant(self, variant_id: VariantId) -> bool:
        """Check if listing belongs to specific variant."""
        return self.variant_id == variant_id

    # Persistence methods

    def to_dict(self) -> dict:
        """
        Convert to dictionary for API responses.

        Prevents data leakage through explicit serialization control.
        Converts Money objects to floats for API compatibility.

        Returns:
            Dictionary safe for API responses
        """
        # Helper to safely extract value from value objects or strings
        def get_value(obj):
            if obj is None:
                return None
            return str(obj.value) if hasattr(obj, 'value') else str(obj)

        return {
            "listing_id": self.listing_id,
            "variant_id": get_value(self.variant_id),
            "product_id": get_value(self.product_id),
            "amount": float(self.amount.amount),  # Convert Money to float
            "currency_code": self.amount.currency_code,
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "inventory_type": self.inventory_type.value if hasattr(self.inventory_type, 'value') else str(self.inventory_type),
            "quantity": self.quantity,

            # Ask details
            "ask_id": self.ask_id,
            "ask_expires_at": self.ask_expires_at.isoformat() if self.ask_expires_at else None,
            "ask_created_at": self.ask_created_at.isoformat() if self.ask_created_at else None,
            "ask_updated_at": self.ask_updated_at.isoformat() if self.ask_updated_at else None,

            # Product details
            "product_name": self.product_name,
            "style_id": self.style_id,

            # Variant details
            "variant_name": self.variant_name,
            "variant_value": self.variant_value,

            # Batch details
            "batch_id": self.batch_id,
            "task_id": self.task_id,

            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Listing':
        """
        Create Listing from dictionary.

        Args:
            data: Dictionary with listing data

        Returns:
            Listing instance
        """
        # Convert value objects
        if 'variant_id' in data and isinstance(data['variant_id'], str):
            data['variant_id'] = VariantId(value=data['variant_id'])
        if 'product_id' in data and data['product_id'] is not None:
            if isinstance(data['product_id'], str):
                data['product_id'] = ProductId(value=data['product_id'])
        if 'amount' in data and isinstance(data['amount'], dict):
            data['amount'] = Money(**data['amount'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = ListingStatus(data['status'])
        if 'inventory_type' in data and isinstance(data['inventory_type'], str):
            data['inventory_type'] = InventoryType(data['inventory_type'])

        # Parse dates
        for date_field in ['ask_expires_at', 'created_at', 'updated_at']:
            if date_field in data and data[date_field] is not None:
                if isinstance(data[date_field], str):
                    data[date_field] = datetime.fromisoformat(data[date_field])

        return cls(**data)

    # Equality and hashing

    def __eq__(self, other):
        """Listings are equal if they have the same ID."""
        if not isinstance(other, Listing):
            return False
        return self.listing_id == other.listing_id

    def __hash__(self):
        """Hash based on listing ID."""
        return hash(self.listing_id)

    def __str__(self) -> str:
        """String representation."""
        return f"Listing({self.listing_id}: {self.amount} - {self.status.value})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<Listing id={self.listing_id} variant_id={self.variant_id} "
            f"amount={self.amount} status={self.status.value}>"
        )
