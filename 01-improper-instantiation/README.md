# Improper Instantiation Antipattern

## 🔴 The Problem

Creating expensive objects repeatedly instead of reusing them. This leads to:
- Excessive memory allocation
- Increased garbage collection pressure
- Slower performance due to repeated initialization
- Wasted CPU cycles

## Common Examples

1. **Database connections** - Creating new connections per request
2. **HTTP clients** - Not reusing connection pools
3. **Regex patterns** - Compiling regex on every use
4. **Heavy configuration objects** - Re-parsing config files
5. **Cryptographic objects** - Re-initializing hash functions, ciphers

## 📊 Impact

- **Memory**: 10-100x more allocations
- **CPU**: 5-50x more overhead
- **Latency**: 2-10x slower response times
- **Throughput**: 50-90% reduction under load

## 🏃 Running the Examples

### Bad Example (Antipattern)
```bash
cd bad
go run main.go
```

### Good Example (Proper Pattern)
```bash
cd good
go run main.go
```

### Benchmarks
```bash
cd benchmarks
go test -bench=. -benchmem
```

## 🎯 Key Takeaways

1. **Identify expensive operations**: Connection creation, compilation, initialization
2. **Reuse when possible**: Use pools, singletons, package-level variables
3. **Initialize once**: Use `sync.Once` for lazy initialization
4. **Measure impact**: Profile before and after optimization

## 📚 Related Patterns

- Object Pool Pattern
- Singleton Pattern
- Flyweight Pattern
