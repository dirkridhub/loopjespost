"""Load and validate the event files in events/."""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import yaml

STATUSES = {"nog_niet_open", "open", "vol", "onbekend"}
REQUIRED = ["id", "naam", "plaats", "provincie", "website"]


class EventError(ValueError):
    pass


def _check_date(value, field, path):
    if value in (None, ""):
        return
    if isinstance(value, dt.date):
        return
    raise EventError(f"{path.name}: '{field}' moet een datum zijn (JJJJ-MM-DD), niet '{value}'")


def validate(data: dict, path: Path) -> dict:
    if not isinstance(data, dict):
        raise EventError(f"{path.name}: bestand is leeg of geen geldige YAML")
    for field in REQUIRED:
        if not data.get(field):
            raise EventError(f"{path.name}: verplicht veld '{field}' ontbreekt")
    if not re.fullmatch(r"[a-z0-9-]+", str(data["id"])):
        raise EventError(f"{path.name}: 'id' mag alleen kleine letters, cijfers en '-' bevatten")
    if data["id"] != path.stem:
        raise EventError(f"{path.name}: 'id' ({data['id']}) moet gelijk zijn aan de bestandsnaam")
    for field in ("website", "inschrijfpagina"):
        url = data.get(field)
        if url and not str(url).startswith(("http://", "https://")):
            raise EventError(f"{path.name}: '{field}' moet met http:// of https:// beginnen")
    _check_date(data.get("datum_loopje"), "datum_loopje", path)

    reg = data.get("inschrijving") or {}
    status = reg.get("status") or "onbekend"
    if status not in STATUSES:
        raise EventError(f"{path.name}: status '{status}' is onbekend; kies uit {sorted(STATUSES)}")
    _check_date(reg.get("opent_datum"), "inschrijving.opent_datum", path)
    tijd = reg.get("opent_tijd")
    if tijd not in (None, "") and not re.fullmatch(r"\d{2}:\d{2}", str(tijd)):
        raise EventError(f"{path.name}: 'opent_tijd' moet UU:MM zijn, bijvoorbeeld \"20:00\"")
    return data


def load_events(events_dir: Path) -> list[dict]:
    events = []
    for path in sorted(events_dir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        with path.open(encoding="utf-8") as f:
            events.append(validate(yaml.safe_load(f), path))
    return events
