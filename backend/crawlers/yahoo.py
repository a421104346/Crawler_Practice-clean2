from backend.core.base_crawler import BaseCrawler
import logging

class YahooCrawler(BaseCrawler):
    def __init__(self):
        # Initialize parent class, but tell it not to use random UA (use_fake_ua=False)
        # Yahoo is sensitive to UA, we need a stable PC UA
        super().__init__(use_fake_ua=False, base_delay=2.0)
        
        # Ensure headers match a perfect Chrome PC version
        self.client.headers.update({
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.crumb = None
        # Initialization logic moved to first request since it requires async calls

    async def _initialize_session(self):
        """Yahoo-specific initialization: visit homepage -> get Crumb"""
        logging.info("Initializing Yahoo session...")
        
        # 1. Visit homepage to get Cookie
        # This step allows the session's internal cookie jar to receive cookies
        await self.get("https://finance.yahoo.com")
        
        # 2. Get Crumb
        try:
            crumb_url = 'https://query1.finance.yahoo.com/v1/test/getcrumb'
            # Simulating Referer is an important disguise
            headers = {'Referer': 'https://finance.yahoo.com'}
            resp = await self.get(crumb_url, headers=headers)
            
            if resp and resp.status_code == 200:
                self.crumb = resp.text
                logging.info(f"Successfully got Crumb: {self.crumb}")
            else:
                logging.error(f"Failed to get Crumb. Status: {resp.status_code if resp else 'None'}")
                
        except Exception as e:
            logging.error(f"Error initializing Yahoo session: {e}")

    async def get_quote(self, symbol):
        """
        Business interface for fetching stock prices
        Users only need to call this without worrying about underlying logic
        """
        if not self.crumb:
            await self._initialize_session()
            
        if not self.crumb:
            logging.error("Cannot fetch quote: Crumb is missing")
            return None

        # Construct API URL with Crumb
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?symbol={symbol}&crumb={self.crumb}"
        
        # Reuse parent's get method (with retry and delay)
        resp = await self.get(url)
        
        if resp and resp.status_code == 200:
            return resp.json()
        else:
            return None
