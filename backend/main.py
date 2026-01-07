from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from typing import Optional, Any
import sys
import os

# 将根目录添加到 sys.path，以便能导入 core 和 crawlers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.yahoo import YahooCrawler

app = FastAPI(title="Crawler Management API")

# 1. 定义请求模型
class CrawlerRequest(BaseModel):
    symbol: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL"
            }
        }

# 2. 定义响应模型
class CrawlerResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """健康检查接口"""
    return {"message": "Crawler API is running", "version": "1.0.0"}

@app.post("/api/yahoo/run", response_model=CrawlerResponse)
async def run_yahoo(request: CrawlerRequest):
    """
    启动 Yahoo 爬虫 (同步代码在异步线程池中运行)
    """
    try:
        # 初始化爬虫
        # 注意：这里每次请求都会新建一个 Crawler 实例 (包括初始化 session)
        # 以后可以优化为单例模式或连接池
        crawler = YahooCrawler()
        
        # 关键点：使用 asyncio.to_thread 将同步的 crawler.get_quote 放到线程池运行
        # 这样不会阻塞 FastAPI 的主循环
        print(f"Starting crawl for {request.symbol}...")
        result = await asyncio.to_thread(crawler.get_quote, request.symbol)
        
        if result:
            return CrawlerResponse(status="success", data=result)
        else:
            # 如果爬虫返回 None，抛出 404
            # 注意：这里我们返回 200 OK + status="error" 还是直接 404？
            # 根据 RESTful 规范，资源未找到应该 404
            raise HTTPException(status_code=404, detail=f"No data found for {request.symbol}")
            
    except HTTPException:
        raise
    except Exception as e:
        # 捕获所有其他异常并返回 500
        print(f"Error during crawl: {e}")
        return CrawlerResponse(status="error", error=str(e))

if __name__ == "__main__":
    import uvicorn
    # 开发模式启动
    uvicorn.run(app, host="0.0.0.0", port=8000)

