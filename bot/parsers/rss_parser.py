from typing import List, Dict
import feedparser


class RSSParser:
    def __init__(self, limit: int = 20):
        self.limit = limit

    async def parse_feed(self, url: str) -> List[Dict]:
        feed = feedparser.parse(url)
        if feed.bozo:
            # feed.bozo_exception may contain details
            return []
        items: List[Dict] = []
        for entry in feed.entries[: self.limit]:
            title = getattr(entry, "title", "Без названия")
            link = getattr(entry, "link", None)
            summary = getattr(entry, "summary", "")
            published = getattr(entry, "published", None)
            source_name = getattr(feed.feed, "title", "RSS")
            if not link:
                continue
            items.append(
                {
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": published,
                    "source": source_name,
                    "type": "rss",
                }
            )
        return items


