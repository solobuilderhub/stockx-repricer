"""
Value Objects for the domain.
Value objects are immutable and compared by their values, not identity.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator, field_validator
from enum import Enum


class Money(BaseModel):
    """
    Value object representing money with currency.
    Immutable and uses Decimal for precision.
    """
    amount: Decimal = Field(..., description="Monetary amount")
    currency_code: str = Field(..., description="ISO 4217 currency code")

    class Config:
        frozen = True  # Make immutable
        json_encoders = {
            Decimal: lambda v: float(v)
        }

    @field_validator('amount')
    @classmethod
    def amount_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v

    @field_validator('currency_code')
    @classmethod
    def currency_code_must_be_valid(cls, v):
        v = v.upper()
        if len(v) != 3:
            raise ValueError("Currency code must be 3 characters (ISO 4217)")
        return v

    def add(self, other: 'Money') -> 'Money':
        """Add two Money objects (must have same currency)."""
        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot add different currencies: {self.currency_code} and {other.currency_code}")
        return Money(amount=self.amount + other.amount, currency_code=self.currency_code)

    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two Money objects (must have same currency)."""
        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot subtract different currencies: {self.currency_code} and {other.currency_code}")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Resulting amount cannot be negative")
        return Money(amount=result, currency_code=self.currency_code)

    def __str__(self) -> str:
        return f"{self.currency_code} {self.amount:.2f}"


class ProductId(BaseModel):
    """Value object for Product ID with validation."""
    value: str = Field(..., min_length=1, max_length=255)

    class Config:
        frozen = True

    @field_validator('value')
    @classmethod
    def value_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Product ID cannot be empty or whitespace")
        return v.strip()

    def __str__(self) -> str:
        return self.value

    def __hash__(self):
        return hash(self.value)


class VariantId(BaseModel):
    """Value object for Variant ID with validation."""
    value: str = Field(..., min_length=1, max_length=255)

    class Config:
        frozen = True

    @field_validator('value')
    @classmethod
    def value_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Variant ID cannot be empty or whitespace")
        return v.strip()

    def __str__(self) -> str:
        return self.value

    def __hash__(self):
        return hash(self.value)


class StyleId(BaseModel):
    """Value object for Style ID (SKU)."""
    value: str = Field(..., min_length=1, max_length=100)

    class Config:
        frozen = True

    @field_validator('value')
    @classmethod
    def value_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError("Style ID cannot be empty")
        # Remove extra whitespace
        return v.strip().upper()

    def __str__(self) -> str:
        return self.value

    def __hash__(self):
        return hash(self.value)


class UPC(BaseModel):
    """Value object for UPC code."""
    value: str = Field(..., pattern=r'^\d{12,14}$')

    class Config:
        frozen = True

    @field_validator('value')
    @classmethod
    def validate_upc(cls, v):
        if not v.isdigit():
            raise ValueError("UPC must contain only digits")
        if len(v) not in [12, 13, 14]:
            raise ValueError("UPC must be 12, 13, or 14 digits")
        return v

    def __str__(self) -> str:
        return self.value


