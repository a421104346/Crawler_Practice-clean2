
import os
from bs4 import BeautifulSoup

file_path = os.path.join("Rednote", "output", "xiaohongshu_debug.html")

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # 查找第一个 footer
    footer = soup.find(class_="footer")
    if footer:
        print("Found footer structure:")
        print(footer.prettify())
        
        # 尝试分析 author 部分
        author_wrapper = footer.find(class_="author-wrapper")
        if author_wrapper:
            print("\nAuthor wrapper structure:")
            print(author_wrapper.prettify())
    else:
        print("No footer found in HTML parsing.")

except Exception as e:
    print(f"Error: {e}")
