import logging
import time
from collections import deque
from urllib.parse import urldefrag, urlparse

from pydantic import BaseModel

from app.crawler.fetcher import fetch_page
from app.crawler.parser import ParsedPage, parse_page
from app.crawler.robots import RobotsPolicy, load_robots
from app.crawler.url_safety import validate_url

logger = logging.getLogger(__name__)

SKIP_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    ".zip", ".mp4", ".mp3", ".css", ".js", ".xml",
)


class CrawledPage(BaseModel):
    url: str
    final_url: str | None
    status_code: int | None
    error: str | None
    parsed: ParsedPage | None


class BrokenLink(BaseModel):
    url: str
    status_code: int | None
    error: str | None
    linked_from: list[str]


class CrawlResult(BaseModel):
    start_url: str
    pages: list[CrawledPage]
    skipped_by_robots: list[str]
    broken_internal_links: list[BrokenLink]


def _is_broken(page: CrawledPage) -> bool:
    if page.status_code is not None and page.status_code >= 400:
        return True
    return page.error is not None and page.error.startswith("Request failed")


def crawl_site(
    start_url: str,
    max_pages: int = 20,
    delay_seconds: float = 1.0,
    fetch=fetch_page,
    robots: RobotsPolicy | None = None,
    sleep=time.sleep,
    seed_urls: list[str] | None = None,
) -> CrawlResult:
    start, _ = urldefrag(start_url.strip())
    parsed_start = urlparse(start)
    host = parsed_start.netloc.lower()
    root = f"{parsed_start.scheme}://{parsed_start.netloc}"

    if robots is None:
        validate_url(root)  # galat ya khatarnak start URL yahin ruk jaaye
        policy = load_robots(root)
    else:
        policy = robots
    delay = max(delay_seconds, policy.crawl_delay() or 0.0)

    queue: deque[str] = deque([start])
    seen: set[str] = {start}
    pages: list[CrawledPage] = []
    skipped: list[str] = []
    linked_from: dict[str, set[str]] = {}
    for extra in seed_urls or []:
        extra, _ = urldefrag(extra)
        if extra not in seen and urlparse(extra).netloc.lower() == host:
            seen.add(extra)
            queue.append(extra)
       
    while queue and len(pages) < max_pages:
        url = queue.popleft()

        if not policy.can_fetch(url):
            skipped.append(url)
            continue

        if pages:
            sleep(delay)  # pehli request se pehle intezaar nahi
        result = fetch(url)

        parsed = None
        if result.html:
            parsed = parse_page(result.html, result.final_url or url)
            if not pages and urlparse(result.final_url or url).netloc.lower() != host:
                logger.warning("Start URL redirected to another host: %s", result.final_url)
            if (result.status_code or 0) < 400:
                for link in parsed.internal_links:
                    link_parts = urlparse(link)
                    if link_parts.netloc.lower() != host:
                        continue
                    if link_parts.path.lower().endswith(SKIP_EXTENSIONS):
                        continue
                    linked_from.setdefault(link, set()).add(url)
                    if link not in seen:
                        seen.add(link)
                        queue.append(link)

        pages.append(
            CrawledPage(
                url=url,
                final_url=result.final_url,
                status_code=result.status_code,
                error=result.error,
                parsed=parsed,
            )
        )

    broken = [
        BrokenLink(
            url=p.url,
            status_code=p.status_code,
            error=p.error,
            linked_from=sorted(linked_from.get(p.url, set())),
        )
        for p in pages
        if _is_broken(p)
    ]
    return CrawlResult(
        start_url=start,
        pages=pages,
        skipped_by_robots=skipped,
        broken_internal_links=broken,
    )