import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crawler.crawler import CrawlResult
from app.db.models import CrawledPageRow


def save_crawl(session: Session, website: str, result: CrawlResult) -> str:
    crawl_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    rows = []
    for page in result.pages:
        parsed = page.parsed
        rows.append(
            CrawledPageRow(
                crawl_id=crawl_id,
                website=website,
                url=page.url,
                final_url=page.final_url,
                status_code=page.status_code,
                error=page.error,
                title=parsed.title if parsed else None,
                meta_description=parsed.meta_description if parsed else None,
                h1=parsed.h1 if parsed else None,
                canonical_url=parsed.canonical_url if parsed else None,
                robots_meta=parsed.robots_meta if parsed else None,
                crawled_at=now,
            )
        )
    session.add_all(rows)
    session.flush()
    return crawl_id


def list_crawled_pages(session: Session, crawl_id: str) -> list[CrawledPageRow]:
    stmt = (
        select(CrawledPageRow)
        .where(CrawledPageRow.crawl_id == crawl_id)
        .order_by(CrawledPageRow.id)
    )
    return list(session.scalars(stmt))