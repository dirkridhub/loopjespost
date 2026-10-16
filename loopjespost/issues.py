"""Open a GitHub Issue for Dirk to check by hand."""
from __future__ import annotations

import os

import requests

LABEL = "controleren"


def create_issue(title: str, body: str) -> str:
    """Create an issue in the current repository. Returns its URL, or a note when run locally."""
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print(f"[lokaal, geen issue aangemaakt] {title}\n{body}\n")
        return "lokaal"
    resp = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        json={"title": title, "body": body, "labels": [LABEL]},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["html_url"]
