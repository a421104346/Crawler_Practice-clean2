import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 选取一个测试目标
test_url = "https://prosettings.net/players/zywoo/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    print(f"正在测试直接请求: {test_url}")
    response = requests.get(test_url, headers=headers, timeout=10)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试获取一些关键信息，比如鼠标型号
        # 这里只是举例查找，具体选择器可能需要根据页面调整
        title = soup.find('h1')
        print(f"页面标题: {title.get_text(strip=True) if title else '未找到标题'}")
        
        # 检查是否包含反爬虫提示
        if "Attention Required" in response.text or "Cloudflare" in response.text:
            print("警告: 似乎触发了 Cloudflare 验证！")
        else:
            print("成功: 页面看起来是正常的 HTML，可以直接解析！")
            
    else:
        print("请求失败")

except Exception as e:
    print(f"发生错误: {e}")
