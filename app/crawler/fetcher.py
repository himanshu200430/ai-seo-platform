import logging
from urllib.parse import urljoin

import requests
from pydantic import BaseModel

from app.crawler.url_safety import UnsafeURLError, validate_url

logger = logging.getLogger(__name__)

USER_AGENT = "AISEOBot/0.1 (learning project)"
MAX_REDIRECTS = 5
MAX_BYTES = 2_000_000
REDIRECT_CODES = (301, 302, 303, 307, 308)


class FetchResult(BaseModel):
    requested_url: str
    final_url: str | None = None
    status_code: int | None = None
    html: str | None = None
    error: str | None = None


def fetch_page(url: str, timeout: float = 10.0) -> FetchResult:
    current = url
    try:
        for _ in range(MAX_REDIRECTS + 1):
            validate_url(current)  # har hop pe dobara check
            resp = requests.get(
                current,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
                allow_redirects=False,
                stream=True,
            )
            try:
                if resp.status_code in REDIRECT_CODES:
                    location = resp.headers.get("Location")
                    if not location:
                        return FetchResult(
                            requested_url=url, final_url=current,
                            status_code=resp.status_code,
                            error="Redirect without Location header",
                        )
                    current = urljoin(current, location)
                    continue

                content_type = resp.headers.get("Content-Type", "")
                if "html" not in content_type.lower():
                    return FetchResult(
                        requested_url=url, final_url=current,
                        status_code=resp.status_code,
                        error=f"Not an HTML page: {content_type}",
                    )

                body = resp.raw.read(MAX_BYTES + 1, decode_content=True)
                if len(body) > MAX_BYTES:
                    return FetchResult(
                        requested_url=url, final_url=current,
                        status_code=resp.status_code, error="Page too large",
                    )
                html = body.decode(resp.encoding or "utf-8", errors="replace")
                return FetchResult(
                    requested_url=url, final_url=current,
                    status_code=resp.status_code, html=html,
                )
            finally:
                resp.close()

        return FetchResult(requested_url=url, error="Too many redirects")
    except UnsafeURLError as exc:
        logger.warning("Blocked unsafe URL %s: %s", url, exc)
        return FetchResult(requested_url=url, error=f"Blocked: {exc}")
    except requests.RequestException as exc:
        return FetchResult(requested_url=url, error=f"Request failed: {exc}")