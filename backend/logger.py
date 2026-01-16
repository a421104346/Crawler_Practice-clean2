"""
结构化日志配置
支持 JSON 格式日志输出，便于日志聚合和分析
"""
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from backend.config import settings


class JSONFormatter(logging.Formatter):
    """JSON 格式的日志输出器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON
        
        Args:
            record: 日志记录
        
        Returns:
            JSON 格式的日志字符串
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加额外字段
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging():
    """
    配置应用日志系统
    
    - 开发环境：彩色控制台输出
    - 生产环境：JSON 格式输出到文件和控制台
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    if settings.DEBUG:
        # 开发环境：控制台输出（带颜色）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # 简单格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 同时写入文件，便于排查问题
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    else:
        # 生产环境：JSON 格式
        
        # 1. 控制台处理器（JSON）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(console_handler)
        
        # 2. 文件处理器 - 普通日志
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
        
        # 3. 错误日志单独文件
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)
    
    # 第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    
    logging.info(f"Logging configured: level={settings.LOG_LEVEL}, debug={settings.DEBUG}")


# 添加 RotatingFileHandler
import logging.handlers
