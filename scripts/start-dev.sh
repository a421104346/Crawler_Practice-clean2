#!/bin/bash
# Development environment startup script

set -e

echo "================================"
echo "Starting development environment"
echo "================================"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
cd backend
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python -c "import asyncio; from database import init_db; asyncio.run(init_db())"

# Start services
echo "Starting FastAPI service..."
echo ""
echo "Access URLs:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
