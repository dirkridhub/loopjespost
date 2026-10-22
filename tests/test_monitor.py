import json
from pathlib import Path

import pytest

from loopjespost.extract import fingerprint, main_text
from loopjespost.monitor import check_event

FIXTURES = Path(__file__).parent / "fixtures" / "stuwwalloop"
HOME = (FIXTURES / "home.html").read_text(encoding="utf-8")
HOME_2027 = (FIXTURES / "home_2027_aangekondigd.html").read_text(encoding="utf-8")

EVENT = {
    "id": "stuwwalloop",
    "naam": "Stuwwalloop",
    "plaats": "Oosterbeek",
    "provincie": "Gelderland",
    "website": "https://www.stuwwalloop.nl/",
}


def field(waarde, zekerheid="hoog", bron_zin=""):
    return {"waarde": waarde, "zekerheid": zekerheid, "bron_zin": bron_zin}


UNKNOWN_RESULT = {
    "datum_loopje": field("", "laag"),
    "inschrijving_status": field("onbekend", "laag"),
    "inschrijving_opent_datum": field("", "laag"),
    "inschrijving_opent_tijd": field("", "laag"),
}

ANNOUNCED_RESULT = {
    "datum_loopje": field("2027-05-29", "hoog", "2027 zaterdag 29 mei"),
    "inschrijving_status": field("nog_niet_open", "hoog",
                                 "De inschrijving opent op dinsdag 1 december 2026 om 20:00 uur."),
    "inschrijving_opent_datum": field("2026-12-01", "hoog",
                                      "De inschrijving opent op dinsdag 1 december 2026 om 20:00 uur."),
    "inschrijving_opent_tijd": field("20:00", "hoog",
                                     "De inschrijving opent op dinsdag 1 december 2026 om 20:00 uur."),
}


class FakeAI:
    def __init__(self, *results):
        self.results = list(results)
        self.calls = 0

    def __call__(self, text, name, today):
        self.calls += 1
        return self.results.pop(0), {"input_tokens": 1000, "output_tokens": 100}


class FakeIssues:
    def __init__(self):
        self.opened = []

    def __call__(self, title, body):
        self.opened.append((title, body))
        return f"https://github.com/example/issues/{len(self.opened)}"


def run(tmp_path, html, ai, issues=None, today="2026-10-16"):
    return check_event(
        EVENT,
        fetch=lambda url: html,
        read=ai,
        open_issue=issues or FakeIssues(),
        data_dir=tmp_path,
        today=today,
    )


def state(tmp_path):
    return json.loads((tmp_path / "state" / "stuwwalloop.json").read_text(encoding="utf-8"))


def test_main_text_drops_menu_but_keeps_content():
    text = main_text(HOME)
    assert "2026 zaterdag 30 mei" in text
    assert "Vrijwilliger worden" not in text  # menu item
    assert "Kom je ook helpen als vrijwilliger" in text  # body text


def test_fingerprint_is_stable():
    assert fingerprint(main_text(HOME)) == fingerprint(main_text(HOME))
    assert fingerprint(main_text(HOME)) != fingerprint(main_text(HOME_2027))


def test_unchanged_page_skips_ai(tmp_path):
    ai = FakeAI(UNKNOWN_RESULT)
    assert run(tmp_path, HOME, ai) == "eerste meting"
    assert run(tmp_path, HOME, ai, today="2026-10-17") == "ongewijzigd"
    assert ai.calls == 1
    assert state(tmp_path)["gecontroleerd_op"] == "2026-10-17"


def test_simulated_announcement_creates_change_event(tmp_path):
    ai = FakeAI(UNKNOWN_RESULT, ANNOUNCED_RESULT)
    run(tmp_path, HOME, ai)
    assert run(tmp_path, HOME_2027, ai, today="2026-10-17") == "gewijzigd"

    changes = json.loads((tmp_path / "changes" / "2026-10-17-stuwwalloop.json").read_text(encoding="utf-8"))
    assert len(changes) == 1
    by_field = {c["veld"]: c for c in changes[0]["wijzigingen"]}
    assert by_field["datum_loopje"]["oud"] == ""
    assert by_field["datum_loopje"]["nieuw"] == "2027-05-29"
    assert by_field["inschrijving_status"]["oud"] == "onbekend"
    assert by_field["inschrijving_status"]["nieuw"] == "nog_niet_open"
    assert by_field["inschrijving_opent_datum"]["nieuw"] == "2026-12-01"
    assert by_field["inschrijving_opent_tijd"]["nieuw"] == "20:00"
    assert by_field["inschrijving_opent_tijd"]["bron_url"] == "https://www.stuwwalloop.nl/"

    assert state(tmp_path)["status"]["inschrijving_opent_datum"]["waarde"] == "2026-12-01"


def test_low_confidence_opens_issue_and_publishes_nothing(tmp_path):
    unsure = dict(ANNOUNCED_RESULT, inschrijving_opent_datum=field(
        "2026-12-01", "laag", "De inschrijving opent op dinsdag 1 december 2026 om 20:00 uur."))
    ai, issues = FakeAI(UNKNOWN_RESULT, unsure), FakeIssues()
    run(tmp_path, HOME, ai, issues)
    assert run(tmp_path, HOME_2027, ai, issues, today="2026-10-17") == "controleren"

    assert len(issues.opened) == 1
    title, body = issues.opened[0]
    assert title == "Controleren: Stuwwalloop"
    assert "(twijfel)" in body and "2026-12-01" in body
    assert not (tmp_path / "changes").exists()
    s = state(tmp_path)
    assert s["status"]["inschrijving_opent_datum"]["waarde"] == ""  # old value kept
    assert s["wacht_op_controle"] == "https://github.com/example/issues/1"

    # Same page next day: no second AI call and no duplicate issue.
    assert run(tmp_path, HOME_2027, ai, issues, today="2026-10-18") == "ongewijzigd"
    assert len(issues.opened) == 1


