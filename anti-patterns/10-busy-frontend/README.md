# Busy Frontend Antipattern

## 🔴 The Problem

Performing heavy computation, business logic, or data processing in the client/frontend layer instead of the backend. This leads to:
- Poor performance on low-end devices
- Excessive battery drain on mobile
- Inconsistent behavior across clients
- Security vulnerabilities
- Difficult to update business logic

## Common Examples

### 1. **Complex Calculations in Frontend**

❌ **Bad:**
```javascript
// React component doing heavy computation
function ProductList({ products }) {
  // Computing in browser for every render!
  const sortedProducts = products.sort((a, b) => {
    const scoreA = calculateComplexScore(a);  // Expensive!
    const scoreB = calculateComplexScore(b);
    return scoreB - scoreA;
  });
  
  const filteredProducts = sortedProducts.filter(p => {
    return complexFilterLogic(p);  // More computation!
  });
  
  return <div>{filteredProducts.map(renderProduct)}</div>;
}
```

✅ **Good:**
```javascript
// Backend does heavy lifting
function ProductList() {
  const { data: products } = useQuery('/api/products?sort=relevance&filter=available');
  return <div>{products.map(renderProduct)}</div>;
}
```

### 2. **Business Logic in Client**

❌ **Bad:**
```javascript
// Pricing logic in frontend - BAD!
function calculatePrice(product, user) {
  let price = product.basePrice;
  
  // Complex business rules in client
  if (user.isPremium) {
    price *= 0.9;
  }
  if (product.category === 'electronics' && isHolidaySeason()) {
    price *= 0.85;
  }
  if (user.loyaltyPoints > 1000) {
    price -= 50;
  }
  
  return price;
}
```

✅ **Good:**
```javascript
// Backend calculates price with all business rules
const { data: pricing } = useQuery(`/api/products/${id}/price`);
```

### 3. **Data Aggregation in Client**

❌ **Bad:**
```javascript
// Aggregating in browser
function Dashboard() {
  const [orders, setOrders] = useState([]);
  
  useEffect(() => {
    // Fetch ALL orders (could be thousands)
    fetch('/api/orders').then(res => res.json()).then(setOrders);
  }, []);
  
  // Heavy computation in client
  const totalRevenue = orders.reduce((sum, o) => sum + o.total, 0);
  const avgOrderValue = totalRevenue / orders.length;
  const ordersByMonth = groupByMonth(orders);  // Complex!
  
  return <Dashboard stats={{ totalRevenue, avgOrderValue, ordersByMonth }} />;
}
```

✅ **Good:**
```javascript
// Backend pre-computes analytics
function Dashboard() {
  const { data: stats } = useQuery('/api/analytics/dashboard');
  return <Dashboard stats={stats} />;
}
```

### 4. **Validation Only in Frontend**

❌ **Bad:**
```javascript
// Only client-side validation - can be bypassed!
function SignupForm() {
  const handleSubmit = (data) => {
    if (!isValidEmail(data.email)) return;
    if (data.password.length < 8) return;
    
    // Direct submission without backend validation
    api.post('/api/users', data);
  };
}
```

✅ **Good:**
```javascript
// Client validation for UX, backend for security
function SignupForm() {
  const handleSubmit = async (data) => {
    // Frontend validation for immediate feedback
    if (!isValidEmail(data.email)) {
      setError('Invalid email');
      return;
    }
    
    try {
      // Backend validates again (authoritative)
      await api.post('/api/users', data);
    } catch (err) {
      // Server-side validation errors
      setError(err.message);
    }
  };
}
```

## 📊 Impact

- **Performance**: Slow on low-end devices (2-10x slower)
- **Battery**: High CPU usage drains battery
- **Inconsistency**: Different results on different clients
- **Security**: Business logic can be inspected/bypassed
- **Maintainability**: Need to update all clients for logic changes

## ✅ Solutions

### 1. **Backend for Business Logic**

```go
// Backend calculates prices with all business rules
func (s *PricingService) CalculatePrice(ctx context.Context, productID int, userID int) (*Price, error) {
    product, _ := s.productRepo.Get(productID)
    user, _ := s.userRepo.Get(userID)
    
    price := product.BasePrice
    
    // All business logic in one place
    if user.IsPremium {
        price *= 0.9
    }
    
    if s.isHolidaySeason() {
        price *= 0.85
    }
    
    // Apply discounts, taxes, etc.
    return &Price{
        Original: product.BasePrice,
        Final:    price,
    }, nil
}
```

### 2. **Server-Side Rendering (SSR)**

```javascript
// Next.js - compute on server
export async function getServerSideProps(context) {
  // Heavy computation on server
  const products = await db.query('SELECT * FROM products');
  const processed = complexProcessing(products);
  
  return {
    props: { products: processed }
  };
}

// Component just displays
export default function ProductPage({ products }) {
  return <ProductList products={products} />;
}
```

