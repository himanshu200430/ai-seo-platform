import logging
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests

from app.crawler.fetcher import USER_AGENT
from app.crawler.url_safety import UnsafeURLError, validate_url

logger = logging.getLogger(__name__)

USER_AGENT_TOKEN = "AISEOBot"
MAX_ROBOTS_BYTES = 500_000
REDIRECT_CODES = (301,302, 303, 307, 308)

class RobotsPolicy:
    def __init__(self, parser: RobotFileParser | None, allow_all: bool):
        self._parser = parser
        self._allow_all = allow_all

    def can_fetch(self, url: str) -> bool:
        if self._parser is None:
            return self._allow_all
        return self._parser.can_fetch(USER_AGENT_TOKEN, url)

    def crawl_delay(self) -> float | None:
        if self._parser is None:
            return None
        delay = self._parser.crawl_delay(USER_AGENT_TOKEN)
        return float(delay) if delay is not None else None

def parse_robots(text:str) -> RobotsPolicy:
    parser = RobotFileParser()
    parser.parse(text.splitlines())
    parser.modified()
    return RobotsPolicy(parser, allow_all=True)

def load_robots(site_root: str, timeout: float = 10.0) -> RobotsPolicy:
    current = urljoin(site_root, "/robots.txt")
    try:
        for _ in range(4):
            validate_url(current)
            resp = requests.get(
                current,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
                allow_redirects=False,
                stream=True,
            )
            try:
                location = resp.headers.get("Location")
                if resp.status_code in REDIRECT_CODES and location:
                    current = urljoin(current, location)
                    continue

                if resp.status_code == 200:
                    body = resp.raw.read(MAX_ROBOTS_BYTES, decode_content=True)
                    return parse_robots(body.decode("utf-8", errors="replace"))
                if 400 <= resp.status_code < 500 and resp.status_code != 429:
                    return RobotsPolicy(None, allow_all=True)
                logger.warning("robots.txt returned %s; staying conservative", resp.status_code)
                return RobotsPolicy(None, allow_all=False)
            finally:
                resp.close()
        logger.warning("Too many redirects for robots.txt; staying conservative")
        return RobotsPolicy(None, allow_all=False)
    except(UnsafeURLError, requests.RequestException) as exc:
        logger.warning("Could not load robots.txt (%s); staying conservative", exc)
        return RobotsPolicy(None, allow_all=False)