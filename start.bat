@echo off
echo Starting FastAPI application with Uvicorn...
echo Note: Gunicorn is not supported on Windows. Using Uvicorn with multiple workers instead.
echo.

if not exist venv (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    exit /b 1
)

call venv\Scripts\activate.bat
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
