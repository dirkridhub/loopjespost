from pathlib import Path

import pytest
import yaml

from loopjespost.events import EventError, load_events, validate

ROOT = Path(__file__).resolve().parent.parent


def make(**overrides):
    data = {
        "id": "testloop",
        "naam": "Testloop",
        "plaats": "Arnhem",
        "provincie": "Gelderland",
        "website": "https://example.nl",
    }
    data.update(overrides)
    return data


def test_all_event_files_are_valid():
    load_events(ROOT / "events")


def test_example_file_is_valid_apart_from_its_name():
    data = yaml.safe_load((ROOT / "events" / "_voorbeeld.yaml").read_text(encoding="utf-8"))
    validate(data, Path("voorbeeldloop.yaml"))


@pytest.mark.parametrize("overrides, message", [
    ({"naam": ""}, "naam"),
    ({"id": "Test Loop"}, "kleine letters"),
    ({"website": "example.nl"}, "http"),
    ({"datum_loopje": "30 mei"}, "datum"),
    ({"inschrijving": {"status": "misschien"}}, "status"),
    ({"inschrijving": {"opent_tijd": "8 uur"}}, "UU:MM"),
])
def test_invalid_events_give_a_clear_message(overrides, message):
    with pytest.raises(EventError, match=message):
        validate(make(**overrides), Path("testloop.yaml"))


def test_id_must_match_file_name():
    with pytest.raises(EventError, match="bestandsnaam"):
        validate(make(), Path("andere-naam.yaml"))
