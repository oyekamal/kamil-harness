---
name: docker-pro
description: Docker best practices for Python/Django and React applications — multi-stage builds, production-ready Dockerfiles, docker-compose patterns, health checks, layer caching optimization, and common debugging. Use when writing a Dockerfile, setting up docker-compose, "container won't start", "build is slow", "image is too large", or deploying Django/React to production.
---

# Docker Pro

Production-ready Docker patterns for Python/Django backends and React frontends.

## Multi-Stage Build: Django

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Stage: deps (cached separately from app code)
FROM base AS deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Stage: production
FROM base AS production
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Non-root user for security
RUN addgroup --system app && adduser --system --group app
COPY --chown=app:app . .

USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "config.wsgi:application"]
```

## Multi-Stage Build: React

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s CMD wget -qO- http://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

## docker-compose: Django + Postgres + Redis

```yaml
# docker-compose.yml
version: '3.9'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  web:
    build:
      context: .
      target: production  # use multi-stage target
    environment:
      DATABASE_URL: postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"

  celery:
    build:
      context: .
      target: production
    command: celery -A config worker --loglevel=info --concurrency=4
    environment:
      DATABASE_URL: postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  postgres_data:
```

## Layer Caching: The #1 Performance Rule

**Order: Rarely-changing → Frequently-changing**

```dockerfile
# WRONG — app code change invalidates pip cache
COPY . .
RUN pip install -r requirements.txt

# CORRECT — pip cache survives app code changes
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

Same for Node:
```dockerfile
# requirements first, then code
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

## .dockerignore (Always Include)

```
.git
.gitignore
__pycache__
*.pyc
*.pyo
.pytest_cache
.env
.env.*
node_modules
dist
build
*.log
.DS_Store
```

## Health Checks

```python
# Django health check endpoint (add to urls.py)
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    # Check DB connection
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    
    status = 200 if db_ok else 503
    return JsonResponse({"status": "ok" if db_ok else "error", "db": db_ok}, status=status)
```

## Common Issues

| Problem | Cause | Fix |
|---|---|---|
| Build slow every time | Wrong layer order | Put requirements.txt COPY before app COPY |
| Image too large | Using full base image | Use slim/alpine variants |
| Container exits immediately | Foreground process exits | Don't use `&` — run CMD as foreground |
| DB connection refused | Container starts before DB ready | Use `depends_on` with `condition: service_healthy` |
| Permission denied on files | Running as root then switching user | `COPY --chown=app:app` before `USER app` |
| Env vars not available | Build-time vs runtime confusion | Use `ARG` for build-time, `ENV`/docker-compose env for runtime |

## Useful Commands

```bash
# Build with no cache (for debugging)
docker build --no-cache -t myapp .

# Inspect image layers and sizes
docker history myapp

# Shell into running container
docker exec -it <container_id> /bin/sh

# View logs live
docker logs -f <container_id>

# Check resource usage
docker stats

# Remove all stopped containers + dangling images
docker system prune

# Run one-off command (DB migrations)
docker-compose run --rm web python manage.py migrate
```
