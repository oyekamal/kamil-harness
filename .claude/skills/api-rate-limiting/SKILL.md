---
name: api-rate-limiting
description: Implements API rate limiting and throttling controls using token bucket, sliding window, and fixed window algorithms to protect against brute force attacks, credential stuffing, resource exhaustion, and API abuse. Use when configuring DRF throttling, Redis rate limits, HTTP 429 responses, per-user/per-IP limits, or defending against API abuse. Activates for requests involving rate limiting implementation, API throttling setup, or request quota management.
domain: api-security
tags: [api-security, rate-limiting, throttling, redis, django, drf]
---

# API Rate Limiting and Throttling

## When to Use

- Protecting auth endpoints against brute force and credential stuffing
- Preventing API abuse from automated scripts
- Implementing fair usage quotas (free/premium/enterprise tiers)
- Defending against application-layer DoS
- Meeting compliance requirements for API abuse prevention

## DRF Built-in Throttling (Quickest Start)

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    }
}

# Per-view override
from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'

# settings.py
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].update({
    'burst': '60/min',
    'sustained': '1000/day',
})

class LoginView(APIView):
    throttle_classes = [BurstRateThrottle]
```

## Sliding Window Rate Limiter (Redis)

```python
import redis
import time
import hashlib
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class SlidingWindowRateLimiter:
    def __init__(self, redis_conn):
        self.redis = redis_conn

    def is_allowed(self, key, max_requests, window_seconds):
        now = time.time()
        window_start = now - window_seconds
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {f"{now}:{hashlib.md5(str(now).encode()).hexdigest()[:8]}": now})
        pipe.expire(key, window_seconds + 1)
        results = pipe.execute()
        current_count = results[1]

        if current_count >= max_requests:
            oldest = self.redis.zrange(key, 0, 0, withscores=True)
            retry_after = int(oldest[0][1] + window_seconds - now) + 1 if oldest else window_seconds
            return False, current_count, max_requests, retry_after
        return True, current_count + 1, max_requests, 0

rate_limiter = SlidingWindowRateLimiter(redis_client)

def rate_limit(max_requests, window_seconds, key_func=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask import request, jsonify, g
            if key_func:
                identifier = key_func()
            elif hasattr(g, 'user_id'):
                identifier = f"user:{g.user_id}"
            else:
                identifier = f"ip:{request.remote_addr}"

            key = f"ratelimit:{request.endpoint}:{identifier}"
            allowed, current, limit, retry_after = rate_limiter.is_allowed(key, max_requests, window_seconds)

            headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(max(0, limit - current)),
                "X-RateLimit-Reset": str(int(time.time()) + window_seconds),
            }

            if not allowed:
                headers["Retry-After"] = str(retry_after)
                response = jsonify({
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                })
                response.status_code = 429
                for h, v in headers.items():
                    response.headers[h] = v
                return response

            response = f(*args, **kwargs)
            for h, v in headers.items():
                response.headers[h] = v
            return response
        return wrapped
    return decorator
```

## Tiered Rate Limiting (Free/Premium/Enterprise)

```python
from enum import Enum

class UserTier(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

TIER_LIMITS = {
    UserTier.FREE: {
        "default": (60, 60),          # 60 req/min
        "search": (10, 60),
        "export": (5, 3600),
    },
    UserTier.PREMIUM: {
        "default": (300, 60),
        "search": (50, 60),
        "export": (20, 3600),
    },
    UserTier.ENTERPRISE: {
        "default": (1000, 60),
        "search": (200, 60),
        "export": (100, 3600),
    },
}

def get_rate_limit_for_request(user_tier, endpoint_category="default"):
    tier_config = TIER_LIMITS.get(user_tier, TIER_LIMITS[UserTier.FREE])
    return tier_config.get(endpoint_category, tier_config["default"])
```

## Django REST Framework + Redis Integration

```python
# custom_throttle.py
import redis
from rest_framework.throttling import SimpleRateThrottle

class RedisThrottle(SimpleRateThrottle):
    """Redis-backed throttle with sliding window."""
    scope = 'user_api'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}

# Rate limit config per endpoint type
RATE_LIMITS = {
    "auth.login": {"requests": 5, "window_seconds": 60, "by": "ip"},
    "auth.register": {"requests": 3, "window_seconds": 300, "by": "ip"},
    "api.free": {"requests": 60, "window_seconds": 60, "by": "user"},
    "api.premium": {"requests": 300, "window_seconds": 60, "by": "user"},
    "search": {"requests": 10, "window_seconds": 60, "by": "user"},
    "export": {"requests": 5, "window_seconds": 3600, "by": "user"},
}
```

## Response Headers (Always Include)

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705700400
Retry-After: 30   (only on 429)
```

## Endpoint Rate Limit Configuration

```python
RATE_LIMITS = {
    # Auth endpoints — most restrictive, by IP
    "auth/login":         {"requests": 5,    "window": 60,   "by": "ip"},
    "auth/register":      {"requests": 3,    "window": 300,  "by": "ip"},
    "auth/forgot_password": {"requests": 3,  "window": 3600, "by": "ip"},
    # Standard API — by user tier
    "api/default/free":   {"requests": 60,   "window": 60,   "by": "user"},
    "api/default/premium": {"requests": 300, "window": 60,   "by": "user"},
    # Resource-intensive
    "api/search":         {"requests": 10,   "window": 60,   "by": "user"},
    "api/export":         {"requests": 5,    "window": 3600, "by": "user"},
}
```

## Common Pitfalls

- Using in-memory rate limiting without shared state across instances (bypass by hitting different servers)
- Not implementing separate limits on auth endpoints vs general API
- Using fixed windows that allow burst at window boundaries (2x the limit briefly)
- Not including rate limit headers on successful responses
- Trusting X-Forwarded-For for IP without validating against load balancer
