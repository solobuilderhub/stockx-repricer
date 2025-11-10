"""Application configuration and settings management."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application Settings
    app_name: str = "StockX Repricer API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000

    # MongoDB Settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "stockx_repricer"
    mongodb_min_pool_size: int = 10
    mongodb_max_pool_size: int = 50

    # StockX API Settings (customize based on actual API)
    stockx_api_url: Optional[str] = None
    stockx_api_key: Optional[str] = None
    stockx_client_id: Optional[str] = None
    stockx_client_secret: Optional[str] = None
    stockx_auth_url: Optional[str] = None
    stockx_grant_type: Optional[str] = None
    stockx_audience: Optional[str] = None
    stockx_refresh_token: Optional[str] = None
    stockx_auth_content_type: Optional[str] = None

    # External StockX Market Data API Settings
    external_stockx_api_token: Optional[str] = None


    # Pricing Configuration
    default_margin_percentage: float = 10.0
    min_price_threshold: float = 0.0
    max_price_threshold: float = 10000.0

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
