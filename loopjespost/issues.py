"""Open and close GitHub Issues for Dirk to check by hand."""
from __future__ import annotations

import os

import requests

LABEL = "controleren"
API = "https://api.github.com"


def _github():
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        return None, None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    return f"{API}/repos/{repo}", headers


def create_issue(title: str, body: str) -> str:
    """Create an issue in the current repository. Returns its URL, or a note when run locally."""
    base, headers = _github()
    if not base:
        print(f"[lokaal, geen issue aangemaakt] {title}\n{body}\n")
        return "lokaal"
    resp = requests.post(f"{base}/issues", headers=headers,
                         json={"title": title, "body": body, "labels": [LABEL]}, timeout=20)
    resp.raise_for_status()
    return resp.json()["html_url"]


def resolve_issues(title: str, comment: str) -> int:
    """Close every open check-issue with this title, with a comment. Returns how many were closed."""
    base, headers = _github()
    if not base:
        print(f"[lokaal, geen issue gesloten] {title}: {comment}")
        return 0
    resp = requests.get(f"{base}/issues", headers=headers,
                        params={"state": "open", "labels": LABEL, "per_page": 100}, timeout=20)
    resp.raise_for_status()
    closed = 0
    for issue in resp.json():
        if issue["title"] != title:
            continue
        number = issue["number"]
        requests.post(f"{base}/issues/{number}/comments", headers=headers,
                      json={"body": comment}, timeout=20).raise_for_status()
        requests.patch(f"{base}/issues/{number}", headers=headers,
                       json={"state": "closed", "state_reason": "completed"}, timeout=20).raise_for_status()
        closed += 1
    return closed
