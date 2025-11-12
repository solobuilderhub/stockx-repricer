"""Dependency injection for API routes."""
from app.repositories.product import product_repository



def get_product_repository():
    """Dependency for product repository."""
    return product_repository
