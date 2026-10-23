import argparse
from collections import Counter
from urllib.parse import urlparse

from app.crawler.checks import find_duplicates, find_missing_metadata
from app.crawler.crawler import crawl_site
from app.crawler.issues import crawl_to_issues
from app.crawler.sitemap import load_sitemap_urls
from app.crawler.storage import save_crawl
from app.crawler.url_safety import UnsafeURLError
from app.db.init_db import init_db
from app.db.repository import save_issues
from app.db.session import SessionLocal
from app.logging_setup import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl a site you have permission to crawl")
    parser.add_argument("start_url")
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    parser.add_argument("--use-sitemap", action="store_true", help="seed the crawl from sitemap.xml")
    parser.add_argument("--save", action="store_true", help="save crawl and issues to the database")
    args = parser.parse_args()

    setup_logging()
    start = urlparse(args.start_url)
    website = start.netloc.lower()

    seeds: list[str] = []
    if args.use_sitemap:
        seeds = load_sitemap_urls(f"{start.scheme}://{start.netloc}")
        print(f"Sitemap URLs found: {len(seeds)}")

    try:
        result = crawl_site(
            args.start_url,
            max_pages=args.max_pages,
            delay_seconds=args.delay,
            seed_urls=seeds,
        )
    except UnsafeURLError as exc:
        print(f"Blocked: {exc}")
        return

    print(f"Crawled {len(result.pages)} pages")
    for p in result.pages:
        title = p.parsed.title if p.parsed else None
        print(f"  {p.status_code} | {p.url} | title={title!r}")

    if result.skipped_by_robots:
        print(f"\nSkipped by robots.txt ({len(result.skipped_by_robots)}):")
        for url in result.skipped_by_robots:
            print(f"  {url}")

    if result.broken_internal_links:
        print("\nBroken internal links:")
        for b in result.broken_internal_links:
            print(f"  {b.status_code or b.error} | {b.url} | linked from {b.linked_from}")

    for field in ("title", "meta_description"):
        dups = find_duplicates(result.pages, field)
        if dups:
            print(f"\nDuplicate {field}:")
            for value, urls in dups.items():
                print(f"  {value!r} -> {urls}")

    missing = find_missing_metadata(result.pages)
    print("\nMissing metadata:")
    for field, urls in missing.items():
        print(f"  {field}: {len(urls)} pages")

    issues = crawl_to_issues(result, website)
    print(f"\n{len(issues)} crawl issues:")
    for issue_type, count in sorted(Counter(i.issue_type for i in issues).items()):
        print(f"  {issue_type}: {count}")

    if args.save:
        init_db()
        with SessionLocal() as session:
            crawl_id = save_crawl(session, website, result)
            saved = save_issues(session, issues)
            session.commit()
        print(f"\nSaved crawl {crawl_id} ({len(result.pages)} pages) and {saved} issues")


if __name__ == "__main__":
    main()