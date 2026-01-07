from crawler_base import BaseCrawler
import logging

class YahooCrawler(BaseCrawler):
    def __init__(self):
        # 初始化父类，但告诉它不要乱用随机 UA (use_fake_ua=False)
        # Yahoo 对 UA 很敏感，我们需要一个稳定的 PC UA
        super().__init__(use_fake_ua=False, base_delay=2.0)
        
        # 再次确保 Header 是完美的 Chrome PC 版
        self.session.headers.update({
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.crumb = None
        self._initialize_session()

    def _initialize_session(self):
        """专门处理 Yahoo 的初始化逻辑：访问主页 -> 拿 Crumb"""
        logging.info("Initializing Yahoo session...")
        
        # 1. 访问主页拿 Cookie
        # 这一步是为了让 session 内部的 cookie jar 吃到 cookie
        self.get("https://finance.yahoo.com")
        
        # 2. 拿 Crumb
        try:
            crumb_url = 'https://query1.finance.yahoo.com/v1/test/getcrumb'
            # 模拟 Referer 是很重要的伪装
            headers = {'Referer': 'https://finance.yahoo.com'}
            resp = self.get(crumb_url, headers=headers)
            
            if resp and resp.status_code == 200:
                self.crumb = resp.text
                logging.info(f"Successfully got Crumb: {self.crumb}")
            else:
                logging.error(f"Failed to get Crumb. Status: {resp.status_code if resp else 'None'}")
                
        except Exception as e:
            logging.error(f"Error initializing Yahoo session: {e}")

    def get_quote(self, symbol):
        """
        获取股票价格的业务接口
        用户只需要调用这个，不需要关心底层逻辑
        """
        if not self.crumb:
            logging.error("Cannot fetch quote: Crumb is missing")
            return None

        # 构造带有 Crumb 的 API URL
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?symbol={symbol}&crumb={self.crumb}"
        
        # 复用父类的 get 方法（带重试和延时）
        resp = self.get(url)
        
        if resp and resp.status_code == 200:
            return resp.json()
        else:
            return None

