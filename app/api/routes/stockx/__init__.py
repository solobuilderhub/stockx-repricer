"""StockX API routes."""
from app.api.routes.stockx.stockx_routes import router as stockx_routes
from app.api.routes.stockx.external_market_data_routes import router as external_market_data_routes

__all__ = ["stockx_routes", "external_market_data_routes"]
