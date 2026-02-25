"""
Custom middleware
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import uuid

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Request logging middleware
    Logs detailed information for each request
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and log details
        
        Args:
            request: Request object
            call_next: Next middleware/route handler
        
        Returns:
            Response object
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client": request.client.host if request.client else None,
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            # Log request completion
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.4f}s",
                }
            )
            
            return response
            
        except Exception as e:
            # Log exception
            process_time = time.time() - start_time
            
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": f"{process_time:.4f}s",
                },
                exc_info=True
            )
            
            raise


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Performance monitoring middleware
    Monitors slow requests
    """
    
    SLOW_REQUEST_THRESHOLD = 1.0  # 1 second
    
    async def dispatch(self, request: Request, call_next):
        """
        Monitor request performance
        
        Args:
            request: Request object
            call_next: Next handler
        
        Returns:
            Response object
        """
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log slow requests
        if process_time > self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                "Slow request detected",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": f"{process_time:.4f}s",
                    "threshold": f"{self.SLOW_REQUEST_THRESHOLD}s",
                }
            )
        
        return response
