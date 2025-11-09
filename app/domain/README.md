# Domain Layer

This directory contains the core domain models following Domain-Driven Design (DDD) principles.

## Architecture Overview

The domain layer is structured following DDD patterns:

```
domain/
├── value_objects.py   # Immutable value objects
├── product.py         # Product entity
├── variant.py         # Variant entity
├── listing.py         # Listing entity
├── aggregates.py      # Aggregate roots (ProductAggregate, ListingAggregate)
└── factories.py       # Factories for creating domain objects
```

## Key Concepts

### Value Objects (`value_objects.py`)

Immutable objects identified by their values, not identity:

- **Money**: Represents monetary amounts with currency (uses Decimal for precision)
- **ProductId, VariantId**: Type-safe IDs with validation
- **StyleId**: Product SKU/style identifier
- **UPC**: Universal Product Code with validation
- **ListingStatus, InventoryType, BatchStatus**: Enumerations for status values
- **MarketData**: Immutable snapshot of market conditions
- **TimeRange**: Time period representation

**Characteristics:**
- Immutable (`frozen=True`)
- Equality based on values
- Strong validation
- No side effects

### Entities

Objects with identity and lifecycle:

#### Product (`product.py`)
Represents a StockX product with business logic for:
- Price updates
- Title modifications
- Release date tracking
- Data persistence

#### Variant (`variant.py`)
Represents a product variant (size, color) with:
- Market data management
- UPC validation
- Product relationship validation

#### Listing (`listing.py`)
Represents a marketplace listing with:
- State machine for status transitions (ACTIVE → SOLD, etc.)
- Price updates
- Quantity management
- Expiration tracking

**Characteristics:**
- Mutable state
- Identity-based equality (by ID)
- Business logic encapsulation
- Explicit serialization (prevents data leakage)

### Aggregates (`aggregates.py`)

Clusters of entities treated as a single unit:

#### ProductAggregate
- **Root**: Product entity
- **Contains**: Collection of Variant entities
- **Ensures**: All variants belong to the product
- **Provides**: Consistency boundary for product operations

#### ListingAggregate
- **Root**: Variant ID
- **Contains**: Collection of Listing entities
- **Ensures**: All listings belong to the variant
- **Provides**: Batch operations on listings

### Factories (`factories.py`)

Create domain objects from external sources:

- **ProductFactory**: Creates Products from API/database
- **VariantFactory**: Creates Variants from API/database
- **ListingFactory**: Creates Listings from API/database or for new operations
- **MarketDataFactory**: Creates MarketData from API responses

## Best Practices Implemented

### 1. Immutability (Where Appropriate)
Value objects are immutable using `frozen=True`:
```python
class Money(BaseModel):
    class Config:
        frozen = True  # Cannot be modified after creation
```

### 2. Data Validation
All inputs are validated using Pydantic validators:
```python
@field_validator('amount')
@classmethod
def amount_must_be_non_negative(cls, v):
    if v < 0:
        raise ValueError("Amount cannot be negative")
    return v
```

### 3. Preventing Data Leakage
Explicit serialization prevents exposing internal state:
```python
def to_dict(self) -> dict:
    """Only serialize what's needed for persistence."""
    return {
        "product_id": str(self.product_id),
        "title": self.title,
        # Only explicit fields, no accidental leakage
    }
```

### 4. Type Safety
Strong typing with value objects:
```python
# Type-safe, prevents mixing up IDs
product_id: ProductId
variant_id: VariantId

# Prevents accidental string assignment
product.product_id = "123"  # ❌ Type error
product.product_id = ProductId(value="123")  # ✅ Correct
```

### 5. Business Logic Encapsulation
All business rules in domain objects:
```python
# Business logic is in the entity, not scattered in services
listing.activate()  # ✅ Encapsulated
listing.status = ListingStatus.ACTIVE  # ❌ Bypasses business rules
```

### 6. Consistency Boundaries
Aggregates enforce invariants:
```python
aggregate = ProductAggregate(product, variants)
# Cannot add variant that doesn't belong to product
aggregate.add_variant(wrong_variant)  # ❌ Raises ValueError
```

## Usage Examples

### Creating Domain Objects from API

```python
from app.domain.factories import ProductFactory, VariantFactory

# From StockX API response (via mapper)
api_data = await stockx_service.get_product("DO6716-700")
product = ProductFactory.from_stockx_api(api_data)

# Access with type safety
print(product.product_id)  # ProductId value object
print(product.style_id)    # StyleId value object
print(product.retail_price)  # Money value object or None
```

