from requests_html import AsyncHTMLSession
import sys
import os
import asyncio
import nest_asyncio

# 解决 "There is no current event loop" 问题
nest_asyncio.apply()

# 设置标准输出编码为 utf-8
sys.stdout.reconfigure(encoding='utf-8')

url = "https://prosettings.net/games/cs2/page/50/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

async def main():
    try:
        print(f"正在请求 (支持 JavaScript 渲染): {url}")
        session = AsyncHTMLSession()
        response = await session.get(url, headers=headers)
        
        # 渲染页面
        print("正在渲染...")
        await response.html.arender(sleep=5, scrolldown=1, timeout=30)
        
        # 保存渲染后的 HTML
        debug_file = "anotherProsettingPractice/output/debug_page_50_rendered.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.html.html)
        print(f"渲染后的 HTML 已保存到 {debug_file}")

        # 计数
        links = response.html.find("div.player_heading-wrapper h4 a")
        print(f"找到 {len(links)} 个选手链接:")
        for i, link in enumerate(links):
            print(f"{i+1}. {link.text.strip()}")
            
        await session.close()

    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
