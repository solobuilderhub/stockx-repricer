"""Custom exception classes for the application."""


class StockXRepricerException(Exception):
    """Base exception for all application-specific exceptions."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(StockXRepricerException):
    """Exception raised for database-related errors."""
    pass


class APIClientException(StockXRepricerException):
    """Exception raised for external API client errors."""
    pass


class PricingCalculationException(StockXRepricerException):
    """Exception raised during pricing calculation."""
    pass


class DataNotFoundException(StockXRepricerException):
    """Exception raised when requested data is not found."""
    pass


class ValidationException(StockXRepricerException):
    """Exception raised for data validation errors."""
    pass


class ConfigurationException(StockXRepricerException):
    """Exception raised for configuration-related errors."""
    pass
