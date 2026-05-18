#!/usr/bin/env python3
"""Compare parse outputs to expected.json and update scorecard.csv."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"
RESULTS = ROOT / "results"


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip()[:10]


def normalize_time(value: str | None) -> str | None:
    if not value:
        return None
    m = re.match(r"(\d{1,2}):(\d{2})", str(value))
    if not m:
        return None
    return f"{int(m.group(1)):02d}:{m.group(2)}"


def normalize_price(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    s = re.sub(r"[^\d.]", "", str(value))
    return round(float(s), 2) if s else None


def field_match(expected, actual, key: str, normalizers: dict | None = None) -> bool:
    normalizers = normalizers or {}
    ev, av = expected.get(key), actual.get(key)
    if ev is None and av is None:
        return True
    if normalizers.get(key):
        ev, av = normalizers[key](ev), normalizers[key](av)
    return ev == av


def score_case(case_dir: Path, parse_path: Path) -> dict:
    expected = json.loads((case_dir / "expected.json").read_text(encoding="utf-8"))
    actual = json.loads(parse_path.read_text(encoding="utf-8"))
    ticket_type = expected.get("ticket_type", case_dir.name.split("_")[-1])

    norms = {
        "show_date": normalize_date,
        "show_time": normalize_time,
        "price": normalize_price,
    }

    core_keys = ["movie_title", "show_date", "hall_name", "price"]
    core_ok = all(field_match(expected, actual, k, norms) for k in core_keys if k in expected)

    electronic_extra_ok = "n/a"
    if ticket_type == "electronic":
        electronic_extra_ok = (
            "yes"
            if all(
                field_match(expected, actual, k, norms)
                for k in ("show_time", "payment_status")
                if k in expected
            )
            else "no"
        )

    paper_seat_ok = "n/a"
    if ticket_type == "paper":
        paper_seat_ok = "yes" if field_match(expected, actual, "seat_info", norms) else "no"

    missing = set(actual.get("missing_fields") or [])
    hallucination = False
    for k, v in actual.items():
        if k in ("confidence", "missing_fields"):
            continue
        if v is not None and k in missing:
            hallucination = True

    return {
        "core_fields_ok": "yes" if core_ok else "no",
        "electronic_extra_ok": electronic_extra_ok if electronic_extra_ok != "n/a" else "n/a",
        "paper_seat_ok": paper_seat_ok if paper_seat_ok != "n/a" else "n/a",
        "hallucination": "yes" if hallucination else "no",
    }


def main() -> None:
    rows = []
    header = [
        "case_id",
        "ticket_type",
        "core_fields_ok",
        "electronic_extra_ok",
        "paper_seat_ok",
        "hallucination",
        "parse_seconds",
        "notes",
    ]

    for case_dir in sorted(CASES.iterdir()):
        if not case_dir.is_dir():
            continue
        case_id = case_dir.name
        ticket_type = "electronic" if "electronic" in case_id else "paper"
        parse_path = RESULTS / f"{case_id}_parse.json"
        row = {
            "case_id": case_id,
            "ticket_type": ticket_type,
            "core_fields_ok": "pending",
            "electronic_extra_ok": "n/a" if ticket_type == "paper" else "pending",
            "paper_seat_ok": "n/a" if ticket_type == "electronic" else "pending",
            "hallucination": "pending",
            "parse_seconds": "",
            "notes": "",
        }
        if parse_path.exists():
            scored = score_case(case_dir, parse_path)
            row.update(scored)
            row["notes"] = "auto-scored"
        rows.append(row)

    with (RESULTS / "scorecard.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {RESULTS / 'scorecard.csv'}")


if __name__ == "__main__":
    main()
