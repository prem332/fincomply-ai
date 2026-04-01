import sys
import os
import re
import logging
import feedparser
import httpx
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MCA_RSS_URL

logger = logging.getLogger(__name__)

MCA_RSS_URLS = [
    "https://www.mca.gov.in/content/mca/global/en/data-and-reports/rss-feed.html",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FinComplyAI/1.0)"}


def _is_mca_url(url: str) -> bool:
    return bool(url) and "mca.gov.in" in url.lower()


def _parse_date(date_str: str) -> Optional[str]:
    if not date_str:
        return None
    try:
        from dateutil.parser import parse
        return parse(date_str).strftime("%Y-%m-%d")
    except Exception:
        return None


def _extract_mca_notification_number(title: str) -> str:
    patterns = [
        r"G\.S\.R\.\s*\d+\([A-Z]\)",
        r"S\.O\.\s*\d+\([A-Z]\)",
        r"MCA Notification[^\n]{0,50}",
    ]
    for p in patterns:
        m = re.search(p, title, re.IGNORECASE)
        if m:
            return m.group(0)[:100]
    return "MCA Notification"


def fetch_mca_data(query: str, max_results: int = 10) -> list[dict]:
    """Fetch MCA regulatory data from official mca.gov.in."""
    results: list[dict] = []
    query_terms = query.lower().split()

    for rss_url in MCA_RSS_URLS:
        try:
            resp = httpx.get(rss_url, headers=HEADERS, timeout=10.0, follow_redirects=True)
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:30]:
                title = getattr(entry, "title", "")
                summary = getattr(entry, "summary", "")
                link = getattr(entry, "link", "")
                published = getattr(entry, "published", "")

                if not _is_mca_url(link):
                    continue

                combined = f"{title} {summary}".lower()
                if not any(t in combined for t in query_terms if len(t) > 3):
                    continue

                results.append({
                    "title": title,
                    "content": f"{title}\n\n{summary}",
                    "source_url": link,
                    "published_date": _parse_date(published),
                    "domain": "mca",
                    "circular_number": _extract_mca_notification_number(title),
                    "is_gov_verified": True,
                })
                if len(results) >= max_results:
                    break
        except Exception as e:
            logger.error(f"MCA RSS fetch error: {e}")

    logger.info(f"MCA Tool: fetched {len(results)} results")
    return results[:max_results]