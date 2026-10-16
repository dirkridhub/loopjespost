"""Polite HTTP fetching: honour robots.txt, wait between requests to the same site."""
from __future__ import annotations

import time
import urllib.robotparser
from urllib.parse import urlparse

import requests

USER_AGENT = "LoopjespostBot/0.1 (+https://github.com/dirkridhub/loopjespost)"
DELAY_SECONDS = 3
TIMEOUT_SECONDS = 20


class FetchError(RuntimeError):
    pass


class Fetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_request: dict[str, float] = {}

    def _wait_for(self, host: str):
        last = self._last_request.get(host)
        if last is not None:
            remaining = DELAY_SECONDS - (time.monotonic() - last)
            if remaining > 0:
                time.sleep(remaining)
        self._last_request[host] = time.monotonic()

    def _allowed(self, url: str) -> bool:
        parts = urlparse(url)
        base = f"{parts.scheme}://{parts.netloc}"
        if base not in self._robots:
            parser = urllib.robotparser.RobotFileParser()
            self._wait_for(parts.netloc)
            try:
                resp = self.session.get(base + "/robots.txt", timeout=TIMEOUT_SECONDS)
                lines = resp.text.splitlines() if resp.status_code == 200 else []
            except requests.RequestException:
                lines = []
            parser.parse(lines)
            self._robots[base] = parser
        return self._robots[base].can_fetch(USER_AGENT, url)

    def get(self, url: str) -> str:
        if not self._allowed(url):
            raise FetchError(f"robots.txt staat het ophalen van {url} niet toe")
        self._wait_for(urlparse(url).netloc)
        try:
            resp = self.session.get(url, timeout=TIMEOUT_SECONDS)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise FetchError(f"{url}: {e}") from e
        resp.encoding = resp.encoding or resp.apparent_encoding
        return resp.text
