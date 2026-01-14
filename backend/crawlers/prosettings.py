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
            
        # 使用 lxml 解析 HTML
        tree = html.fromstring(response.content)
        
        # 查找表格
        table = tree.xpath("//table[@id='pro-list-table']")
        
        players = []
        
        if table:
            table = table[0]
            
            # 提取表头并建立索引映射
            headers_raw = table.xpath(".//thead/tr/th//text()")
            # 清理表头: 去除空白, 转小写以便匹配
            header_map = {}
            current_col_idx = 0
            
            # 由于 xpath 可能会把一个 th 里的多个 text 节点分开返回，我们需要更精确地遍历 th 元素
            th_elements = table.xpath(".//thead/tr/th")
            for idx, th in enumerate(th_elements):
                # 获取该 th 下的所有文本并合并
                text_content = "".join(th.xpath(".//text()")).strip().lower()
                if text_content:
                    header_map[text_content] = idx
            
            logger.info(f"Detected headers mapping: {header_map}")
            
            # 提取行
            rows = table.xpath(".//tbody/tr")
            logger.info(f"Found {len(rows)} rows")
            
            total_rows = len(rows)
            
            for i, row in enumerate(rows):
                if progress_callback and i % 50 == 0 and i > 0:
                    current_progress = 40 + int((i / total_rows) * 50)
                    await progress_callback(current_progress, f"正在解析第 {i}/{total_rows} 行...")
                
                cells = row.xpath(".//td")
                if not cells:
                    continue
                
                # 提取这一行的所有文本数据，方便后续按索引取
                # 注意：有些单元格可能为空，我们需要确保索引对齐
                # cells 列表对应列索引
                
                def get_cell_text(col_name_keywords):
                    """辅助函数：根据列名关键字查找对应列的文本"""
                    for keyword in col_name_keywords:
                        # 尝试精确匹配或包含匹配
                        for h_name, h_idx in header_map.items():
                            if keyword in h_name:
                                if h_idx < len(cells):
                                    return "".join(cells[h_idx].xpath(".//text()")).strip()
                    return ""

                # 使用动态映射获取数据
                # 如果找不到对应列，回退到空字符串
                player = {
                    "team": get_cell_text(["team"]),
                    "player": get_cell_text(["player", "name"]),
                    "mouse": get_cell_text(["mouse"]),
                    "hz": get_cell_text(["hz", "polling"]),
                    "dpi": get_cell_text(["dpi"]),
                    "sens": get_cell_text(["sens", "sensitivity"]),
                    "edpi": get_cell_text(["edpi"]),
                    "zoom_sens": get_cell_text(["zoom", "zoom sens"]),
                    "monitor": get_cell_text(["monitor"]),
                    "resolution": get_cell_text(["res", "resolution"]),
                }
                
                # 如果根据表头没找到关键数据（如 player），尝试使用默认索引作为 fallback
                # 这是为了防止表头识别完全失败的情况
                if not player["player"] and len(cells) > 1:
                     player["player"] = "".join(cells[1].xpath(".//text()")).strip()
                
                if player["player"]: # 至少要有名字
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
