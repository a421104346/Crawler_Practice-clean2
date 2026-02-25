"""
ProSettings crawler
Scrape CS2 pro player settings
"""
from backend.core.base_crawler import BaseCrawler
import logging
from lxml import html
import csv
import io

logger = logging.getLogger(__name__)


class ProSettingsCrawler(BaseCrawler):
    """ProSettings CS2 player settings crawler"""
    
    def __init__(self):
        super().__init__(use_fake_ua=True, base_delay=2.0)
        self.url = "https://prosettings.net/lists/cs2/"
        
    async def run(self, progress_callback=None) -> dict:
        """
        Execute scraping
        """
        logger.info("Starting ProSettings crawler...")
        
        if progress_callback:
            await progress_callback(10, "Fetching page...")
            
        response = await self.get(self.url)
        
        if not response or response.status_code != 200:
            error_msg = f"Failed to fetch {self.url}"
            logger.error(error_msg)
            return {"error": error_msg, "players": []}
            
        if progress_callback:
            await progress_callback(40, "Parsing data...")
            
        # Parse HTML using lxml
        tree = html.fromstring(response.content)
        
        # Find table
        table = tree.xpath("//table[@id='pro-list-table']")
        
        players = []
        
        if table:
            table = table[0]
            
            # Extract table headers and build index mapping
            headers_raw = table.xpath(".//thead/tr/th//text()")
            # Clean headers: trim whitespace, lowercase for matching
            header_map = {}
            current_col_idx = 0
            
            # Since xpath may return multiple text nodes per th separately, iterate th elements more precisely
            th_elements = table.xpath(".//thead/tr/th")
            for idx, th in enumerate(th_elements):
                # Get all text under this th and merge
                text_content = "".join(th.xpath(".//text()")).strip().lower()
                if text_content:
                    header_map[text_content] = idx
            
            logger.info(f"Detected headers mapping: {header_map}")
            
            # Extract rows
            rows = table.xpath(".//tbody/tr")
            logger.info(f"Found {len(rows)} rows")
            
            total_rows = len(rows)
            
            for i, row in enumerate(rows):
                if progress_callback and i % 50 == 0 and i > 0:
                    current_progress = 40 + int((i / total_rows) * 50)
                    await progress_callback(current_progress, f"Parsing row {i}/{total_rows}...")
                
                cells = row.xpath(".//td")
                if not cells:
                    continue
                
                # Extract all text data from this row for index-based access
                # Note: some cells may be empty, ensure index alignment
                # cells list corresponds to column indices
                
                def get_cell_text(col_name_keywords):
                    """Helper function: find column text by header keyword"""
                    for keyword in col_name_keywords:
                        # Try exact match or contains match
                        for h_name, h_idx in header_map.items():
                            if keyword in h_name:
                                if h_idx < len(cells):
                                    return "".join(cells[h_idx].xpath(".//text()")).strip()
                    return ""

                # Get data using dynamic mapping
                # If column not found, fall back to empty string
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
                
                # If key data (e.g. player) not found via headers, use default index as fallback
                # This prevents complete header recognition failure
                if not player["player"] and len(cells) > 1:
                     player["player"] = "".join(cells[1].xpath(".//text()")).strip()
                
                if player["player"]: # Must have at least a name
                    players.append(player)
        else:
            logger.warning("Table 'pro-list-table' not found")
            
        if progress_callback:
            await progress_callback(95, "Organizing data...")
            
        result = {
            "total": len(players),
            "players": players
        }
        
        if progress_callback:
            await progress_callback(100, "Done!")
            
        return result
