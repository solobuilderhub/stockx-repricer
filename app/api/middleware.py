"""Middleware for error handling and logging."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time

from app.core.exceptions import StockXRepricerException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def exception_handler_middleware(request: Request, call_next):
    """Global exception handling middleware."""
    try:
        response = await call_next(request)
        return response

    except StockXRepricerException as e:
        logger.error(f"Application error: {e.message}", extra=e.details)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": e.message,
                "details": e.details
            }
        )

    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": str(e) if logger.level <= 10 else "An unexpected error occurred"
            }
        )


async def logging_middleware(request: Request, call_next):
    """Middleware for logging requests and responses."""
    start_time = time.time()

    # Log request
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None
        }
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {duration:.3f}s",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration
        }
    )

    return response


def setup_exception_handlers(app):
    """Setup exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "details": exc.errors()
            }
        )

    @app.exception_handler(StockXRepricerException)
    async def app_exception_handler(request: Request, exc: StockXRepricerException):
        """Handle custom application exceptions."""
        logger.error(f"Application error: {exc.message}", extra=exc.details)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": exc.message,
                "details": exc.details
            }
        )
