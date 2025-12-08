from urllib.parse import urlparse
import hashlib

import feedparser
import requests
from django.core.cache import cache
from django.utils.html import strip_tags

ALLOWED_HOSTS = {"skatteverket.se", "www7.skatteverket.se", "www4.skatteverket.se"}

def get_rss_items(url: str, limit: int = 8, cache_seconds: int = 1800):
    p = urlparse(url)
    if p.scheme not in {"http", "https"} or p.hostname not in ALLOWED_HOSTS:
        return []

    url_key = hashlib.sha256(url.encode("utf-8")).hexdigest()
    cache_key = f"rss:skv:{url_key}:{limit}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        r = requests.get(
            url,
            timeout=6,
            headers={"User-Agent": "HarpansRedovisning/1.0 (+https://harpans.se)"},
        )
        r.raise_for_status()

        feed = feedparser.parse(r.text)
        items = []
        for e in (feed.entries or [])[:limit]:
            items.append({
                "title": (e.get("title") or "").strip(),
                "link": e.get("link") or "",
                "published": e.get("published") or e.get("updated") or "",
                "summary": strip_tags(e.get("summary") or "")[:180],
            })

        cache.set(cache_key, items, cache_seconds)
        return items
    except Exception:
        cache.set(cache_key, [], 300)  # kort cache vid fel
        return []
