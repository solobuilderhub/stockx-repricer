"""Dependency injection for API routes."""
from app.services.pricing_service import pricing_service
from app.services.data_collector import data_collector
from app.repositories.pricing_repository import PricingRepository, ProductRepository


def get_pricing_service():
    """Dependency for pricing service."""
    return pricing_service


def get_data_collector():
    """Dependency for data collection service."""
    return data_collector


def get_pricing_repository():
    """Dependency for pricing repository."""
    return PricingRepository()


def get_product_repository():
    """Dependency for product repository."""
    return ProductRepository()
