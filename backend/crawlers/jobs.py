"""
Remotive Jobs API crawler
"""
from backend.core.base_crawler import BaseCrawler
import logging
from typing import Optional
import inspect

logger = logging.getLogger(__name__)


class JobsCrawler(BaseCrawler):
    """Remotive remote job crawler"""
    
    def __init__(self, category: Optional[str] = None, search: Optional[str] = None):
        """
        Initialize jobs crawler
        
        Args:
            category: Job category (software-dev, data, devops, etc.)
            search: Search keyword (python, data analyst, etc.)
        """
        super().__init__(use_fake_ua=True, base_delay=1.0)
        self.api_url = "https://remotive.com/api/remote-jobs"
        self.category = category
        self.search = search
    
    def _normalize_city(self, location: str) -> str:
        """
        Normalize city name
        
        Args:
            location: Raw location string
        
        Returns:
            Normalized city name
        """
        loc = (location or "").strip()
        if not loc:
            return "Unknown"
        
        # Common formats: "City, Country" / "Country" / "Worldwide"
        if "," in loc:
            return loc.split(",", 1)[0].strip() or loc.strip()
        return loc
    
    async def run(self, progress_callback=None) -> dict:
        """
        Execute crawler workflow
        
        Returns:
            Crawl results: {"jobs": [...], "total": N}
        """
        if progress_callback:
            self.progress_callback = progress_callback

        logger.info(f"Starting jobs crawler: category={self.category}, search={self.search}")

        if self.progress_callback:
            if inspect.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(10, "Fetching job data...")
            else:
                self.progress_callback(10, "Fetching job data...")
        
        # Build request parameters
        params = {}
        if self.category:
            params["category"] = self.category
        if self.search:
            params["search"] = self.search
        
        # Send request
        response = await self.get(self.api_url, params=params, timeout=30)
        
        if not response or response.status_code != 200:
            logger.error(f"Failed to fetch jobs: status={response.status_code if response else 'None'}")
            if self.progress_callback:
                if inspect.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(90, "Request failed")
                else:
                    self.progress_callback(90, "Request failed")
            return {"jobs": [], "total": 0, "error": "Failed to fetch jobs"}
        
        # Parse JSON response
        data = response.json()
        jobs = data.get("jobs", [])
        
        # Process and normalize data
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
                    "description": job.get("description", "")[:200]  # Truncate to first 200 chars
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
                await self.progress_callback(100, "Done!")
            else:
                self.progress_callback(100, "Done!")
        return result
