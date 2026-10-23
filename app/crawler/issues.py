import uuid
from datetime import datetime, timezone

from app.analysis.schemas import Issue
from app.crawler.checks import find_duplicates, find_missing_metadata
from app.crawler.crawler import CrawlResult

MISSING_SEVERITY = {"title": "high", "meta_description": "medium", "h1": "medium"}
DUPLICATE_SEVERITY = {"title": "medium", "meta_description": "low"}


def crawl_to_issues(result: CrawlResult, website: str) -> list[Issue]:
    now = datetime.now(timezone.utc)
    period = f"crawl on {now.date()}"
    status_by_url = {p.url: p.status_code for p in result.pages}
    issues: list[Issue] = []

    def add(page_url, issue_type, severity, metrics, next_step):
        issues.append(
            Issue(
                issue_id=str(uuid.uuid4()),
                website=website,
                page_url=page_url,
                issue_type=issue_type,
                supporting_metrics=metrics,
                comparison_period=period,
                severity=severity,
                confidence="high",  # ye rule-based fact hai, andaza nahi
                detected_at=now,
                suggested_next_investigation=next_step,
            )
        )

    for field, urls in find_missing_metadata(result.pages).items():
        for url in urls:
            metrics = {}
            if status_by_url.get(url) is not None:
                metrics["status_code"] = float(status_by_url[url])
            add(
                url, f"missing_{field}", MISSING_SEVERITY[field], metrics,
                f"Check why this page has no {field}: template, CMS field, or "
                "intentional. Then decide the right value.",
            )

    for field in ("title", "meta_description"):
        for _, urls in find_duplicates(result.pages, field).items():
            for url in urls:
                others = [u for u in urls if u != url]
                add(
                    url, f"duplicate_{field}", DUPLICATE_SEVERITY[field],
                    {"duplicate_count": float(len(urls))},
                    f"Pages sharing this {field}: " + ", ".join(others[:5]),
                )

    for b in result.broken_internal_links:
        metrics = {"inbound_links": float(len(b.linked_from))}
        if b.status_code is not None:
            metrics["status_code"] = float(b.status_code)
        add(
            b.url, "broken_internal_link",
            "high" if len(b.linked_from) >= 3 else "medium", metrics,
            "Fix or remove links to this URL from: "
            + (", ".join(b.linked_from[:5]) or "unknown"),
        )

    return issues