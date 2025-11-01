# StockX Repricer - FastAPI Project

A FastAPI application for StockX price optimization with clean architecture, MongoDB async support, and production-ready deployment.

## Features

- Clean Architecture with clear separation of concerns
- Async MongoDB integration with Beanie ODM
- Historical price data collection from external APIs
- Optimal price calculation based on historical data
- RESTful API with comprehensive documentation
- Error handling and logging middleware
- Environment-based configuration
- Production-ready with Gunicorn/Uvicorn

## Project Structure

```
stockx-repricer/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── core/                        # Core configuration and utilities
│   │   ├── config.py               # Settings management
│   │   ├── exceptions.py           # Custom exceptions
│   │   └── logging.py              # Logging configuration
│   ├── db/                         # Database layer
│   │   └── mongodb.py              # MongoDB connection management
│   ├── models/                     # Beanie document models
│   │   ├── product.py              # Product model
│   │   └── historical.py           # Historical price model
│   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── product.py
│   │   └── pricing.py
│   ├── repositories/               # Data access layer
│   │   ├── base.py                 # Base repository with CRUD
│   │   └── pricing_repository.py  # Pricing-specific queries
│   ├── services/                   # Business logic layer
│   │   ├── api_client.py           # External API client
│   │   ├── pricing_service.py      # Price calculation
│   │   └── data_collector.py       # Data collection service
│   └── api/                        # API layer
│       ├── dependencies.py         # Dependency injection
│       ├── middleware.py           # Error handling & logging
│       └── routes/                 # API route modules
│           ├── pricing.py          # Pricing endpoints
│           └── data.py             # Data collection endpoints
├── .env.example                    # Environment variables template
├── .gitignore
├── gunicorn.conf.py               # Gunicorn configuration
├── requirements.txt               # Python dependencies
├── setup.bat/.sh                  # Setup scripts
├── start.bat/.sh                  # Start scripts
└── README.md
```

## Architecture Layers

### 1. Core Layer (`app/core/`)
- Configuration management with environment variables
- Custom exception classes
- Logging setup and utilities

### 2. Database Layer (`app/db/`)
- Async MongoDB client with connection pooling
- Beanie ODM initialization
- Database lifecycle management

### 3. Models Layer (`app/models/`)
- Beanie document models for MongoDB
- Database schema definitions with indexes

### 4. Schemas Layer (`app/schemas/`)
- Pydantic models for API validation
- Request and response schemas

### 5. Repository Layer (`app/repositories/`)
- Data access abstraction
- Base CRUD operations
- Specialized query methods

### 6. Service Layer (`app/services/`)
- Business logic implementation
- External API integration
- Price calculation algorithms
- Data collection orchestration

### 7. API Layer (`app/api/`)
- RESTful endpoints
- Dependency injection
- Middleware (error handling, logging)
- Route modules organized by domain

## Setup Instructions

### Prerequisites

- Python 3.9+
- MongoDB 4.4+ (running locally or accessible via connection string)

### Quick Start

#### Windows

**Note**: Gunicorn doesn't support Windows. The Windows script uses Uvicorn with multiple workers instead.

1. Run the setup script to create virtual environment and install dependencies:
   ```bash
   setup.bat
   ```

2. Copy `.env.example` to `.env` and configure your environment variables:
   ```bash
   copy .env.example .env
   ```

3. Edit `.env` file with your MongoDB connection string and API credentials

4. Start the application:
   ```bash
   start.bat
   ```

   This will start Uvicorn with 4 workers on port 8000.

#### Linux/Mac

1. Make scripts executable:
   ```bash
   chmod +x setup.sh start.sh
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

3. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` file with your configuration

5. Start the application:
   ```bash
   ./start.sh
   ```

## Manual Setup

If you prefer to set up manually:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the application
# Windows:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
# Linux/Mac:
gunicorn app.main:app -c gunicorn.conf.py
```

## Configuration

### Production Server Settings

**Linux/Mac (Gunicorn)**: The application is configured in [gunicorn.conf.py](gunicorn.conf.py):
- **Workers**: CPU cores * 2 + 1
- **Worker Class**: uvicorn.workers.UvicornWorker
- **Bind Address**: 0.0.0.0:8000
- **Timeout**: 30 seconds
- **Max Requests**: 1000 (with 50 jitter)

**Windows (Uvicorn)**: Configured via command-line arguments in [start.bat](start.bat):
- **Workers**: 4
- **Host**: 0.0.0.0
- **Port**: 8000
- **Log Level**: info

### API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## Accessing the Application

Once started, the application will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Development

To run in development mode with auto-reload:

```bash
# Activate virtual environment first
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Considerations

- **Linux/Mac**: Adjust worker count in [gunicorn.conf.py](gunicorn.conf.py) based on your server resources
- **Windows**: Adjust worker count in [start.bat](start.bat) or use WSL/Docker for Gunicorn support
- Configure SSL certificates if needed
- Set up a reverse proxy (nginx, traefik) in front of the application server
- Use a process supervisor (systemd, supervisor, or PM2) to manage the application
- Configure proper logging and monitoring

## Important Notes

- **Gunicorn on Windows**: Gunicorn requires Unix-specific modules and doesn't work on native Windows. For Windows development, use Uvicorn directly (which the start.bat script does automatically).
- **Production on Windows**: Consider using Docker, WSL (Windows Subsystem for Linux), or deploying to a Linux server for production environments.
- **Multiple Workers**: Both Gunicorn (Linux/Mac) and Uvicorn (Windows) support multiple worker processes for better performance.
