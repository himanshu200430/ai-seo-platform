from app.crawler.checks import find_duplicates, find_missing_metadata
from app.crawler.crawler import crawl_site
from app.crawler.fetcher import FetchResult
from app.crawler.robots import parse_robots


def _page(links, title="T"):
    anchors = "".join(f'<a href="{link}">x</a>' for link in links)
    return (
        f"<html><head><title>{title}</title></head>"
        f"<body><h1>H</h1>{anchors}</body></html>"
    )


SITE = {
    "https://example.com/": (200, _page(["/a", "/b", "/private/x", "/missing"])),
    "https://example.com/a": (200, _page(["/"], title="A")),
    "https://example.com/b": (200, _page(["/a"], title="A")),
    "https://example.com/missing": (404, "<html><head><title>Not found</title></head></html>"),
}

ROBOTS_TEXT = "User-agent: *\nDisallow: /private\n"


def fake_fetch(url):
    status, html = SITE[url]  # galat URL maangega to KeyError, test fail
    return FetchResult(requested_url=url, final_url=url, status_code=status, html=html)


def _crawl(robots_text=ROBOTS_TEXT, max_pages=10, delay=1.0, sleeps=None):
    sleeps = sleeps if sleeps is not None else []
    return crawl_site(
        "https://example.com/",
        max_pages=max_pages,
        delay_seconds=delay,
        fetch=fake_fetch,
        robots=parse_robots(robots_text),
        sleep=sleeps.append,
    )


def test_crawl_respects_robots_and_finds_broken_links():
    sleeps = []
    result = _crawl(sleeps=sleeps)

    assert [p.url for p in result.pages] == [
        "https://example.com/",
        "https://example.com/a",
        "https://example.com/b",
        "https://example.com/missing",
    ]
    assert result.skipped_by_robots == ["https://example.com/private/x"]
    assert [b.url for b in result.broken_internal_links] == ["https://example.com/missing"]
    assert result.broken_internal_links[0].linked_from == ["https://example.com/"]
    assert sleeps == [1.0, 1.0, 1.0]  # 4 pages, pehli se pehle intezaar nahi


def test_max_pages_limit():
    result = _crawl(max_pages=2)
    assert len(result.pages) == 2


def test_crawl_delay_from_robots_is_honoured():
    sleeps = []
    _crawl(robots_text=ROBOTS_TEXT + "Crawl-delay: 3\n", sleeps=sleeps)
    assert set(sleeps) == {3.0}


def test_duplicate_and_missing_metadata():
    result = _crawl()
    assert find_duplicates(result.pages, "title") == {
        "a": ["https://example.com/a", "https://example.com/b"]
    }
    missing = find_missing_metadata(result.pages)
    assert missing["meta_description"] == [
        "https://example.com/",
        "https://example.com/a",
        "https://example.com/b",
    ]
    assert missing["title"] == []
    assert missing["h1"] == []