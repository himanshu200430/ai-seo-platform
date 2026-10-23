import logging
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.crawler.safe_http import fetch_text

logger = logging.getLogger(__name__)


def parse_sitemap(text: str) -> tuple[list[str], list[str]]:
    """Returns (page_urls, child_sitemap_urls)."""
    soup = BeautifulSoup(text, "html.parser")
    pages: list[str] = []
    children: list[str] = []
    for loc in soup.find_all("loc"):
        url = loc.get_text(strip=True)
        if not url:
            continue
        parent = loc.find_parent()
        if parent is not None and parent.name == "sitemap":
            children.append(url)
        else:
            pages.append(url)
    return pages, children


def load_sitemap_urls(
    site_root: str,
    fetch=fetch_text,
    max_urls: int = 500,
    max_sitemaps: int = 5,
) -> list[str]:
    host = urlparse(site_root).netloc.lower()
    to_visit = [urljoin(site_root, "/sitemap.xml")]
    visited: set[str] = set()
    urls: list[str] = []

    while to_visit and len(visited) < max_sitemaps and len(urls) < max_urls:
        sitemap_url = to_visit.pop(0)
        if sitemap_url in visited:
            continue
        visited.add(sitemap_url)

        result = fetch(sitemap_url)
        if result.error or result.status_code != 200 or not result.text:
            logger.info("No usable sitemap at %s (%s)", sitemap_url, result.error or result.status_code)
            continue

        pages, children = parse_sitemap(result.text)
        for url in pages:
            if urlparse(url).netloc.lower() == host and url not in urls:
                urls.append(url)
        for child in children:
            if urlparse(child).netloc.lower() == host:
                to_visit.append(child)

    return urls[:max_urls]