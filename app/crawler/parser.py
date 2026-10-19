from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel

class ParsedPage(BaseModel):
    url: str
    title:str | None
    meta_description: str | None
    h1: list[str]
    canonical_url: str | None
    robots_meta: str | None
    internal_links: list[str]
    external_links: list[str]

def _meta_content(soup: BeautifulSoup, name: str) -> str | None:
    for tag in soup.find_all("meta"):
        if str(tag.get("name", "")).strip().lower() == name:
            return str(tag.get("content", "")).strip() or None
    return None

def parse_page(html: str, page_url: str) -> ParsedPage:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    canonical = None
    for tag in soup.find_all("link", href=True):
        rels = [r.lower() for r in (tag.get("rel") or [])]
        if "canonical" in rels:
            canonical = urljoin(page_url, tag["href"].strip())
            break

    h1 = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
    h1 = [text for text in h1 if text]

    site = urlparse(page_url).netloc.lower()
    internal: set[str] = set()
    external: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute, _ = urldefrag(urljoin(page_url, href))
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc.lower() == site:
            internal.add(absolute)
        else:
            external.add(absolute)

    return ParsedPage(
        url=page_url,
        title=title,
        meta_description = _meta_content(soup,"description"),
        h1=h1,
        canonical_url=canonical,
        robots_meta=_meta_content(soup, "robots"),
        internal_links=sorted(internal),
        external_links=sorted(external),
    )
