"""
Product domain entity.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.value_objects import ProductId, StyleId, Money


class Product(BaseModel):
    """
    Product entity representing a StockX product.

    This is a domain entity - mutable and identified by product_id.
    Follows DDD principles with proper encapsulation and business logic.
    """
    product_id: ProductId = Field(..., description="Unique product identifier")
    title: str = Field(..., min_length=1, max_length=500, description="Product title")
    brand: str = Field(..., min_length=1, max_length=100, description="Brand name")
    style_id: StyleId = Field(..., description="Style/SKU identifier")
    product_type: Optional[str] = Field(None, max_length=100, description="Product category/type")
    url_key: Optional[str] = Field(None, max_length=255, description="URL slug for product page")
    retail_price: Optional[Money] = Field(None, description="Original retail price")
    release_date: Optional[datetime] = Field(None, description="Official release date")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Entity creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        # Allow mutation for entities (unlike value objects)
        frozen = False
        # Prevent extra fields to avoid data leakage
        extra = "forbid"
        # Use enum values
        use_enum_values = True
        # Validate on assignment
        validate_assignment = True

    @field_validator('title', 'brand')
    @classmethod
    def string_must_not_be_empty(cls, v):
        """Ensure strings are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator('url_key')
    @classmethod
    def url_key_must_be_valid(cls, v):
        """Validate URL key format."""
        if v is not None:
            v = v.strip().lower()
            # Basic validation - can be extended
            if ' ' in v:
                raise ValueError("URL key cannot contain spaces")
        return v

    # Business logic methods

    def update_price(self, new_price: Money) -> None:
        """
        Update retail price with business logic.

        Args:
            new_price: New price to set

        Raises:
            ValueError: If price is invalid
        """
        if new_price.amount <= 0:
            raise ValueError("Price must be positive")
        self.retail_price = new_price
        self.updated_at = datetime.utcnow()

    def update_title(self, new_title: str) -> None:
        """
        Update product title.

        Args:
            new_title: New title

        Raises:
            ValueError: If title is invalid
        """
        if not new_title or not new_title.strip():
            raise ValueError("Title cannot be empty")
        if len(new_title) > 500:
            raise ValueError("Title too long (max 500 characters)")
        self.title = new_title.strip()
        self.updated_at = datetime.utcnow()

    def update_release_date(self, release_date: datetime) -> None:
        """Update release date."""
        self.release_date = release_date
        self.updated_at = datetime.utcnow()

    def is_released(self) -> bool:
        """Check if product has been released."""
        if self.release_date is None:
            return True  # Unknown release date, assume released
        return datetime.utcnow() >= self.release_date

    def days_since_release(self) -> Optional[int]:
        """Calculate days since release."""
        if self.release_date is None:
            return None
        if not self.is_released():
            return None
        delta = datetime.utcnow() - self.release_date
        return delta.days

    # Persistence methods

    def to_dict(self) -> dict:
        """
        Convert to dictionary for API responses.

        This prevents data leakage by explicitly defining what gets serialized.
        Converts Money objects to floats for API compatibility.

        Returns:
            Dictionary representation safe for API responses
        """
        return {
            "product_id": str(self.product_id.value),
            "title": self.title,
            "brand": self.brand,
            "style_id": str(self.style_id.value),
            "product_type": self.product_type,
            "url_key": self.url_key,
            "retail_price": float(self.retail_price.amount) if self.retail_price else None,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """
        Create Product from dictionary (e.g., from database).

        Args:
            data: Dictionary with product data

        Returns:
            Product instance
        """
        # Convert nested objects
        if 'product_id' in data and isinstance(data['product_id'], str):
            data['product_id'] = ProductId(value=data['product_id'])
        if 'style_id' in data and isinstance(data['style_id'], str):
            data['style_id'] = StyleId(value=data['style_id'])
        if 'retail_price' in data and data['retail_price'] is not None:
            if isinstance(data['retail_price'], dict):
                data['retail_price'] = Money(**data['retail_price'])

        # Parse dates
        for date_field in ['release_date', 'created_at', 'updated_at']:
            if date_field in data and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(data[date_field])

        return cls(**data)

    # Equality and hashing (based on identity)

    def __eq__(self, other):
        """Products are equal if they have the same ID."""
        if not isinstance(other, Product):
            return False
        return self.product_id == other.product_id

    def __hash__(self):
        """Hash based on product ID for use in sets/dicts."""
        return hash(self.product_id)

    def __str__(self) -> str:
        """String representation."""
        return f"Product({self.product_id}: {self.brand} {self.title})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<Product id={self.product_id} style_id={self.style_id} title='{self.title[:30]}...'>"
