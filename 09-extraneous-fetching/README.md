# Extraneous Fetching Antipattern

## 🔴 The Problem

Retrieving more data than needed from databases or APIs. Common manifestations:
- Using `SELECT *` instead of specific columns
- Loading entire objects when only IDs are needed
- Fetching full collections when paginated results suffice
- Not using projections/field filters in APIs

This leads to:
- Increased network traffic
- Higher memory usage
- Slower query execution
- Wasted bandwidth and processing

## Common Examples

### 1. **SELECT * Queries**

❌ **Bad:**
```go
// Fetches ALL columns including large text/blob fields
rows, err := db.Query("SELECT * FROM users")
```

✅ **Good:**
```go
// Only fetch what you need
rows, err := db.Query("SELECT id, name, email FROM users")
```

### 2. **Loading Full Objects**

❌ **Bad:**
```go
// Need just IDs but load entire product objects
products, err := productRepo.FindAll()  // Returns full objects
var productIDs []int
for _, p := range products {
    productIDs = append(productIDs, p.ID)  // Only using ID!
}
```

✅ **Good:**
```go
// Query just the IDs
productIDs, err := db.Query("SELECT id FROM products")
```

### 3. **No Pagination**

❌ **Bad:**
```go
// Loads all 1,000,000 records into memory
func getAllUsers() ([]User, error) {
    return db.Query("SELECT * FROM users")
}
```

✅ **Good:**
```go
// Paginate results
func getUsers(page, pageSize int) ([]User, error) {
    offset := (page - 1) * pageSize
    return db.Query(
        "SELECT id, name, email FROM users LIMIT $1 OFFSET $2",
        pageSize, offset,
    )
}
```

### 4. **API Over-fetching**

❌ **Bad:**
```go
// GraphQL query fetching everything
query {
  user(id: 1) {
    id
    name
    email
    address {
      street
      city
      state
      zipCode
    }
    orders {
      id
      items {
        product {
          id
          name
          description  # Don't need this
          images       # Don't need this
        }
      }
    }
  }
}
```

✅ **Good:**
```go
// Only fetch what's displayed
query {
  user(id: 1) {
    name
    email
    orders {
      id
    }
  }
}
```

## 📊 Impact

- **Network**: 5-100x more data transferred
- **Memory**: OOM errors with large datasets
- **Database**: Slower queries, more I/O
- **Cost**: Higher bandwidth and storage costs

## ✅ Solutions

### 1. **Use Projections in Queries**

```go
// PostgreSQL
type UserBasic struct {
    ID    int
    Name  string
    Email string
}

func getUsersBasic() ([]UserBasic, error) {
    return db.Query("SELECT id, name, email FROM users")
}

// MongoDB
collection.Find(ctx, bson.M{}, options.Find().SetProjection(bson.M{
    "name":  1,
    "email": 1,
}))
```

### 2. **Implement Pagination**

```go
type PaginatedResult struct {
    Data       []User `json:"data"`
    Page       int    `json:"page"`
    PageSize   int    `json:"page_size"`
    TotalCount int    `json:"total_count"`
    TotalPages int    `json:"total_pages"`
}

func getUsersPaginated(page, pageSize int) (*PaginatedResult, error) {
    // Count total
    var totalCount int
    db.QueryRow("SELECT COUNT(*) FROM users").Scan(&totalCount)
    
    // Fetch page
    offset := (page - 1) * pageSize
    rows, err := db.Query(
        "SELECT id, name, email FROM users LIMIT $1 OFFSET $2",
        pageSize, offset,
    )
    
    // ... process rows
    
    return &PaginatedResult{
        Data:       users,
        Page:       page,
        PageSize:   pageSize,
        TotalCount: totalCount,
        TotalPages: (totalCount + pageSize - 1) / pageSize,
    }, nil
}
```

### 3. **Use Lazy Loading**

```go
type User struct {
    ID      int
    Name    string
    orders  []Order  // Not loaded initially
}

// Only load orders when needed
func (u *User) GetOrders() ([]Order, error) {
    if u.orders == nil {
        // Lazy load
        u.orders, err = db.Query("SELECT * FROM orders WHERE user_id = $1", u.ID)
    }
    return u.orders, nil
}
```

### 4. **GraphQL Field Resolvers**

