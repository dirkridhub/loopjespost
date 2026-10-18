"""Daily status check: fetch each race's pages, and only ask the AI when the text changed.

Run with: python -m loopjespost.monitor
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from . import ai
from .events import load_events
from .extract import fingerprint, main_text
from .fetch import Fetcher
from .issues import create_issue

ROOT = Path(__file__).resolve().parent.parent
# Bump when the reading rules change: every race is then read again once.
CHECK_VERSION = 2
UNKNOWN = ("", "onbekend")
DATE_FIELDS = ("datum_loopje", "inschrijving_opent_datum")
MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
          "augustus", "september", "oktober", "november", "december"]
LABELS = {
    "datum_loopje": "Datum loopje",
    "inschrijving_status": "Status inschrijving",
    "inschrijving_opent_datum": "Inschrijving opent (datum)",
    "inschrijving_opent_tijd": "Inschrijving opent (tijd)",
}


def _read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


_TYPOGRAPHY = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                              "–": "-", "—": "-", " ": " ", "…": "..."})


def _squash(text: str) -> str:
    """Lower-case, single spaces, plain quotes and dashes."""
    return re.sub(r"\s+", " ", text.translate(_TYPOGRAPHY)).strip().lower()


def _source_url(quote: str, pages: dict[str, str]) -> str:
    needle = _squash(quote).strip(" .!?\"'")
    for url, text in pages.items():
        if needle and needle in _squash(text):
            return url
    return ""


def _parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def _quote_has_date(quote: str, day: dt.date) -> bool:
    q = _squash(quote)
    month = MONTHS[day.month - 1]
    has_day = re.search(rf"(?<!\d)0?{day.day}(?!\d)", q)
    has_month = month in q or month[:3] + "." in q or re.search(rf"[-/]0?{day.month}[-/]", q)
    return bool(has_day and has_month)


def _quote_has_time(quote: str, value: str) -> bool:
    q = _squash(quote)
    hour, minute = int(value[:2]), value[3:]
    if value == "00:00" and "middernacht" in q:
        return True
    return bool(re.search(rf"(?<!\d)0?{hour}[:.]{minute}(?!\d)", q)
                or (minute == "00" and re.search(rf"(?<!\d)0?{hour} ?(uur|u)\b", q)))


def _check_value(name: str, f: dict) -> str | None:
    """Return why a found value cannot be trusted, or None if it can."""
    value, quote = f["waarde"], f["bron_zin"]
    if name in DATE_FIELDS:
        day = _parse_date(value)
        if not day:
            return "geen geldige datum"
        if not _quote_has_date(quote, day):
            return "datum staat niet in de bronzin"
    if name == "inschrijving_opent_tijd":
        if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", value):
            return "geen geldige tijd"
        if not _quote_has_time(quote, value):
            return "tijd staat niet in de bronzin"
    if not f["bron_url"]:
        return "bronzin staat niet letterlijk op de pagina"
    return None


def review(fields: dict, pages: dict[str, str], today: str) -> dict:
    """Downgrade confidence when a value is malformed or not backed by the page."""
    checked = {}
    for name in ai.FIELDS:
        f = dict(fields[name])
        f["bron_url"] = _source_url(f["bron_zin"], pages)
        if f["waarde"] not in UNKNOWN:
            reason = _check_value(name, f)
            if reason:
                f["zekerheid"], f["reden"] = "laag", reason
        checked[name] = f

    # A well-sourced race date in the past belongs to the previous edition:
    # the next edition (and its registration) is then simply unknown.
    race = checked["datum_loopje"]
    race_day = _parse_date(race["waarde"])
    if race_day and race_day.isoformat() < today and race.get("reden") is None:
        reason = f"vorige editie ({race_day.isoformat()})"
        for name in ai.FIELDS:
            checked[name] = {
                "waarde": "onbekend" if name == "inschrijving_status" else "",
                "zekerheid": "hoog",
                "bron_zin": race["bron_zin"] if name == "datum_loopje" else "",
                "bron_url": race["bron_url"] if name == "datum_loopje" else "",
                "reden": reason,
            }
    return checked


def uncertain_fields(fields: dict, previous: dict | None) -> list[str]:
    """Low confidence matters when it would set a value, or wipe a value we had."""
    out = []
    for name, f in fields.items():
        had_value = previous and previous[name]["waarde"] not in UNKNOWN
        if f["zekerheid"] == "laag" and (f["waarde"] not in UNKNOWN or had_value):
            out.append(name)
    return out


def _issue_body(event: dict, fields: dict, uncertain: list[str], previous: dict | None) -> str:
    rows = ["| Veld | Vorige waarde | Gevonden | Zekerheid | Bron |", "|---|---|---|---|---|"]
    for name, f in fields.items():
        old = previous[name]["waarde"] if previous else ""
        mark = " **(twijfel)**" if name in uncertain else ""
        quote = f"\"{f['bron_zin']}\"" if f["bron_zin"] else ""
        if f.get("reden"):
            quote += f" ({f['reden']})"
        rows.append(f"| {LABELS[name]}{mark} | {old or '-'} | {f['waarde'] or '-'} | {f['zekerheid']} | {quote} |")
    links = "\n".join(f"- {u}" for u in (event.get("website"), event.get("inschrijfpagina")) if u)
    return (
        f"De pagina van **{event['naam']}** is veranderd, maar de AI is niet zeker genoeg. "
        "Er is niets gepubliceerd.\n\n"
        + "\n".join(rows)
        + f"\n\nPagina's:\n{links}\n\n"
        f"Wat te doen: kijk op de pagina. Klopt het? Zet de juiste waarden in "
        f"`events/{event['id']}.yaml` en sluit dit issue."
    )


def _record_change(data_dir: Path, event: dict, today: str, fields: dict, previous: dict):
    changes = []
    for name, f in fields.items():
        if f["waarde"] != previous[name]["waarde"]:
            changes.append({
                "veld": name,
                "oud": previous[name]["waarde"],
                "nieuw": f["waarde"],
                "bron_zin": f["bron_zin"],
                "bron_url": f["bron_url"],
            })
    if not changes:
        return None
    path = data_dir / "changes" / f"{today}-{event['id']}.json"
    log = _read_json(path, [])
    log.append({"loopje": event["id"], "naam": event["naam"], "datum": today, "wijzigingen": changes})
    _write_json(path, log)
    return path


def _record_cost(data_dir: Path, today: str, usage: dict):
    path = data_dir / "costs" / f"{today[:7]}.json"
    totals = _read_json(path, {"ai_aanroepen": 0, "input_tokens": 0, "output_tokens": 0, "kosten_usd": 0.0})
    totals["ai_aanroepen"] += 1
    totals["input_tokens"] += usage["input_tokens"]
    totals["output_tokens"] += usage["output_tokens"]
    totals["kosten_usd"] = round(totals["kosten_usd"] + ai.cost_usd(usage), 4)
    _write_json(path, totals)


def check_event(
    event: dict,
    *,
    fetch: Callable[[str], str],
    read: Callable[[str, str, str], tuple[dict, dict]],
    open_issue: Callable[[str, str], str],
    data_dir: Path,
    today: str,
) -> str:
    """Check one race. Returns a short Dutch outcome label for the run log."""
    urls = list(dict.fromkeys(u for u in (event.get("website"), event.get("inschrijfpagina")) if u))
    pages = {url: main_text(fetch(url)) for url in urls}
    combined = "\n\n".join(f"[{url}]\n{text}" for url, text in pages.items())
    page_hash = fingerprint(f"v{CHECK_VERSION}\n{combined}")

    state_path = data_dir / "state" / f"{event['id']}.json"
    state = _read_json(state_path, {})
    state["gecontroleerd_op"] = today
    state.pop("laatste_fout", None)

    if state.get("hash") == page_hash:
        _write_json(state_path, state)
        return "ongewijzigd"

    fields, usage = read(combined, event["naam"], today)
    _record_cost(data_dir, today, usage)
    fields = review(fields, pages, today)
    previous = state.get("status")
    state["hash"] = page_hash

    uncertain = uncertain_fields(fields, previous)
    if uncertain:
        url = open_issue(
            f"Controleren: {event['naam']}",
            _issue_body(event, fields, uncertain, previous),
        )
        state["wacht_op_controle"] = url
        _write_json(state_path, state)
        return "controleren"

    state.pop("wacht_op_controle", None)
    state["status"] = fields
    _write_json(state_path, state)
    if previous is None:
        return "eerste meting"
    return "gewijzigd" if _record_change(data_dir, event, today, fields, previous) else "pagina anders, status gelijk"


def run(root: Path = ROOT) -> int:
    today = dt.datetime.now(ZoneInfo("Europe/Amsterdam")).date().isoformat()
    events = load_events(root / "events")
    fetcher = Fetcher()
    data_dir = root / "data"
    results: dict[str, list[str]] = {}

    def read(text, name, day):
        return ai.read_status(text, name, day)

    for event in events:
        try:
            outcome = check_event(
                event, fetch=fetcher.get, read=read, open_issue=create_issue,
                data_dir=data_dir, today=today,
            )
        except Exception as e:  # one broken site must not stop the run
            outcome = "fout"
            state_path = data_dir / "state" / f"{event['id']}.json"
            state = _read_json(state_path, {})
            state["laatste_fout"] = f"{today}: {e}"
            _write_json(state_path, state)
            print(f"FOUT {event['id']}: {e}", file=sys.stderr)
        results.setdefault(outcome, []).append(event["id"])
        print(f"{event['id']}: {outcome}")

    print("\nSamenvatting:")
    for outcome, ids in sorted(results.items()):
        print(f"  {outcome}: {len(ids)} ({', '.join(ids)})")
    return 0


if __name__ == "__main__":
    sys.exit(run())
