from collections import defaultdict

from app.crawler.crawler import CrawledPage

def _ok_pages(pages: list[CrawledPage]) -> list[CrawledPage]:
    return [p for p in pages if p.parsed is not None and (p.status_code or 0) < 400]

def find_missing_metadata(pages: list[CrawledPage]) -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {"title": [], "meta_description": [], "h1":[]}
    for p in _ok_pages(pages):
        if not p.parsed.title:
            missing["title"].append(p.url)
        if not p.parsed.meta_description:
            missing["meta_description"].append(p.url)
        if not p.parsed.h1:
            missing["h1"].append(p.url)
    return missing

def find_duplicates(pages: list[CrawledPage],field: str) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for p in _ok_pages(pages):
        value = getattr(p.parsed, field)
        if value:
            groups[value.strip().lower()].append(p.url)
    return {value: urls for value, urls in groups.items() if len(urls) > 1}