### Using Business Logic

```python
from decimal import Decimal
from app.domain.value_objects import Money

# Update price with validation
new_price = Money(amount=Decimal("199.99"), currency_code="USD")
product.update_price(new_price)  # Validates and updates timestamp

# Check product state
if product.is_released():
    days = product.days_since_release()
    print(f"Released {days} days ago")
```

### Working with Aggregates

```python
from app.domain.aggregates import ProductAggregate

# Create aggregate
aggregate = ProductAggregate(product, variants)

# Find variant by size
size_10 = aggregate.find_variant_by_value("10")

# Get market insights
lowest_ask = aggregate.get_lowest_ask_across_variants()
print(f"Cheapest available: {lowest_ask}")

# Check for stale data
stale_variants = aggregate.get_variants_with_stale_market_data(3600)
if stale_variants:
    print(f"{len(stale_variants)} variants need price refresh")
```

### Managing Listings

```python
from app.domain.listing import Listing
from app.domain.value_objects import ListingStatus

# Create listing from API
listing = ListingFactory.from_stockx_api(api_data)

# Business operations
if listing.is_modifiable():
    new_price = Money(amount=Decimal("189.99"), currency_code="USD")
    listing.update_price(new_price)

# State transitions
listing.activate()  # PENDING → ACTIVE
listing.mark_as_sold()  # ACTIVE → SOLD

# Cannot modify sold listings
listing.update_price(new_price)  # ❌ Raises ValueError
```

### Batch Operations with Listing Aggregate

```python
from app.domain.aggregates import ListingAggregate

# Group listings by variant
aggregate = ListingAggregate(variant_id, listings)

# Batch operations
active_count = len(aggregate.get_active_listings())
total_qty = aggregate.total_quantity()

# Update all prices at once
new_price = Money(amount=Decimal("175.00"), currency_code="USD")
updated_count = aggregate.update_all_prices(new_price)
print(f"Updated {updated_count} listings")

# Cancel all
cancelled = aggregate.cancel_all_active()
```

## Persistence

### Saving to Database

```python
# Convert to dict for database
db_data = product.to_dict()
await product_repository.create(db_data)

# Load from database
db_record = await product_repository.get_by_id(product_id)
product = ProductFactory.from_database(db_record)
```

### Safety Features

1. **Explicit serialization**: Only specified fields are serialized
2. **No circular references**: Aggregates use IDs, not references
3. **Immutable value objects**: Cannot be accidentally modified
4. **Validation on construction**: Invalid data is rejected immediately

## Design Patterns Used

- **Value Object Pattern**: Money, IDs, enumerations
- **Entity Pattern**: Product, Variant, Listing
- **Aggregate Pattern**: ProductAggregate, ListingAggregate
- **Factory Pattern**: Creating complex objects
- **Domain Event Pattern**: Ready for event sourcing (future enhancement)

## Testing

Domain objects are easy to test because they:
- Have no external dependencies
- Use pure business logic
- Validate all inputs
- Are deterministic

```python
# Unit test example
def test_listing_cannot_update_price_when_sold():
    listing = create_test_listing()
    listing.mark_as_sold()

    with pytest.raises(ValueError, match="sold listing"):
        listing.update_price(Money(amount=Decimal("100"), currency_code="USD"))
```

## Migration from Current Models

The existing MongoDB models (`app/models/`) can coexist with domain models:

1. **API Layer**: Uses domain models for business logic
2. **Persistence Layer**: Converts domain models ↔ MongoDB documents
3. **Service Layer**: Operates on domain models

```python
# Service method example
async def update_product_price(product_id: str, new_price: Decimal):
    # Load from database
    db_record = await product_repo.get_by_id(product_id)

    # Create domain object
    product = ProductFactory.from_database(db_record)

    # Apply business logic
    money = Money(amount=new_price, currency_code="USD")
    product.update_price(money)  # Validates, updates timestamp

    # Save back
    await product_repo.update(product_id, product.to_dict())
```

## Future Enhancements

- **Domain Events**: Publish events when entities change state
- **Specifications**: Complex business rules as specifications
- **Repository Interfaces**: Domain-defined repository contracts
- **Validation Rules**: More complex cross-entity validations
