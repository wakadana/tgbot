from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class WebParser:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        }

    async def parse_page(self, url: str) -> List[Dict]:
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
        except Exception:
            return []

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove scripts and styles
        for tag in soup(["script", "style"]):
            tag.decompose()

        title_tag = soup.find(["h1", "title"]) or soup.find("h2") or soup.find("h3")
        title = title_tag.get_text(strip=True) if title_tag else "Материал сайта"

        article = soup.find(["article", "main"]) or soup.find("div", class_="content")
        if not article:
            article = soup

        paragraphs = [p.get_text(strip=True) for p in article.find_all("p")]
        text = " ".join(paragraphs)[:1000]

        if not text:
            text = (soup.get_text(" ", strip=True) or "")[:1000]

        return [
            {
                "title": title,
                "link": url,
                "summary": text,
                "published": None,
                "source": url.split("/")[2] if "//" in url else url,
                "type": "website",
            }
        ]


