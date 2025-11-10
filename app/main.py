from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db.mongodb import db
from app.models.product import Product
from app.models.historical import HistoricalPrice
from app.models.variant import Variant
from app.api.routes.stockx import stockx_routes, auth as stockx_auth, external_market_data_routes
from app.api.routes.product import product_routes
from app.api.middleware import logging_middleware, setup_exception_handlers

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Application starting up...")
    try:
        await db.connect_to_database()
        await db.init_beanie_models([Product, HistoricalPrice, Variant])
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Application shutting down...")
    await db.close_database_connection()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="FastAPI application for StockX price optimization with clean architecture",
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.middleware("http")(logging_middleware)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(stockx_auth.router)
app.include_router(stockx_routes)
app.include_router(external_market_data_routes)
app.include_router(product_routes)




@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to StockX Repricer API",
        "status": "online",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "stockx-repricer",
            "version": settings.app_version
        }
    )
