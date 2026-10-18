from datetime import datetime
from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class SeoIssue(Base):
    __tablename__ = "seo_issues"

    issue_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    website: Mapped[str] = mapped_column(String(255), index=True)
    page_url: Mapped[str] = mapped_column(Text)
    issue_type: Mapped[str] = mapped_column(String(50))
    supporting_metrics: Mapped[dict] = mapped_column(JSONB)
    comparison_period: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(10))
    confidence: Mapped[str] = mapped_column(String(10))
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    suggested_next_investigation: Mapped[str] = mapped_column(Text)