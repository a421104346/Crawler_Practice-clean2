"""
爬虫相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict


class CrawlerRequest(BaseModel):
    """启动爬虫的请求模型"""
    # 爬虫特定参数
    symbol: Optional[str] = Field(None, description="股票代码（Yahoo爬虫）", example="AAPL")
    page: Optional[int] = Field(1, description="页码", ge=1)
    keyword: Optional[str] = Field(None, description="搜索关键词")
    
    # 通用参数
    extra_params: Optional[Dict[str, Any]] = Field(default={}, description="额外参数")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "symbol": "AAPL",
                    "extra_params": {"days": 30}
                },
                {
                    "keyword": "python developer",
                    "page": 1
                }
            ]
        }


class CrawlerResponse(BaseModel):
    """爬虫响应模型（启动任务后的响应）"""
    status: str = Field(..., description="状态", example="success")
    task_id: str = Field(..., description="任务ID")
    message: str = Field(..., description="消息", example="Task created successfully")
    timestamp: Optional[str] = None


class CrawlerInfo(BaseModel):
    """爬虫信息模型"""
    name: str = Field(..., description="爬虫名称", example="yahoo")
    display_name: str = Field(..., description="显示名称", example="Yahoo Finance")
    description: str = Field(..., description="描述")
    parameters: list[str] = Field(..., description="必需参数")
    optional_parameters: list[str] = Field(default=[], description="可选参数")
    status: str = Field(default="active", description="爬虫状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "yahoo",
                "display_name": "Yahoo Finance",
                "description": "抓取 Yahoo Finance 股票数据",
                "parameters": ["symbol"],
                "optional_parameters": ["days"],
                "status": "active"
            }
        }