```go
// Only resolve requested fields
type Resolver struct{}

func (r *Resolver) User(ctx context.Context, args struct{ ID int }) (*User, error) {
    // Check which fields are requested
    fields := graphql.CollectFields(ctx)
    
    if onlyBasicFields(fields) {
        // Light query
        return db.QueryRow("SELECT id, name FROM users WHERE id = $1", args.ID)
    }
    
    // Full query if needed
    return db.QueryRow("SELECT * FROM users WHERE id = $1", args.ID)
}
```

### 5. **Cursor-Based Pagination (Efficient)**

```go
// More efficient than OFFSET for large datasets
func getUsersWithCursor(cursor string, limit int) ([]User, string, error) {
    query := `
        SELECT id, name, email 
        FROM users 
        WHERE id > $1 
        ORDER BY id 
        LIMIT $2
    `
    
    var lastID int
    if cursor != "" {
        lastID, _ = strconv.Atoi(cursor)
    }
    
    rows, err := db.Query(query, lastID, limit)
    // ... process rows
    
    newCursor := strconv.Itoa(users[len(users)-1].ID)
    return users, newCursor, nil
}
```

### 6. **Streaming Large Results**

```go
func exportUsersStream(w io.Writer) error {
    rows, err := db.Query("SELECT id, name, email FROM users")
    if err != nil {
        return err
    }
    defer rows.Close()
    
    encoder := json.NewEncoder(w)
    
    // Stream results without loading all into memory
    for rows.Next() {
        var user User
        rows.Scan(&user.ID, &user.Name, &user.Email)
        encoder.Encode(user)  // Stream one at a time
    }
    
    return nil
}
```

## 🎯 Best Practices

### 1. **DTOs (Data Transfer Objects)**

```go
// Full domain object
type User struct {
    ID              int
    Name            string
    Email           string
    PasswordHash    string  // Sensitive
    Address         Address
    PaymentMethods  []PaymentMethod
    LoginHistory    []Login
    Preferences     json.RawMessage  // Large JSON
}

// Lightweight DTOs for different use cases
type UserListDTO struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

type UserDetailDTO struct {
    ID      int     `json:"id"`
    Name    string  `json:"name"`
    Email   string  `json:"email"`
    Address Address `json:"address"`
}
```

### 2. **Index-Only Scans**

```sql
-- Create covering index
CREATE INDEX idx_users_list ON users(id, name, email);

-- This query can use index-only scan (faster)
SELECT id, name, email FROM users WHERE email LIKE '%@example.com';
```

### 3. **Field Masks (gRPC/REST)**

```go
// REST API with field selection
GET /users/123?fields=id,name,email

// Implementation
func getUserWithFields(id int, fields []string) (map[string]interface{}, error) {
    query := fmt.Sprintf("SELECT %s FROM users WHERE id = $1", 
        strings.Join(fields, ", "))
    // ... execute query
}
```

### 4. **Avoid N+1 in ORMs**

```go
// ❌ Bad: N+1 query problem
users := db.Find(&User{})
for _, user := range users {
    user.Orders  // Triggers separate query for each user!
}

// ✅ Good: Eager loading
users := db.Preload("Orders").Find(&User{})
```

## 📊 Monitoring

Track these metrics:
- **Query result size** (rows, bytes)
- **Network bandwidth** (MB/s)
- **Query execution time**
- **Memory usage** per request
- **SELECT * queries** (audit logs)

## 🛠️ Tools

- **Database**: `EXPLAIN ANALYZE` to see data size
- **APM**: New Relic, Datadog for query analysis
- **Linters**: Detect `SELECT *` in code reviews
- **GraphQL**: Built-in field selection
- **ORMs**: Projection support (GORM, sqlx)

## 🎯 Key Takeaways

1. **Only fetch what you need**: Be explicit about columns
2. **Paginate everything**: Never load unbounded datasets
3. **Use projections**: DTO pattern for different contexts
4. **Lazy load**: Don't fetch related data unless needed
5. **Monitor query size**: Alert on large result sets
6. **Use cursors for scale**: More efficient than OFFSET

## 📚 Related Patterns

- DTO Pattern
- Lazy Loading
- Eager Loading
- GraphQL (field-level fetching)
- CQRS (separate read models)
