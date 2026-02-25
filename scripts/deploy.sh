#!/bin/bash
# Production deployment script

set -e  # Exit on error

echo "================================"
echo "Crawler API Production Deployment"
echo "================================"

# Color output
GREEN='\033[0.32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose not installed${NC}"
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: .env.production file not found${NC}"
    echo "Please copy from .env.example and configure production environment variables"
    exit 1
fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Build new images
echo "Building Docker images..."
docker-compose build --no-cache

# Run database migrations
echo "Running database migrations..."
docker-compose run --rm backend alembic upgrade head

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Health check
echo "Running health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    echo ""
    echo "Service URLs:"
    echo "  - API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Flower (Celery monitoring): http://localhost:5555"
    echo ""
    echo "View logs:"
    echo "  docker-compose logs -f"
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "View logs:"
    echo "  docker-compose logs"
    exit 1
fi
