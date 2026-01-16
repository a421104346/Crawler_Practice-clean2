"""
Remotive 招聘 API 爬虫
"""
from backend.core.base_crawler import BaseCrawler
import logging
from typing import Optional
import inspect

logger = logging.getLogger(__name__)


class JobsCrawler(BaseCrawler):
    """Remotive 远程工作招聘爬虫"""
    
    def __init__(self, category: Optional[str] = None, search: Optional[str] = None):
        """
        初始化招聘爬虫
        
        Args:
            category: 岗位分类 (software-dev, data, devops等)
            search: 搜索关键词 (python, data analyst等)
        """
        super().__init__(use_fake_ua=True, base_delay=1.0)
        self.api_url = "https://remotive.com/api/remote-jobs"
        self.category = category
        self.search = search
    
    def _normalize_city(self, location: str) -> str:
        """
        规范化城市名称
        
        Args:
            location: 原始地址字符串
        
        Returns:
            规范化后的城市名
        """
        loc = (location or "").strip()
        if not loc:
            return "Unknown"
        
        # 常见格式： "City, Country" / "Country" / "Worldwide"
        if "," in loc:
            return loc.split(",", 1)[0].strip() or loc.strip()
        return loc
    
    async def run(self, progress_callback=None) -> dict:
        """
        执行爬虫流程
        
        Returns:
            爬取结果：{"jobs": [...], "total": N}
        """
        if progress_callback:
            self.progress_callback = progress_callback

        logger.info(f"Starting jobs crawler: category={self.category}, search={self.search}")

        if self.progress_callback:
            if inspect.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(10, "正在请求招聘数据...")
            else:
                self.progress_callback(10, "正在请求招聘数据...")
        
        # 构建请求参数
        params = {}
        if self.category:
            params["category"] = self.category
        if self.search:
            params["search"] = self.search
        
        # 发起请求
        response = await self.get(self.api_url, params=params, timeout=30)
        
        if not response or response.status_code != 200:
            logger.error(f"Failed to fetch jobs: status={response.status_code if response else 'None'}")
            if self.progress_callback:
                if inspect.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(90, "请求失败")
                else:
                    self.progress_callback(90, "请求失败")
            return {"jobs": [], "total": 0, "error": "Failed to fetch jobs"}
        
        # 解析 JSON 响应
        data = response.json()
        jobs = data.get("jobs", [])
        
        # 处理和规范化数据
        processed_jobs = []
        for job in jobs:
            try:
                tags = job.get("tags") or []
                
                processed_job = {
                    "id": job.get("id"),
                    "title": job.get("title"),
                    "company": job.get("company_name"),
                    "city": self._normalize_city(job.get("candidate_required_location") or ""),
                    "location_raw": job.get("candidate_required_location"),
                    "salary": job.get("salary"),
                    "publication_date": job.get("publication_date"),
                    "tags": [str(t).strip() for t in tags if str(t).strip()],
                    "category": job.get("category"),
                    "job_type": job.get("job_type"),
                    "url": job.get("url"),
                    "description": job.get("description", "")[:200]  # 截取前200字符
                }
                
                processed_jobs.append(processed_job)
                
            except Exception as e:
                logger.error(f"Error processing job: {e}")
                continue
        
        result = {
            "jobs": processed_jobs,
            "total": len(processed_jobs),
            "category": self.category,
            "search": self.search
        }
        
        logger.info(f"Jobs crawler completed: {len(processed_jobs)} jobs")
        if self.progress_callback:
            if inspect.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(100, "完成！")
            else:
                self.progress_callback(100, "完成！")
        return result
