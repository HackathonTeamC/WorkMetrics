import logging
import time
from typing import Callable

from fastapi import Request, Response

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Structured logging middleware for request/response tracking.
    
    Logs request details, response status, and processing time in a structured format.
    """
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": f"{process_time:.3f}s",
        },
    )
    
    # Add custom header with processing time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    
    return response
