from app.crawler.storage import list_crawled_pages, save_crawl
from app.db.init_db import init_db
from app.db.session import SessionLocal


def test_save_and_read_crawl(sample_crawl):
    init_db()
    with SessionLocal() as session:
        try:
            crawl_id = save_crawl(session, "test-crawl.example", sample_crawl)
            rows = list_crawled_pages(session, crawl_id)

            assert {r.url for r in rows} == {p.url for p in sample_crawl.pages}
            home = next(r for r in rows if r.url == "https://example.com/")
            assert home.title == "Home"
            assert home.meta_description is None
        finally:
            session.rollback()