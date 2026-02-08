# OpenAPI Usage Guide

This guide shows how to use the OpenAPI specification for the Proximity Service API.

## Quick Start

### View Interactive Documentation

#### Option 1: Swagger UI (Online)
1. Go to [Swagger Editor](https://editor.swagger.io/)
2. File → Import File → Select `openapi.yaml`
3. View interactive documentation with "Try it out" buttons

#### Option 2: Swagger UI (Local)
```bash
# Using Docker
docker run -p 8080:8080 -e SWAGGER_JSON=/openapi.yaml -v $(pwd):/app swaggerapi/swagger-ui

# Open browser
open http://localhost:8080
```

#### Option 3: ReDoc (Beautiful Docs)
```bash
# Using npx
npx @redocly/cli preview-docs openapi.yaml

# Or Docker
docker run -p 8080:80 -e SPEC_URL=openapi.yaml -v $(pwd):/usr/share/nginx/html/openapi.yaml redocly/redoc

# Open browser
open http://localhost:8080
```

---

## Generate Client SDKs

### Python Client
```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o ./clients/python \
  --additional-properties=packageName=proximity_client

# Use the generated client
cd clients/python
pip install -e .
```

**Usage:**
```python
from proximity_client import ApiClient, Configuration, SearchApi

config = Configuration(host="https://api.proximity.example.com/v1")
client = ApiClient(configuration=config)
search_api = SearchApi(client)

# Search nearby places
response = search_api.search_nearby_places(
    latitude=37.7749,
    longitude=-122.4194,
    radius=5000,
    type="restaurant",
    limit=20
)

for place in response.places:
    print(f"{place.name} - {place.distance}m away")
```

### JavaScript/TypeScript Client
```bash
# Generate TypeScript client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-fetch \
  -o ./clients/typescript \
  --additional-properties=npmName=proximity-client

cd clients/typescript
npm install
npm run build
```

**Usage:**
```typescript
import { Configuration, SearchApi } from 'proximity-client';

const config = new Configuration({
  basePath: 'https://api.proximity.example.com/v1'
});

const searchApi = new SearchApi(config);

const response = await searchApi.searchNearbyPlaces({
  latitude: 37.7749,
  longitude: -122.4194,
  radius: 5000,
  type: 'restaurant',
  limit: 20
});

response.places.forEach(place => {
  console.log(`${place.name} - ${place.distance}m away`);
});
```

### Java Client
```bash
# Generate Java client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g java \
  -o ./clients/java \
  --additional-properties=\
groupId=com.example,\
artifactId=proximity-client,\
library=okhttp-gson

cd clients/java
mvn install
```

### Go Client
```bash
# Generate Go client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g go \
  -o ./clients/go \
  --additional-properties=packageName=proximity
```

---

## Generate Server Stubs

### Node.js/Express Server
```bash
openapi-generator-cli generate \
  -i openapi.yaml \
  -g nodejs-express-server \
  -o ./server/nodejs

cd server/nodejs
npm install
npm start
```

### Python/Flask Server
```bash
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python-flask \
  -o ./server/python

cd server/python
pip install -r requirements.txt
python -m openapi_server
```

### Go/Gin Server
```bash
openapi-generator-cli generate \
  -i openapi.yaml \
  -g go-gin-server \
  -o ./server/go
```

---

## Validation

### Request/Response Validation (Node.js)
```javascript
const express = require('express');
const OpenAPIValidator = require('express-openapi-validator');

const app = express();

app.use(express.json());

// Validate requests against OpenAPI spec
app.use(
  OpenAPIValidator.middleware({
    apiSpec: './openapi.yaml',
    validateRequests: true,
    validateResponses: true
  })
);

// Your routes here
app.get('/v1/places/nearby', (req, res) => {
  // Request automatically validated
  // If invalid, returns 400 with details
  res.json({ places: [], total: 0, has_more: false });
});

// Error handler
app.use((err, req, res, next) => {
  res.status(err.status || 500).json({
    error: err.name,
    message: err.message,
    details: err.errors
  });
});

app.listen(8080);
```

### Python Validation
```python
from flask import Flask
from connexion import FlaskApp

# Connexion automatically validates against OpenAPI
app = FlaskApp(__name__, specification_dir='./')
app.add_api('openapi.yaml', strict_validation=True)

app.run(port=8080)
```

---

## Testing

### Mock Server (Prism)
```bash
# Install Prism
npm install -g @stoplight/prism-cli

# Run mock server (returns example responses)
prism mock openapi.yaml -p 8080

# Test endpoints
curl http://localhost:8080/v1/places/nearby?latitude=37.77&longitude=-122.41
```

### Contract Testing (Dredd)
```bash
# Install Dredd
npm install -g dredd

# Test your API against the spec
dredd openapi.yaml https://api.proximity.example.com/v1

# Or with local server
dredd openapi.yaml http://localhost:8080/v1
```

### Postman Collection
```bash
# Convert OpenAPI to Postman collection
npx openapi-to-postmanv2 \
  -s openapi.yaml \
  -o proximity-service.postman_collection.json

# Import to Postman
# File → Import → proximity-service.postman_collection.json
```

---

## Linting

### Validate OpenAPI Spec
```bash
# Install Spectral (OpenAPI linter)
npm install -g @stoplight/spectral-cli

# Lint the spec
spectral lint openapi.yaml

# With custom rules
spectral lint openapi.yaml --ruleset .spectral.yaml
```

### Custom Rules (.spectral.yaml)
```yaml
extends: spectral:oas
rules:
  operation-tags: error
  operation-description: warn
  no-eval-in-markdown: error
  no-script-tags-in-markdown: error
  openapi-tags: error
  operation-operationId: error
```

---

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/openapi.yml
name: OpenAPI Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Validate OpenAPI spec
        uses: mbowman100/swagger-validator-action@v1
        with:
          files: proximity-service/openapi.yaml
      
      - name: Lint with Spectral
        run: |
          npm install -g @stoplight/spectral-cli
          spectral lint proximity-service/openapi.yaml
      
      - name: Generate documentation
        run: |
          npx @redocly/cli build-docs openapi.yaml \
            --output=./docs/index.html
      
      - name: Deploy docs to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

---

## Documentation Hosting

### Host on GitHub Pages
```bash
# Generate static HTML documentation
npx @redocly/cli build-docs openapi.yaml -o docs/index.html

# Commit and push
git add docs/
git commit -m "Update API docs"
git push

# Enable GitHub Pages in repo settings → Pages → Source: docs folder
# Access at: https://username.github.io/proximity-service/
```

### Readme Badges
```markdown
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-green.svg)](openapi.yaml)
[![API Docs](https://img.shields.io/badge/API-Documentation-blue.svg)](https://api.proximity.example.com/docs)
```

---

## IDE Integration

### VS Code
Install extension: **OpenAPI (Swagger) Editor**
- Syntax highlighting
- Auto-completion
- Validation
- Preview

### IntelliJ IDEA
- Built-in OpenAPI support
- Right-click openapi.yaml → OpenAPI → Generate Code
- Preview documentation

---

## Best Practices

✅ **Version your API spec** with your code  
✅ **Auto-generate docs** in CI/CD  
✅ **Use examples** for all responses  
✅ **Validate requests** at runtime  
✅ **Generate clients** for consumers  
✅ **Lint regularly** with Spectral  
✅ **Mock early** for parallel development  
✅ **Test contracts** with Dredd/Pact  

---

## Troubleshooting

### Circular References
```yaml
# Use $ref to break circular dependencies
components:
  schemas:
    Place:
      properties:
        nearby_places:
          type: array
          items:
            $ref: '#/components/schemas/PlaceSummary'  # Reference, not inline
```

### Large Specs
```bash
# Split into multiple files
openapi.yaml       # Main file
paths/
  places.yaml      # Place endpoints
  search.yaml      # Search endpoints
components/
  schemas.yaml     # Schema definitions
  responses.yaml   # Response definitions
```

### Validation Errors
```bash
# Get detailed error information
spectral lint openapi.yaml --format pretty

# Check specific rule
spectral lint openapi.yaml --only operation-descriptions
```

---

## Additional Resources

- **OpenAPI Specification:** https://spec.openapis.org/oas/v3.0.0
- **OpenAPI Generator:** https://openapi-generator.tech/
- **Swagger Editor:** https://editor.swagger.io/
- **Redocly:** https://redocly.com/
- **Stoplight Studio:** https://stoplight.io/studio
- **API Design Guide:** https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.0.md
