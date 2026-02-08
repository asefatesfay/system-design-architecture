#!/bin/bash

# Start all caching pattern services

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         Starting Caching Patterns Services                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Check if Docker services are running
echo ""
echo "Checking Docker services..."
if ! docker ps | grep -q "caching_postgres\|caching_redis"; then
    echo "Starting Docker services..."
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 5
else
    echo "✓ Docker services already running"
fi

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry not found. Please install poetry first."
    echo "Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo ""
    echo "Installing dependencies..."
    poetry install
fi

echo ""
echo "Starting FastAPI applications..."
echo ""

# Start each service in background
poetry run uvicorn cache_aside.main:app --host 0.0.0.0 --port 8001 > logs/cache_aside.log 2>&1 &
CACHE_ASIDE_PID=$!
echo "✓ Cache-Aside Pattern     → http://localhost:8001 (PID: $CACHE_ASIDE_PID)"

poetry run uvicorn read_through.main:app --host 0.0.0.0 --port 8002 > logs/read_through.log 2>&1 &
READ_THROUGH_PID=$!
echo "✓ Read-Through Pattern    → http://localhost:8002 (PID: $READ_THROUGH_PID)"

poetry run uvicorn write_through.main:app --host 0.0.0.0 --port 8003 > logs/write_through.log 2>&1 &
WRITE_THROUGH_PID=$!
echo "✓ Write-Through Pattern   → http://localhost:8003 (PID: $WRITE_THROUGH_PID)"

poetry run uvicorn write_behind.main:app --host 0.0.0.0 --port 8004 > logs/write_behind.log 2>&1 &
WRITE_BEHIND_PID=$!
echo "✓ Write-Behind Pattern    → http://localhost:8004 (PID: $WRITE_BEHIND_PID)"

poetry run uvicorn refresh_ahead.main:app --host 0.0.0.0 --port 8005 > logs/refresh_ahead.log 2>&1 &
REFRESH_AHEAD_PID=$!
echo "✓ Refresh-Ahead Pattern   → http://localhost:8005 (PID: $REFRESH_AHEAD_PID)"

# Save PIDs to file for stop script
echo "$CACHE_ASIDE_PID $READ_THROUGH_PID $WRITE_THROUGH_PID $WRITE_BEHIND_PID $REFRESH_AHEAD_PID" > .pids

echo ""
echo "Waiting for services to start..."
sleep 3

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 All Services Started!                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "API Documentation:"
echo "  Cache-Aside:    http://localhost:8001/docs"
echo "  Read-Through:   http://localhost:8002/docs"
echo "  Write-Through:  http://localhost:8003/docs"
echo "  Write-Behind:   http://localhost:8004/docs"
echo "  Refresh-Ahead:  http://localhost:8005/docs"
echo ""
echo "Run tests:"
echo "  poetry run python test_patterns.py"
echo ""
echo "View logs:"
echo "  tail -f logs/cache_aside.log"
echo ""
echo "Stop all services:"
echo "  ./stop.sh"
echo ""