### 3. **API Aggregation Endpoints**

```go
// Backend endpoint returns pre-aggregated data
func (h *Handler) GetDashboardStats(w http.ResponseWriter, r *http.Request) {
    stats := &DashboardStats{
        TotalRevenue:   h.analytics.CalculateTotalRevenue(),
        AvgOrderValue:  h.analytics.CalculateAvgOrder(),
        OrdersByMonth:  h.analytics.GroupOrdersByMonth(),
        TopProducts:    h.analytics.GetTopProducts(10),
    }
    
    json.NewEncoder(w).Encode(stats)
}
```

### 4. **Pagination & Server-Side Filtering**

```go
// Backend handles filtering, sorting, pagination
func (h *Handler) GetProducts(w http.ResponseWriter, r *http.Request) {
    params := &ProductQuery{
        Category: r.URL.Query().Get("category"),
        Sort:     r.URL.Query().Get("sort"),
        Page:     parseInt(r.URL.Query().Get("page"), 1),
        PageSize: parseInt(r.URL.Query().Get("pageSize"), 20),
    }
    
    // Backend does the heavy lifting
    result, err := h.productService.Search(params)
    if err != nil {
        http.Error(w, err.Error(), 500)
        return
    }
    
    json.NewEncoder(w).Encode(result)
}
```

### 5. **WebWorkers for Unavoidable Client Work**

```javascript
// If must do heavy work in client, use Web Workers
const worker = new Worker('processor.worker.js');

worker.postMessage({ data: largeDataset });

worker.onmessage = (e) => {
  const processedData = e.data;
  updateUI(processedData);
};

// processor.worker.js - runs in background thread
self.onmessage = (e) => {
  const result = heavyComputation(e.data);
  self.postMessage(result);
};
```

### 6. **Edge Computing (Cloudflare Workers, Lambda@Edge)**

```javascript
// Cloudflare Worker - compute close to user
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const products = await fetchProducts();
  
  // Process on edge, close to user
  const filtered = products.filter(p => p.inStock);
  const sorted = filtered.sort((a, b) => b.rating - a.rating);
  
  return new Response(JSON.stringify(sorted), {
    headers: { 'Content-Type': 'application/json' }
  });
}
```

## 🎯 Best Practices

### 1. **Thin Client, Fat Server**
- Client handles UI/UX only
- Server handles business logic
- Edge layer for personalization

### 2. **Smart API Design**
```
❌ Bad:
GET /api/products        → Returns all products
GET /api/categories      → Client cross-references
GET /api/reviews         → Client aggregates

✅ Good:
GET /api/products/featured  → Pre-computed, filtered, with reviews
```

### 3. **Progressive Enhancement**
```javascript
// Basic functionality without JS
<form action="/api/search" method="POST">
  <input name="query" />
  <button type="submit">Search</button>
</form>

// Enhanced with JavaScript
<SearchComponent 
  onSearch={query => api.search(query)}
  fallbackAction="/api/search"
/>
```

### 4. **Use Backend for Authorization**
```javascript
// ❌ Never trust client
if (user.isAdmin) {  // Can be manipulated!
  showDeleteButton();
}

// ✅ Backend enforces
fetch('/api/admin/delete', {
  method: 'DELETE',
  // Backend checks auth
})
```

## 📊 What Goes Where?

| Responsibility | Frontend | Backend |
|----------------|----------|---------|
| **UI rendering** | ✅ | SSR option |
| **Form validation** | ✅ (UX) | ✅ (Security) |
| **Business logic** | ❌ | ✅ |
| **Calculations** | Simple only | ✅ Complex |
| **Data filtering** | Client-side sort | ✅ Large datasets |
| **Authorization** | UI hints only | ✅ Enforcement |
| **Data aggregation** | ❌ | ✅ |
| **Pricing** | ❌ | ✅ |

## 🎯 Key Takeaways

1. **Backend for business logic**: Keep critical logic server-side
2. **Frontend for presentation**: UI/UX only
3. **Server-side rendering**: For SEO and performance
4. **Validate twice**: Client for UX, server for security
5. **Pre-aggregate data**: Don't make client do heavy work
6. **Consider mobile**: Low-end devices have limited power
7. **Edge computing**: For personalization close to users

## 📚 Related Patterns

- Thin Client Architecture
- Backend for Frontend (BFF)
- Server-Side Rendering (SSR)
- API Gateway Pattern
- Edge Computing

## 🛠️ Tools

- **SSR Frameworks**: Next.js, Nuxt.js, Remix
- **Edge**: Cloudflare Workers, Vercel Edge, Lambda@Edge
- **State Management**: React Query, SWR (minimize client logic)
- **Validation**: Zod, Yup (share schemas between client/server)
