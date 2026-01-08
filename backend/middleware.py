"""
自定义中间件
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import uuid

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    记录每个请求的详细信息
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求并记录日志
        
        Args:
            request: 请求对象
            call_next: 下一个中间件/路由处理器
        
        Returns:
            响应对象
        """
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始
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
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 添加自定义响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            # 记录请求完成
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
            # 记录异常
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
    性能监控中间件
    监控慢请求
    """
    
    SLOW_REQUEST_THRESHOLD = 1.0  # 1 秒
    
    async def dispatch(self, request: Request, call_next):
        """
        监控请求性能
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
        
        Returns:
            响应对象
        """
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # 记录慢请求
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