def test_quote_not_on_page_counts_as_low_confidence(tmp_path):
    invented = dict(ANNOUNCED_RESULT, datum_loopje=field("2027-05-29", "hoog", "Het loopje is op 29 mei 2027"))
    issues = FakeIssues()
    run(tmp_path, HOME, FakeAI(UNKNOWN_RESULT), issues)
    assert run(tmp_path, HOME_2027, FakeAI(invented), issues, today="2026-10-17") == "controleren"
    assert "bronzin staat niet letterlijk op de pagina" in issues.opened[0][1]


def test_costs_are_recorded_per_month(tmp_path):
    ai = FakeAI(UNKNOWN_RESULT, ANNOUNCED_RESULT)
    run(tmp_path, HOME, ai)
    run(tmp_path, HOME_2027, ai, today="2026-10-17")
    costs = json.loads((tmp_path / "costs" / "2026-10.json").read_text(encoding="utf-8"))
    assert costs["ai_aanroepen"] == 2
    assert costs["kosten_usd"] == pytest.approx(2 * (1000 * 1 + 100 * 5) / 1_000_000)


# Cases seen in the first real runs (October 2026).

from loopjespost.monitor import finalize, merge, review  # noqa: E402

PAGE = {"https://example.nl/": (
    "Op zondag 27 december 2026 organiseert atletiekvereniging Ciko’66 de loop. "
    "We hopen jullie volgend jaar aan de start te zien. Februariloop 2027. "
    "De Ehrmann Posbankloop ZONDAG 27 SEPTEMBER 2026. 6K en 15K uitverkocht."
)}


def reviewed(**fields):
    base = {name: field("", "laag") for name in UNKNOWN_RESULT}
    base["inschrijving_status"] = field("onbekend", "laag")
    base.update(fields)
    return review(base, PAGE, today="2026-10-18")


def test_typographic_apostrophe_still_matches():
    out = reviewed(datum_loopje=field("2026-12-27", "hoog",
                                      "Op zondag 27 december 2026 organiseert atletiekvereniging Ciko'66 de loop."))
    assert out["datum_loopje"]["zekerheid"] == "hoog"


def test_date_built_from_vague_text_is_low():
    out = reviewed(datum_loopje=field("2027-06-27", "middel", "We hopen jullie volgend jaar aan de start te zien."))
    assert out["datum_loopje"]["zekerheid"] == "laag"
    assert out["datum_loopje"]["reden"] == "datum staat niet in de bronzin"


def test_impossible_date_is_low():
    out = reviewed(datum_loopje=field("2027-02-00", "middel", "Februariloop 2027"))
    assert out["datum_loopje"]["reden"] == "geen geldige datum"


def test_past_edition_means_next_edition_unknown():
    out = finalize(reviewed(
        datum_loopje=field("2026-09-27", "hoog", "De Ehrmann Posbankloop ZONDAG 27 SEPTEMBER 2026"),
        inschrijving_status=field("vol", "hoog", "6K en 15K uitverkocht."),
    ), today="2026-10-18")
    assert out["datum_loopje"]["waarde"] == ""
    assert out["inschrijving_status"]["waarde"] == "onbekend"
    assert all(f["zekerheid"] == "hoog" for f in out.values())
    assert out["datum_loopje"]["reden"] == "vorige editie (2026-09-27)"


def test_status_without_race_date_is_not_published():
    out = finalize(reviewed(inschrijving_status=field("vol", "hoog", "6K en 15K uitverkocht.")), "2026-10-18")
    assert out["inschrijving_status"]["waarde"] == "onbekend"
    assert out["inschrijving_status"]["reden"] == "status zonder datum van het loopje"


def test_value_the_ai_missed_this_time_is_kept():
    previous = dict(ANNOUNCED_RESULT)
    now = dict(ANNOUNCED_RESULT, inschrijving_status=field("onbekend", "laag"))
    assert merge(now, previous)["inschrijving_status"]["waarde"] == "nog_niet_open"


def test_countdown_and_block_order_do_not_count_as_change():
    a = "Lingezegen Marathon 134 dagen 17 uren 26 minuten 09 seconden tot het startschot. Volg ons."
    b = "Volg ons. Lingezegen Marathon 133 dagen 2 uren 1 minuten 44 seconden tot het startschot."
    assert fingerprint(a) == fingerprint(b)
    assert fingerprint(a) != fingerprint(a.replace("Marathon", "Marathon uitverkocht"))


class FakeResolve:
    def __init__(self):
        self.closed = []

    def __call__(self, title, comment):
        self.closed.append(title)
        return 1


def test_one_issue_per_race_and_closed_when_resolved(tmp_path):
    unsure = dict(ANNOUNCED_RESULT, datum_loopje=field("2027-05-29", "hoog", "niet op de pagina"))
    issues, resolve = FakeIssues(), FakeResolve()

    def go(html, result, today):
        return check_event(EVENT, fetch=lambda url: html, read=FakeAI(result), open_issue=issues,
                           resolve_issues=resolve, data_dir=tmp_path, today=today)

    assert go(HOME, unsure, "2026-10-16") == "controleren"
    assert go(HOME_2027, unsure, "2026-10-17") == "controleren"  # page changed, still unsure
    assert len(issues.opened) == 1

    assert go(HOME_2027 + "<p>Nieuw blok</p>", ANNOUNCED_RESULT, "2026-10-18") == "eerste meting"
    assert resolve.closed == ["Controleren: Stuwwalloop"]
    assert "wacht_op_controle" not in state(tmp_path)
