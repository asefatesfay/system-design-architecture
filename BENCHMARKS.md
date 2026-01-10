# Performance Benchmarks

This directory contains benchmarks for all performance antipatterns to demonstrate the performance difference between bad and good implementations.

## Running Benchmarks

### Run All Benchmarks
```bash
# From project root
./run-benchmarks.sh
```

### Run Individual Benchmarks

```bash
# 01 - Improper Instantiation
cd 01-improper-instantiation/benchmarks
go test -bench=. -benchmem

# 02 - Synchronous I/O
cd 02-synchronous-io/benchmarks
go test -bench=. -benchtime=1s

# 03 - Chatty I/O (requires database)
docker-compose up -d postgres
cd 03-chatty-io/benchmarks
go test -bench=. -benchtime=500ms

# 04 - No Caching (requires database and Redis)
docker-compose up -d postgres redis
cd 04-no-caching/benchmarks
go test -bench=. -benchtime=500ms

# 05 - Busy Database (requires database)
docker-compose up -d postgres
cd 05-busy-database/benchmarks
go test -bench=. -benchtime=500ms

# 06 - Retry Storm
cd 06-retry-storm/benchmarks
go test -bench=. -benchtime=1s
```

## Benchmark Options

- `-bench=.` - Run all benchmarks
- `-bench=BenchmarkBad` - Run only "bad" benchmarks
- `-bench=BenchmarkGood` - Run only "good" benchmarks
- `-benchmem` - Show memory allocations
- `-benchtime=5s` - Run for 5 seconds
- `-count=3` - Run 3 times for statistical significance
- `-cpuprofile=cpu.out` - Generate CPU profile

## Example: Compare Bad vs Good

```bash
cd 01-improper-instantiation/benchmarks
go test -bench='Bad|Good' -benchmem -benchtime=2s

# Output shows:
# BenchmarkBadDBConnection    - slower, more allocations
# BenchmarkGoodDBConnection   - faster, fewer allocations
```

## Benchmark Results Interpretation

```
BenchmarkSynchronousIO-12      1    305119500 ns/op
BenchmarkAsynchronousIO-12     2    101476042 ns/op
```

- `-12`: Number of CPU cores used
- `1`, `2`: Number of iterations
- `305119500 ns/op`: Nanoseconds per operation (lower is better)
- Async is ~3x faster (305ms vs 101ms)

## Expected Performance Improvements

| Antipattern | Bad | Good | Improvement |
|-------------|-----|------|-------------|
| **Improper Instantiation** | Creates new objects | Reuses pooled objects | **10-100x faster** |
| **Synchronous I/O** | Sequential blocking calls | Concurrent goroutines | **3-5x faster** |
| **Chatty I/O (N+1)** | N+1 queries (101 queries) | Single JOIN (1 query) | **100x faster** |
| **No Caching** | Always hits database | Redis cache hits | **50-100x faster** |
| **Busy Database** | Heavy DB aggregations | App-level processing | **2-5x faster** |
| **Retry Storm** | Aggressive retries | Circuit breaker + backoff | **Prevents cascade failures** |

## Memory Benchmarks

Add `-benchmem` to see allocations:

```bash
go test -bench=. -benchmem

# Example output:
# BenchmarkBad-12    10000    150000 ns/op    5000 B/op    50 allocs/op
# BenchmarkGood-12   50000     30000 ns/op     500 B/op     5 allocs/op
```

- **B/op**: Bytes allocated per operation
- **allocs/op**: Number of allocations per operation

## Statistical Analysis

For more accurate results, run multiple times:

```bash
go test -bench=. -benchtime=3s -count=5 | tee results.txt

# Use benchstat for analysis
go install golang.org/x/perf/cmd/benchstat@latest
benchstat results.txt
```

## Tips

1. **Warm up**: First run is often slower (JIT, caching, etc.)
2. **Consistency**: Close other applications for accurate results
3. **Database tests**: Ensure Docker services are running
4. **Network tests**: Results vary based on network conditions
5. **Skip slow tests**: Use `-short` flag for quick validation

## Troubleshooting

### Database connection failed
```bash
# Start required services
docker-compose up -d postgres redis

# Wait for services to be ready
sleep 5
```

### Tests skipped
Some benchmarks skip if infrastructure isn't available. This is normal.

### Inconsistent results
Run with `-count=5` and use `benchstat` for statistical analysis.