class ListingStatus(str, Enum):
    """Enumeration of possible listing statuses."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SOLD = "SOLD"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"


class InventoryType(str, Enum):
    """Enumeration of inventory types."""
    STANDARD = "STANDARD"
    FLEX = "FLEX"
    DIRECT = "DIRECT"


class BatchStatus(str, Enum):
    """Enumeration of batch operation statuses."""
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class MarketData(BaseModel):
    """
    Value object representing market data for a variant.
    Immutable snapshot of market conditions from StockX API.
    """
    # IDs
    product_id: Optional[ProductId] = Field(None, description="Product identifier")
    variant_id: Optional[VariantId] = Field(None, description="Variant identifier")
    currency_code: str = Field("USD", description="Currency code")

    # Top-level market data
    highest_bid: Optional[Money] = Field(None, description="Highest bid price")
    lowest_ask: Optional[Money] = Field(None, description="Lowest ask price")
    flex_lowest_ask: Optional[Money] = Field(None, description="Flex lowest ask")
    earn_more: Optional[Money] = Field(None, description="Earn more amount")
    sell_faster: Optional[Money] = Field(None, description="Sell faster amount")

    # Standard market data
    standard_lowest_ask: Optional[Money] = Field(None, description="Standard lowest ask")
    standard_highest_bid: Optional[Money] = Field(None, description="Standard highest bid")
    standard_sell_faster: Optional[Money] = Field(None, description="Standard sell faster")
    standard_earn_more: Optional[Money] = Field(None, description="Standard earn more")
    standard_beat_us: Optional[Money] = Field(None, description="Standard beat US")

    # Flex market data
    flex_highest_bid: Optional[Money] = Field(None, description="Flex highest bid")
    flex_sell_faster: Optional[Money] = Field(None, description="Flex sell faster")
    flex_earn_more: Optional[Money] = Field(None, description="Flex earn more")
    flex_beat_us: Optional[Money] = Field(None, description="Flex beat US")

    # Direct market data
    direct_lowest_ask: Optional[Money] = Field(None, description="Direct lowest ask")
    direct_highest_bid: Optional[Money] = Field(None, description="Direct highest bid")
    direct_sell_faster: Optional[Money] = Field(None, description="Direct sell faster")
    direct_earn_more: Optional[Money] = Field(None, description="Direct earn more")
    direct_beat_us: Optional[Money] = Field(None, description="Direct beat US")

    snapshot_time: datetime = Field(default_factory=datetime.utcnow, description="When this data was captured")

    class Config:
        frozen = True

    def spread(self) -> Optional[Money]:
        """Calculate the bid-ask spread."""
        if self.lowest_ask and self.highest_bid:
            try:
                return self.lowest_ask.subtract(self.highest_bid)
            except ValueError:
                return None
        return None

    def midpoint(self) -> Optional[Decimal]:
        """Calculate the midpoint between bid and ask."""
        if self.lowest_ask and self.highest_bid:
            if self.lowest_ask.currency_code == self.highest_bid.currency_code:
                return (self.lowest_ask.amount + self.highest_bid.amount) / Decimal('2')
        return None

    def to_dict(self) -> dict:
        """
        Convert to dictionary for API responses.

        Returns:
            Dictionary representation with serialized values
        """
        return {
            "product_id": str(self.product_id.value) if self.product_id else None,
            "variant_id": str(self.variant_id.value) if self.variant_id else None,
            "currency_code": self.currency_code,
            "highest_bid_amount": float(self.highest_bid.amount) if self.highest_bid else None,
            "lowest_ask_amount": float(self.lowest_ask.amount) if self.lowest_ask else None,
            "flex_lowest_ask_amount": float(self.flex_lowest_ask.amount) if self.flex_lowest_ask else None,
            "earn_more_amount": float(self.earn_more.amount) if self.earn_more else None,
            "sell_faster_amount": float(self.sell_faster.amount) if self.sell_faster else None,
            # Standard market data
            "standard_lowest_ask": float(self.standard_lowest_ask.amount) if self.standard_lowest_ask else None,
            "standard_highest_bid": float(self.standard_highest_bid.amount) if self.standard_highest_bid else None,
            "standard_sell_faster": float(self.standard_sell_faster.amount) if self.standard_sell_faster else None,
            "standard_earn_more": float(self.standard_earn_more.amount) if self.standard_earn_more else None,
            "standard_beat_us": float(self.standard_beat_us.amount) if self.standard_beat_us else None,
            # Flex market data
            "flex_lowest_ask": float(self.flex_lowest_ask.amount) if self.flex_lowest_ask else None,
            "flex_highest_bid": float(self.flex_highest_bid.amount) if self.flex_highest_bid else None,
            "flex_sell_faster": float(self.flex_sell_faster.amount) if self.flex_sell_faster else None,
            "flex_earn_more": float(self.flex_earn_more.amount) if self.flex_earn_more else None,
            "flex_beat_us": float(self.flex_beat_us.amount) if self.flex_beat_us else None,
            # Direct market data
            "direct_lowest_ask": float(self.direct_lowest_ask.amount) if self.direct_lowest_ask else None,
            "direct_highest_bid": float(self.direct_highest_bid.amount) if self.direct_highest_bid else None,
            "direct_sell_faster": float(self.direct_sell_faster.amount) if self.direct_sell_faster else None,
            "direct_earn_more": float(self.direct_earn_more.amount) if self.direct_earn_more else None,
            "direct_beat_us": float(self.direct_beat_us.amount) if self.direct_beat_us else None,
            # Timestamps
            "created_at": self.snapshot_time,
            "updated_at": self.snapshot_time
        }


class TimeRange(BaseModel):
    """Value object representing a time range."""
    start: datetime = Field(..., description="Start of time range")
    end: datetime = Field(..., description="End of time range")

    class Config:
        frozen = True

    @field_validator('end')
    @classmethod
    def end_must_be_after_start(cls, v, info):
        if 'start' in info.data and v <= info.data['start']:
            raise ValueError("End time must be after start time")
        return v

    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return (self.end - self.start).total_seconds()

    def contains(self, dt: datetime) -> bool:
        """Check if a datetime falls within this range."""
        return self.start <= dt <= self.end
