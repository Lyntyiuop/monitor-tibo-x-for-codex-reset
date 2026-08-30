from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser
import requests


@dataclass(frozen=True)
class Post:
    id: str
    author: str
    handle: str
    text: str
    url: str
    published: str


def fetch_latest_post(account_name: str, handle: str, feed_url: str, timeout: int = 20) -> Post | None:
    response = requests.get(feed_url, timeout=timeout, headers={"User-Agent": "codex-reset-monitor/1.0"})
    response.raise_for_status()

    parsed = feedparser.parse(response.text)
    if parsed.bozo and not parsed.entries:
        raise RuntimeError(f"Could not parse feed for @{handle}: {parsed.bozo_exception}")

    if not parsed.entries:
        return None

    entry = parsed.entries[0]
    post_id = getattr(entry, "id", None) or getattr(entry, "link", None)
    if not post_id:
        post_id = f"{handle}:{getattr(entry, 'published', '')}:{getattr(entry, 'title', '')}"

    text = getattr(entry, "summary", None) or getattr(entry, "title", "")
    published = getattr(entry, "published", None) or datetime.now(timezone.utc).isoformat()

    return Post(
        id=str(post_id),
        author=account_name,
        handle=handle,
        text=text,
        url=getattr(entry, "link", feed_url),
        published=published,
    )
