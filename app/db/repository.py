from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analysis.schemas import Issue
from app.db.models import SeoIssue

def save_issues(session:Session, issues: list[Issue]) -> int:
    rows = [SeoIssue(**issue.model_dump()) for issue in issues]
    session.add_all(rows)
    session.flush()
    return len(rows)

def list_issues(session: Session, website: str) -> list[SeoIssue]:
    stmt = (
        select(SeoIssue)
        .where(SeoIssue.website == website)
        .order_by(SeoIssue.detected_at.desc())
    )
    return list(session.scalars(stmt))