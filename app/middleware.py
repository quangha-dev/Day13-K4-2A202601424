from __future__ import annotations

import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Clear contextvars to avoid leakage between requests
        clear_contextvars()

        # 2. Extract x-request-id from headers or generate a new one (format: req-<8-char-hex>)
        correlation_id = request.headers.get("x-request-id")
        if not correlation_id:
            correlation_id = f"req-{uuid.uuid4().hex[:8]}"
        
        # 3. Bind the correlation_id to structlog contextvars and request state
        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id
        
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            response = JSONResponse(
                status_code=500,
                content={"detail": type(exc).__name__, "correlation_id": correlation_id},
            )
            response.headers["x-request-id"] = correlation_id
            response.headers["x-response-time-ms"] = f"{duration_ms:.2f}"
            return response
        
        # 4. Add the correlation_id and processing time (in ms) to response headers
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{duration_ms:.2f}"
        
        return response

