import requests
from bs4 import BeautifulSoup
import time
import random
from pathlib import Path

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://ph.jobstreet.com/",
    "Connection": "keep-alive",
}

url = "https://ph.jobstreet.com/jobs-in-information-communication-technology"

# 输出目录：固定“相对脚本所在目录”，避免你从不同工作目录运行导致路径飘来飘去
# 你只需要改 OUTPUT_DIR 最后一段即可（比如改成 BASE_DIR / "output" / "xxx"）
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output" / "jobstreet"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"输出目录: {OUTPUT_DIR.resolve()}")

# 随机延时，降低触发风控的概率（不保证能绕过 403）
time.sleep(random.uniform(1.5, 3.5))

try:
    with requests.Session() as s:
        resp = s.get(url, headers=headers, timeout=15, allow_redirects=True)
        print(f"状态码: {resp.status_code}")

        if not resp.ok:
            # 403 常见：被站点风控拦截；先把页面内容保存下来方便你分析需要哪些 headers/cookies
            debug_path = OUTPUT_DIR / "jobstreet_debug.html"
            debug_path.write_text(resp.text, encoding="utf-8")
            print(f"请求失败，已把响应内容保存为 {debug_path}（用于排查 403/跳转/验证码）。")
            raise SystemExit(1)

        # 保存页面 HTML，便于你后续写选择器（建议先在浏览器打开这个文件看结构）
        page_path = OUTPUT_DIR / "jobstreet_page.html"
        page_path.write_text(resp.text, encoding="utf-8")
        print(f"已保存页面为 {page_path}")

        # 先给一个“占位解析”：等你确认页面结构后再精确提取（现在 403 时不会走到这里）
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "(no title)"
        print(f"页面标题: {title}")
except requests.exceptions.RequestException as e:
    print(f"网络请求异常: {e}")