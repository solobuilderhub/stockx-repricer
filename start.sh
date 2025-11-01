#!/bin/bash

echo "Starting FastAPI application with Gunicorn..."
echo ""

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run ./setup.sh first."
    exit 1
fi

source venv/bin/activate
gunicorn app.main:app -c gunicorn.conf.py
