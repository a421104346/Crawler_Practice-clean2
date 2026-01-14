"""
ProSettings 爬虫
抓取 CS2 职业选手设置
"""
from backend.core.base_crawler import BaseCrawler
import logging
from lxml import html
import csv
import io

logger = logging.getLogger(__name__)


class ProSettingsCrawler(BaseCrawler):
    """ProSettings CS2 选手设置爬虫"""
    
    def __init__(self):
        super().__init__(use_fake_ua=True, base_delay=2.0)
        self.url = "https://prosettings.net/lists/cs2/"
        
    async def run(self, progress_callback=None) -> dict:
        """
        执行爬取
        """
        logger.info("Starting ProSettings crawler...")
        
        if progress_callback:
            await progress_callback(10, "正在获取页面...")
            
        response = await self.get(self.url)
        
        if not response or response.status_code != 200:
            error_msg = f"Failed to fetch {self.url}"
            logger.error(error_msg)
            return {"error": error_msg, "players": []}
            
        if progress_callback:
            await progress_callback(40, "正在解析数据...")
            
        # 使用 lxml 解析 HTML (无需 BeautifulSoup)
        tree = html.fromstring(response.content)
        
        # 查找表格 (根据 legacy 代码逻辑)
        # legacy: table id='pro-list-table'
        # xpath: //table[@id='pro-list-table']
        table = tree.xpath("//table[@id='pro-list-table']")
        
        players = []
        
        if table:
            table = table[0]
            
            # 提取表头
            headers = table.xpath(".//thead/tr/th//text()")
            headers = [h.strip() for h in headers if h.strip()]
            
            # 提取行
            rows = table.xpath(".//tbody/tr")
            logger.info(f"Found {len(rows)} rows")
            
            total_rows = len(rows)
            
            for i, row in enumerate(rows):
                # 每处理 50 行更新一次进度
                if progress_callback and i % 50 == 0 and i > 0:
                    current_progress = 40 + int((i / total_rows) * 50)
                    await progress_callback(current_progress, f"正在解析第 {i}/{total_rows} 行...")
                
                # 提取每列数据
                # 注意：有些单元格可能包含链接或图片，需要提取文本
                cells = row.xpath(".//td")
                row_data = {}
                
                if not cells:
                    continue
                    
                # 尝试映射数据 (简化版，只提取关键信息)
                # 这里的索引可能需要根据实际网页调整，暂时按顺序提取
                row_values = []
                for cell in cells:
                    # 提取所有文本并连接
                    text = " ".join([t.strip() for t in cell.xpath(".//text()") if t.strip()])
                    row_values.append(text)
                
                if row_values:
                    # 简单的字典结构
                    player = {
                        "team": row_values[0] if len(row_values) > 0 else "",
                        "player": row_values[1] if len(row_values) > 1 else "",
                        "mouse": row_values[2] if len(row_values) > 2 else "",
                        "hz": row_values[3] if len(row_values) > 3 else "",
                        "dpi": row_values[4] if len(row_values) > 4 else "",
                        "sens": row_values[5] if len(row_values) > 5 else "",
                        "edpi": row_values[6] if len(row_values) > 6 else "",
                        "zoom_sens": row_values[7] if len(row_values) > 7 else "",
                        "monitor": row_values[8] if len(row_values) > 8 else "",
                        "resolution": row_values[9] if len(row_values) > 9 else "",
                    }
                    players.append(player)
        else:
            logger.warning("Table 'pro-list-table' not found")
            
        if progress_callback:
            await progress_callback(95, "正在整理数据...")
            
        result = {
            "total": len(players),
            "players": players
        }
        
        if progress_callback:
            await progress_callback(100, "完成！")
            
        return result
