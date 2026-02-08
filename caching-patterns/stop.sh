#!/bin/bash

# Stop all caching pattern services

echo "Stopping all caching pattern services..."

if [ -f .pids ]; then
    PIDS=$(cat .pids)
    for PID in $PIDS; do
        if ps -p $PID > /dev/null; then
            kill $PID
            echo "✓ Stopped process $PID"
        fi
    done
    rm .pids
    echo "✓ All services stopped"
else
    echo "No running services found (no .pids file)"
    echo "Trying to find and kill uvicorn processes..."
    pkill -f "uvicorn.*cache_aside"
    pkill -f "uvicorn.*read_through"
    pkill -f "uvicorn.*write_through"
    pkill -f "uvicorn.*write_behind"
    pkill -f "uvicorn.*refresh_ahead"
fi

echo ""
echo "To stop Docker services:"
echo "  docker-compose down"
