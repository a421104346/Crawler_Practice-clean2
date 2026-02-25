"""
Crawler-related Pydantic models
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict


class CrawlerRequest(BaseModel):
    """Crawler launch request model"""
    # Crawler-specific parameters
    symbol: Optional[str] = Field(
        None,
        description="Stock symbol (Yahoo crawler)",
        json_schema_extra={"example": "AAPL"}
    )
    page: Optional[int] = Field(1, description="Page number", ge=1)
    max_pages: Optional[int] = Field(1, description="Max pages (Movies crawler)", ge=1)
    search: Optional[str] = Field(None, description="Search keyword (Jobs crawler)")
    category: Optional[str] = Field(None, description="Category (Jobs crawler)")
    
    # General parameters
    extra_params: Optional[Dict[str, Any]] = Field(default={}, description="Extra parameters")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "symbol": "AAPL",
                    "extra_params": {"days": 30}
                },
                {
                    "search": "python developer",
                    "page": 1
                }
            ]
        }
    )


class CrawlerResponse(BaseModel):
    """Crawler response model (response after task launch)"""
    status: str = Field(
        ...,
        description="Status",
        json_schema_extra={"example": "success"}
    )
    task_id: str = Field(..., description="Task ID")
    message: str = Field(
        ...,
        description="Message",
        json_schema_extra={"example": "Task created successfully"}
    )
    timestamp: Optional[str] = None


class CrawlerInfo(BaseModel):
    """Crawler info model"""
    name: str = Field(
        ...,
        description="Crawler name",
        json_schema_extra={"example": "yahoo"}
    )
    display_name: str = Field(
        ...,
        description="Display name",
        json_schema_extra={"example": "Yahoo Finance"}
    )
    description: str = Field(..., description="Description")
    parameters: list[str] = Field(..., description="Required parameters")
    optional_parameters: list[str] = Field(default=[], description="Optional parameters")
    status: str = Field(default="active", description="Crawler status")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "yahoo",
                "display_name": "Yahoo Finance",
                "description": "Scrape Yahoo Finance stock data",
                "parameters": ["symbol"],
                "optional_parameters": ["days"],
                "status": "active"
            }
        }
    )
