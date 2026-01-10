#!/bin/bash

# Run all performance benchmarks

echo "======================================"
echo "Performance Antipatterns Benchmarks"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Check if Docker services are needed
echo "Checking Docker services..."
docker-compose ps postgres redis 2>/dev/null | grep -q "Up" || {
    echo "⚠️  Starting Docker services (postgres, redis)..."
    docker-compose up -d postgres redis
    echo "Waiting for services to be ready..."
    sleep 5
}

echo ""
echo "Running benchmarks..."
echo ""

# 01 - Improper Instantiation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "01 - Improper Instantiation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd 01-improper-instantiation/benchmarks
go test -bench=. -benchmem -benchtime=1s | grep -E "Benchmark|PASS|ok"
cd ../..
echo ""

# 02 - Synchronous I/O
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "02 - Synchronous I/O"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd 02-synchronous-io/benchmarks
go test -bench=. -benchtime=500ms | grep -E "Benchmark|PASS|ok"
cd ../..
echo ""

# 03 - Chatty I/O
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "03 - Chatty I/O (N+1 Problem)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd 03-chatty-io/benchmarks
go test -bench=. -benchtime=500ms | grep -E "Benchmark|PASS|ok|SKIP"
cd ../..
echo ""

# 04 - No Caching
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "04 - No Caching"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd 04-no-caching/benchmarks
go test -bench=. -benchtime=500ms | grep -E "Benchmark|PASS|ok|SKIP"
cd ../..
echo ""

# 05 - Busy Database
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "05 - Busy Database"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd 05-busy-database/benchmarks
go test -bench=. -benchtime=500ms | grep -E "Benchmark|PASS|ok|SKIP"
cd ../..
echo ""

# 06 - Retry Storm
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "06 - Retry Storm"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd 06-retry-storm/benchmarks
go test -bench=. -benchtime=500ms | grep -E "Benchmark|PASS|ok"
cd ../..
echo ""

echo "======================================"
echo "✅ All benchmarks completed!"
echo "======================================"
echo ""
echo "📊 To see detailed results with memory stats:"
echo "   cd <antipattern>/benchmarks && go test -bench=. -benchmem"
echo ""
echo "📈 For statistical analysis across multiple runs:"
echo "   go test -bench=. -count=5 | tee results.txt"
echo "   benchstat results.txt"
