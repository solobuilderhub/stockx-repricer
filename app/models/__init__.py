# Data models for MongoDB documents
from app.models.product import Product
from app.models.variant import Variant

# Rebuild Variant model after Product is fully defined
# This is required because Variant has a Link to Product
Variant.model_rebuild()

__all__ = ["Product", "Variant"]
