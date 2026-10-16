"""Turn an HTML page into its main text (without menus and footers) and fingerprint it."""
from __future__ import annotations

import hashlib
import re

from bs4 import BeautifulSoup

DROP_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "form", "svg", "iframe"]
# Class/id fragments that mark navigation and boilerplate on common site builders.
DROP_MARKERS = ("nav", "menu", "footer", "cookie", "breadcrumb", "sidebar")


def _is_boilerplate(tag) -> bool:
    # Never drop page-level wrappers: their classes often describe the layout ("alt-nav-off").
    if tag.attrs is None or tag.name in ("html", "body", "main", "article"):
        return False
    for name in [*tag.get("class", []), tag.get("id") or ""]:
        parts = re.split(r"[-_\s]", name.lower())
        if "not" in parts:  # e.g. Weebly's "wsite-not-footer" is the main content
            continue
        if any(marker in parts for marker in DROP_MARKERS):
            return True
    return False


def main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(DROP_TAGS):
        tag.decompose()
    for tag in soup.find_all(_is_boilerplate):
        if not tag.decomposed:
            tag.decompose()
    text = soup.get_text(" ")
    text = text.replace("​", "")  # zero-width spaces some builders insert
    return re.sub(r"\s+", " ", text).strip()


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
