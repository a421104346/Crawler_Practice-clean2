from requests_html import AsyncHTMLSession
import sys
import os
import asyncio
import nest_asyncio

# Fix "There is no current event loop" issue
nest_asyncio.apply()

# Set stdout encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

url = "https://prosettings.net/games/cs2/page/50/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

async def main():
    try:
        print(f"Requesting (with JavaScript rendering): {url}")
        session = AsyncHTMLSession()
        response = await session.get(url, headers=headers)
        
        # Render page
        print("Rendering...")
        await response.html.arender(sleep=5, scrolldown=1, timeout=30)
        
        # Save rendered HTML
        debug_file = "anotherProsettingPractice/output/debug_page_50_rendered.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.html.html)
        print(f"Rendered HTML saved to {debug_file}")

        # Count results
        links = response.html.find("div.player_heading-wrapper h4 a")
        print(f"Found {len(links)} player links:")
        for i, link in enumerate(links):
            print(f"{i+1}. {link.text.strip()}")
            
        await session.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
