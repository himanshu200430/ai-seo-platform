import pytest

from app.crawler.crawler import crawl_site
from app.crawler.fetcher import FetchResult
from app.crawler.robots import parse_robots

SITE = {
    "https://example.com/": (
        200,
        "<html><head><title>Home</title></head><body><h1>H</h1>"
        "<a href='/a'>a</a><a href='/b'>b</a><a href='/gone'>g</a></body></html>",
    ),
    "https://example.com/a": (
        200,
        "<html><head><title>Same</title><meta name='description' content='d'>"
        "</head><body><h1>A</h1></body></html>",
    ),
    "https://example.com/b": (
        200,
        "<html><head><title>Same</title><meta name='description' content='d'>"
        "</head><body></body></html>",
    ),
    "https://example.com/gone": (404, "<html><head><title>x</title></head></html>"),
}


def _fake_fetch(url):
    status, html = SITE[url]
    return FetchResult(requested_url=url, final_url=url, status_code=status, html=html)


@pytest.fixture
def sample_crawl():
    return crawl_site(
        "https://example.com/",
        max_pages=10,
        delay_seconds=0,
        fetch=_fake_fetch,
        robots=parse_robots("User-agent: *\nDisallow:\n"),
        sleep=lambda seconds: None,
    )