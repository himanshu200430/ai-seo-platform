import logging
from urllib.parse import urljoin

import requests
from pydantic import BaseModel

from app.crawler.fetcher import MAX_REDIRECTS, REDIRECT_CODES, USER_AGENT
from app.crawler.url_safety import UnsafeURLError, validate_url

logger = logging.getLogger(__name__)

MAX_TEXT_BYTES = 2_000_000


class TextResult(BaseModel):
    status_code: int | None = None
    text: str | None = None
    error: str | None = None


def fetch_text(url: str, max_bytes: int = MAX_TEXT_BYTES, timeout: float = 10.0) -> TextResult:
    current = url
    try:
        for _ in range(MAX_REDIRECTS + 1):
            validate_url(current)
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
                        return TextResult(
                            status_code=resp.status_code,
                            error="Redirect without Location header",
                        )
                    current = urljoin(current, location)
                    continue

                body = resp.raw.read(max_bytes + 1, decode_content=True)
                if len(body) > max_bytes:
                    return TextResult(status_code=resp.status_code, error="Response too large")
                return TextResult(
                    status_code=resp.status_code,
                    text=body.decode(resp.encoding or "utf-8", errors="replace"),
                )
            finally:
                resp.close()

        return TextResult(error="Too many redirects")
    except UnsafeURLError as exc:
        logger.warning("Blocked unsafe URL %s: %s", url, exc)
        return TextResult(error=f"Blocked: {exc}")
    except requests.RequestException as exc:
        return TextResult(error=f"Request failed: {exc}")