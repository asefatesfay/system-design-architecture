# Busy Database Antipattern

## 🔴 The Problem

Pushing too much work to the database layer including business logic, complex computations, and data aggregation. The database becomes the bottleneck. This leads to:
- Database CPU/memory exhaustion
- Reduced scalability (can't horizontally scale databases easily)
- Slow queries blocking other operations
- Difficult to maintain stored procedures

## Common Examples

1. **Complex business logic in stored procedures** - Business rules in SQL
2. **Heavy aggregations** - Complex GROUP BY, window functions on large datasets
3. **String manipulation** - Regex, parsing, formatting in SQL
4. **Serialization** - JSON/XML processing in database
5. **Loops and cursors** - Iterative processing in stored procedures

## 📊 Impact

- **Database CPU**: 80-100% utilization
- **Query performance**: 10-100x slower
- **Scalability**: Database becomes single point of failure
- **Maintainability**: Business logic scattered across app and DB

## 🏃 Running the Examples

### Bad Example (Busy Database)
```bash
cd bad
go run main.go
```

### Good Example (Application-Layer Processing)
```bash
cd good
go run main.go
```

### Load Test
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Test endpoints
curl http://localhost:8088/reports/sales  # Bad: heavy DB work
curl http://localhost:8089/reports/sales  # Good: app processing
```

## 🎯 Key Takeaways

1. **Keep DB simple**: Use database for storage and simple queries
2. **Process in application**: Business logic belongs in application code
3. **Read replicas**: Separate read/write workloads
4. **Aggregate in app**: Pull data, aggregate in memory
5. **Use right tool**: Consider analytical databases for complex analytics

## 📚 Related Patterns

- CQRS (Command Query Responsibility Segregation)
- Read Replicas
- Data Warehouse for Analytics
- Materialized Views
