import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
response = requests.get("https://books.toscrape.com/")
# response = requests.get("https://movie.douban.com/top250", headers=headers)
if response.ok:
    print(f"状态码: {response.status_code}")
    print(f"网页长度: {len(response.text)} 字符")
else:
    print(f"请求失败，状态码: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")
all_titles = soup.find_all("h3")
for title in all_titles:
    for a in title.find_all("a"):
        print(a.string)

