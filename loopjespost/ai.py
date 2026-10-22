"""Read race date and registration status from page text with Claude."""
from __future__ import annotations

import json

MODEL = "claude-haiku-4-5"
# USD per million tokens, used for the monthly cost overview.
PRICE_INPUT = 1.00
PRICE_OUTPUT = 5.00
MAX_TEXT_CHARS = 60_000

FIELDS = ["datum_loopje", "inschrijving_status", "inschrijving_opent_datum", "inschrijving_opent_tijd"]
CONFIDENCE = ["hoog", "middel", "laag"]


def _field(value_schema: dict) -> dict:
    return {
        "type": "object",
        "properties": {
            "waarde": value_schema,
            "zekerheid": {"type": "string", "enum": CONFIDENCE},
            "bron_zin": {"type": "string"},
        },
        "required": ["waarde", "zekerheid", "bron_zin"],
        "additionalProperties": False,
    }


SCHEMA = {
    "type": "object",
    "properties": {
        "datum_loopje": _field({"type": "string"}),
        "inschrijving_status": _field(
            {"type": "string", "enum": ["nog_niet_open", "open", "vol", "onbekend"]}
        ),
        "inschrijving_opent_datum": _field({"type": "string"}),
        "inschrijving_opent_tijd": _field({"type": "string"}),
    },
    "required": FIELDS,
    "additionalProperties": False,
}

SYSTEM = """You extract facts about a Dutch running race from the text of its own website.

Return, for the NEXT edition of the race (an edition on or after today's date):
- datum_loopje: race date as YYYY-MM-DD.
- inschrijving_status: nog_niet_open, open, vol (sold out or waiting list), or onbekend.
- inschrijving_opent_datum: date registration opens, YYYY-MM-DD.
- inschrijving_opent_tijd: time registration opens, HH:MM (24h, "00:00" for midnight).

Rules:
- Never guess. If the text does not state a value for the next edition, use "" (or "onbekend"
  for the status) with zekerheid "laag" and bron_zin "".
- Never construct a date. A date counts only if its day and month are written in the text.
  "Next year", "in the spring" or a weekday pattern is not a date: use "".
- Dates of past editions are not the next edition. A past date means the next date is unknown.
- The status is about the next edition too. "Vol" or "open" on a page about a past edition
  means the status is "onbekend".
- bron_zin must be copied word for word from the text: one short sentence or fragment (max 25 words)
  that contains the value (for dates: the day and month). Do not paraphrase, merge or reorder sentences.
- zekerheid: "hoog" if the text states it explicitly for the next edition, "middel" if only the
  year is implied (e.g. "zondag 27 december" on a page about the coming edition), "laag" if
  unclear or not stated."""


def read_status(text: str, race_name: str, today: str, client=None) -> tuple[dict, dict]:
    """Return (fields, usage). usage has input_tokens/output_tokens."""
    import anthropic

    if len(text) > MAX_TEXT_CHARS:
        raise ValueError(
            f"Paginatekst van {race_name} is {len(text)} tekens; te lang om veilig uit te lezen"
        )
    client = client or anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Today is {today}. Race: {race_name}.\n\nWebsite text:\n<text>\n{text}\n</text>",
        }],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"Onverwacht antwoord van de AI ({response.stop_reason}) voor {race_name}")
    raw = next(b.text for b in response.content if b.type == "text")
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return json.loads(raw), usage


def cost_usd(usage: dict) -> float:
    return (usage["input_tokens"] * PRICE_INPUT + usage["output_tokens"] * PRICE_OUTPUT) / 1_000_000
