# Deployment and DevOps Guide

> **"Code isn't done until it's running in production."**
>
> Complete guide to deploying distributed systems: containers, orchestration, CI/CD, and deployment strategies.

---

## Table of Contents

1. [Containerization with Docker](#containerization-with-docker)
2. [Orchestration with Kubernetes](#orchestration-with-kubernetes)
3. [CI/CD Pipelines](#cicd-pipelines)
4. [Deployment Strategies](#deployment-strategies)
5. [Infrastructure as Code](#infrastructure-as-code)
6. [Configuration Management](#configuration-management)
7. [Secrets Management](#secrets-management)
8. [Monitoring Deployments](#monitoring-deployments)

---

## Containerization with Docker

### Why Containers?

**Before containers:**
```
"It works on my machine!" 🤷
- Different OS versions
- Missing dependencies
- Configuration drift
```

**With containers:**
```
✅ Same environment everywhere
✅ All dependencies included
✅ Reproducible builds
✅ Easy to scale
```

### Dockerfile Best Practices

```dockerfile
# Use specific version (not 'latest')
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Non-root user for security
RUN useradd -m appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Stage Builds

```dockerfile
# Stage 1: Build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine
WORKDIR /app
# Copy only built artifacts (smaller image)
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

**Benefits:**
- Smaller final image (300MB → 80MB)
- No build tools in production
- Faster deployment

### Docker Compose for Local Development

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/app
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./:/app  # Hot reload in dev
    command: uvicorn main:app --reload

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Orchestration with Kubernetes

### Why Kubernetes?

**Without orchestration:**
- Manually deploy to servers
- Manually scale up/down
- Manually restart crashed containers
- Manual load balancing

**With Kubernetes:**
- Declarative deployment
- Auto-scaling
- Self-healing
- Built-in load balancing

### Basic Concepts

```
Kubernetes Hierarchy:

Cluster (entire infrastructure)
  └─ Namespace (logical grouping)
      └─ Deployment (manages Pods)
          └─ Pod (1+ containers)
              └─ Container (Docker image)
```

### Example: Deploy URL Shortener

**Deployment:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: url-shortener
  namespace: production
spec:
  replicas: 3  # Run 3 instances
  selector:
    matchLabels:
      app: url-shortener
  template:
    metadata:
      labels:
        app: url-shortener
    spec:
      containers:
      - name: api
        image: url-shortener:v1.2.3
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 3
```

**Service (Load Balancer):**
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: url-shortener
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: url-shortener
  ports:
  - port: 80
    targetPort: 8000
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods -n production
kubectl get services -n production

# View logs
kubectl logs -f deployment/url-shortener -n production

# Scale
kubectl scale deployment url-shortener --replicas=10
```

### Auto-Scaling

**Horizontal Pod Autoscaler:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: url-shortener-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: url-shortener
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## CI/CD Pipelines

### CI/CD Workflow

```
Code Push
   ↓
Trigger CI Pipeline
   ├─ Run tests
   ├─ Run linters
   ├─ Security scan
   └─ Build Docker image
        ↓
   Push to registry
        ↓
Trigger CD Pipeline
   ├─ Deploy to staging
   ├─ Run E2E tests
   ├─ Approval gate
   └─ Deploy to production
        ↓
   Monitor & Alert
```

### GitHub Actions Example

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linters
        run: |
          pip install black flake8 mypy
          black --check .
          flake8 .
          mypy .

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Snyk security scan
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  build-and-push:
    needs: [test, lint, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Log in to registry
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ${{ env.DOCKER_REGISTRY }} -u ${{ github.actor }} --password-stdin

      - name: Build and push Docker image
        run: |
          docker build -t ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .
          docker tag ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          docker push ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          docker push ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/url-shortener \
            api=${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n staging

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/url-shortener -n staging

      - name: Run smoke tests
        run: |
          curl -f https://staging.short.ly/health || exit 1

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://short.ly
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/url-shortener \
            api=${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n production

      - name: Monitor deployment
        run: |
          kubectl rollout status deployment/url-shortener -n production
```

---

## Deployment Strategies

### 1. Rolling Update (Default in K8s)

**How it works:**
```
Current: v1 (5 pods)
Target: v2

Step 1: Create 1 v2 pod → [v1, v1, v1, v1, v1, v2]
Step 2: Kill 1 v1 pod → [v1, v1, v1, v1, v2]
Step 3: Create 1 v2 pod → [v1, v1, v1, v1, v2, v2]
...
Final: All v2 pods → [v2, v2, v2, v2, v2]
```

**Pros:**
- ✅ Zero downtime
- ✅ Gradual rollout
- ✅ Built into Kubernetes

**Cons:**
- ❌ Both versions running simultaneously
- ❌ Slower rollout

**Use when:** Standard deployments, backward compatible changes

---

### 2. Blue-Green Deployment

**How it works:**
```
Blue (Current, 100% traffic) → Load Balancer
Green (New, 0% traffic) ← Deploy here

Test Green
Switch: 0% → 100% traffic
Keep Blue for rollback
```

**Kubernetes implementation:**
```yaml
# Blue deployment (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: url-shortener-blue
spec:
  replicas: 5
  selector:
    matchLabels:
      app: url-shortener
      version: blue
  template:
    metadata:
      labels:
        app: url-shortener
        version: blue
    spec:
      containers:
      - name: api
        image: url-shortener:v1

---
# Service (points to blue)
apiVersion: v1
kind: Service
metadata:
  name: url-shortener
spec:
  selector:
    app: url-shortener
    version: blue  # ← Switch to 'green' to flip traffic
  ports:
  - port: 80
    targetPort: 8000
```

**Deployment steps:**
```bash
# 1. Deploy green
kubectl apply -f deployment-green.yaml

# 2. Test green
kubectl port-forward deployment/url-shortener-green 8001:8000
curl http://localhost:8001/health

# 3. Switch traffic (instant!)
kubectl patch service url-shortener -p '{"spec":{"selector":{"version":"green"}}}'

# 4. Monitor for issues
# If issues, switch back:
kubectl patch service url-shortener -p '{"spec":{"selector":{"version":"blue"}}}'

# 5. Delete blue (after confidence)
kubectl delete deployment url-shortener-blue
```

**Pros:**
- ✅ Instant switchover
- ✅ Easy rollback
- ✅ Full testing before switch

**Cons:**
- ❌ Double resources (expensive)
- ❌ Database migrations tricky

**Use when:** Need instant rollback, can afford double resources

---

### 3. Canary Deployment

**How it works:**
```
V1 (95% traffic)
V2 (5% traffic) ← Canary

Monitor canary:
- Error rate
- Latency
- Business metrics

If good: 5% → 10% → 25% → 50% → 100%
If bad: Rollback
```

**Kubernetes + Istio:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: url-shortener
spec:
  hosts:
  - url-shortener
  http:
  - match:
    - headers:
        user-agent:
          regex: ".*mobile.*"
    route:
    - destination:
        host: url-shortener
        subset: v2
      weight: 100
  - route:
    - destination:
        host: url-shortener
        subset: v1
      weight: 95
    - destination:
        host: url-shortener
        subset: v2
      weight: 5
```

**Gradual rollout script:**
```bash
#!/bin/bash
# canary-rollout.sh

CANARY_WEIGHTS=(5 10 25 50 100)

for weight in "${CANARY_WEIGHTS[@]}"; do
    echo "Setting canary to $weight%"

    # Update traffic split
    kubectl patch virtualservice url-shortener \
      --type merge \
      -p "{\"spec\":{\"http\":[{\"route\":[{\"destination\":{\"host\":\"url-shortener\",\"subset\":\"v1\"},\"weight\":$((100-weight))},{\"destination\":{\"host\":\"url-shortener\",\"subset\":\"v2\"},\"weight\":$weight}]}]}}"

    # Monitor for 10 minutes
    echo "Monitoring canary..."
    sleep 600

    # Check error rate
    ERROR_RATE=$(curl -s http://prometheus/api/v1/query?query='rate(http_errors_total{version="v2"}[5m])' | jq .data.result[0].value[1])

    if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
        echo "❌ Canary failed! Error rate: $ERROR_RATE"
        echo "Rolling back..."
        kubectl patch virtualservice url-shortener \
          --type merge \
          -p '{"spec":{"http":[{"route":[{"destination":{"host":"url-shortener","subset":"v1"},"weight":100}]}]}}'
        exit 1
    fi

    echo "✅ Canary healthy at $weight%"
done

echo "🎉 Canary rollout complete!"
```

**Pros:**
- ✅ Gradual rollout
- ✅ Test with real traffic
- ✅ Limited blast radius

**Cons:**
- ❌ Complex setup (need service mesh)
- ❌ Slower rollout

**Use when:** New features with risk, want gradual validation

---

### 4. Feature Flags

**Deployment vs Release decoupled:**
```python
from launchdarkly import LDClient

ld_client = LDClient(sdk_key='your-sdk-key')

@app.route('/checkout')
def checkout():
    user = get_current_user()

    # Check feature flag
    if ld_client.variation('new-checkout-flow', user, False):
        return new_checkout()  # New code
    else:
        return old_checkout()  # Old code

# Deploy code to 100% of servers
# But enable for only 5% of users
# Gradually increase: 5% → 10% → 50% → 100%
```

**Benefits:**
- ✅ Deploy anytime, release later
- ✅ Rollback without deployment
- ✅ A/B testing
- ✅ User-specific rollout

**Use when:** Want fine-grained control over releases

---

## Infrastructure as Code

### Why IaC?

**Without IaC:**
- Manual changes in AWS console
- Undocumented infrastructure
- Can't reproduce environments
- No version control

**With IaC:**
- ✅ Infrastructure in Git
- ✅ Reproducible
- ✅ Version controlled
- ✅ Code review for infrastructure

### Terraform Example

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "production-vpc"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "production-cluster"
  role_arn = aws_iam_role.cluster.arn
  version  = "1.27"

  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier        = "production-db"
  engine            = "postgres"
  engine_version    = "15.3"
  instance_class    = "db.t3.medium"
  allocated_storage = 100

  db_name  = "app"
  username = "admin"
  password = var.db_password  # From secrets

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 30
  multi_az               = true
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "production-redis"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 2
  parameter_group_name = "default.redis7"
  port                 = 6379
}
```

**Usage:**
```bash
# Initialize
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy (careful!)
terraform destroy
```

---

## Configuration Management

### The 12-Factor App: Config

**Rule:** Store config in environment variables, not in code

**Bad:**
```python
DATABASE_URL = "postgresql://user:pass@localhost/db"  # ❌ Hardcoded
API_KEY = "sk_live_abc123"  # ❌ Secret in code
```

**Good:**
```python
import os

DATABASE_URL = os.getenv('DATABASE_URL')  # ✅ From environment
API_KEY = os.getenv('API_KEY')  # ✅ From environment
```

### Environment-Specific Config

```bash
# .env.development
DATABASE_URL=postgresql://localhost/app_dev
REDIS_URL=redis://localhost:6379
LOG_LEVEL=DEBUG
FEATURE_NEW_CHECKOUT=true

# .env.production
DATABASE_URL=postgresql://prod-db.aws.com/app
REDIS_URL=redis://prod-redis.aws.com:6379
LOG_LEVEL=INFO
FEATURE_NEW_CHECKOUT=false
```

### Kubernetes ConfigMaps

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "INFO"
  FEATURE_NEW_CHECKOUT: "false"
  CACHE_TTL: "3600"
```

```yaml
# Use in deployment
spec:
  containers:
  - name: api
    envFrom:
    - configMapRef:
        name: app-config
```

---

## Secrets Management

### Never Commit Secrets!

```bash
# .gitignore
.env
.env.local
.env.production
secrets.yaml
*.key
*.pem
```

### Kubernetes Secrets

```bash
# Create secret
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password='SuperSecret123!'

# Use in deployment
spec:
  containers:
  - name: api
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
```

### HashiCorp Vault

```python
import hvac

# Connect to Vault
client = hvac.Client(url='http://vault:8200')
client.token = os.getenv('VAULT_TOKEN')

# Read secret
secret = client.secrets.kv.v2.read_secret_version(path='app/database')
db_password = secret['data']['data']['password']

# Use secret
DATABASE_URL = f"postgresql://admin:{db_password}@db:5432/app"
```

---

## Monitoring Deployments

### Deployment Metrics

```yaml
apiVersion: v1
kind: Service
metadata:
  name: url-shortener
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
spec:
  selector:
    app: url-shortener
  ports:
  - port: 80
    targetPort: 8000
```

### Key Metrics to Monitor

**During deployment:**
- Error rate (should not increase)
- Latency (should not increase)
- Pod restart count (should be 0)
- Resource usage (CPU, memory)

**Prometheus query:**
```promql
# Error rate increase
rate(http_errors_total{version="v2"}[5m])
/
rate(http_requests_total{version="v2"}[5m])
> 0.05

# Latency increase
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{version="v2"}[5m]))
> 1.0

# Pod restarts
increase(kube_pod_container_status_restarts_total[15m]) > 0
```

### Automated Rollback

```bash
#!/bin/bash
# monitor-deployment.sh

DEPLOYMENT="url-shortener"
NAMESPACE="production"

# Monitor for 10 minutes
for i in {1..20}; do
    # Check error rate
    ERROR_RATE=$(curl -s "http://prometheus/api/v1/query?query=rate(http_errors_total[5m])" | jq -r '.data.result[0].value[1]')

    if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
        echo "❌ High error rate detected: $ERROR_RATE"
        echo "Rolling back deployment..."
        kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE
        exit 1
    fi

    echo "✅ Deployment healthy (error rate: $ERROR_RATE)"
    sleep 30
done

echo "🎉 Deployment successful!"
```

---

## Deployment Checklist

### Before Deployment ✅

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Security scan passed
- [ ] Database migrations tested
- [ ] Feature flags configured
- [ ] Rollback plan documented
- [ ] On-call engineer notified

### During Deployment ✅

- [ ] Monitor error rate
- [ ] Monitor latency
- [ ] Monitor resource usage
- [ ] Check logs for errors
- [ ] Verify health checks passing

### After Deployment ✅

- [ ] Smoke tests passed
- [ ] Metrics stable for 30 minutes
- [ ] No alerts fired
- [ ] Documentation updated
- [ ] Deployment postmortem (if issues)

---

## Key Takeaways

1. **Containers** - Package once, run anywhere
2. **Kubernetes** - Orchestration at scale
3. **CI/CD** - Automate everything
4. **Deployment Strategies** - Choose based on risk tolerance
5. **Infrastructure as Code** - Version control infrastructure
6. **Secrets Management** - Never commit secrets
7. **Monitor Deployments** - Automated rollback on errors
8. **Feature Flags** - Decouple deploy from release

---

**Related Guides:**
- [Testing Guide](./TESTING-DISTRIBUTED-SYSTEMS.md)
- [Observability Guide](./system-design-topics/54-observability-and-sre-fundamentals-EXPANDED.md)
- [Hands-On Labs](./hands-on-labs/)

Good luck deploying! 🚀
