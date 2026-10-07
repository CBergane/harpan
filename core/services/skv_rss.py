from urllib.parse import urlparse
import hashlib

from datetime import datetime
from calendar import timegm

import feedparser
import requests
from django.core.cache import cache
from django.utils.html import strip_tags


ALLOWED_HOSTS = {
    "skatteverket.se",
    "www7.skatteverket.se",
    "www4.skatteverket.se",
}


def _cache_keys(url: str, limit: int):
    url_key = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return (
        f"rss:skv:{url_key}:{limit}",
        f"rss:skv:stale:{url_key}:{limit}",
    )


def get_rss_items(
    url: str,
    limit: int = 8,
    cache_seconds: int = 1800,
    stale_seconds: int = 604800,
    force_refresh: bool = False,
):
    """
    Returnerar RSS-poster från cache.

    Normal sidvisning:
      - använder färsk cache om den finns
      - använder senaste fungerande data om färsk cache gått ut
      - blockerar därmed inte en besökare på Skatteverket

    force_refresh=True:
      - hämtar nytt innehåll från Skatteverket
      - används av bakgrundsjobbet/systemd-timern
    """

    p = urlparse(url)

    if (
        p.scheme not in {"http", "https"}
        or p.hostname not in ALLOWED_HOSTS
    ):
        return []

    cache_key, stale_key = _cache_keys(url, limit)

    cached = cache.get(cache_key)

    if cached is not None and not force_refresh:
        return cached

    stale = cache.get(stale_key)

    # En vanlig webbrequest ska hellre få senaste fungerande data
    # än vänta på ett externt RSS-anrop.
    if not force_refresh and stale is not None:
        cache.set(cache_key, stale, 300)
        return stale

    try:
        r = requests.get(
            url,
            timeout=6,
            headers={
                "User-Agent":
                    "HarpansRedovisning/1.0 (+https://harpans.se)"
            },
        )
        r.raise_for_status()

        feed = feedparser.parse(r.text)
        items = []

        for e in (feed.entries or [])[:limit]:
            published_dt = None

            if e.get("published_parsed"):
                published_dt = datetime.utcfromtimestamp(
                    timegm(e.published_parsed)
                )
            elif e.get("updated_parsed"):
                published_dt = datetime.utcfromtimestamp(
                    timegm(e.updated_parsed)
                )

            items.append(
                {
                    "title": (e.get("title") or "").strip(),
                    "link": e.get("link") or "",
                    "published": (
                        e.get("published")
                        or e.get("updated")
                        or ""
                    ),
                    "summary": strip_tags(
                        e.get("summary") or ""
                    )[:180],
                    "published_dt": published_dt,
                }
            )

        # Normal cache: 30 minuter
        cache.set(cache_key, items, cache_seconds)

        # Senaste fungerande kopian: 7 dagar
        cache.set(stale_key, items, stale_seconds)

        return items

    except Exception:
        # Skatteverket nere/långsamt:
        # använd senaste fungerande data.
        if stale is not None:
            cache.set(cache_key, stale, 300)
            return stale

        # Endast om vi aldrig tidigare fått fungerande data.
        cache.set(cache_key, [], 300)
        return []
