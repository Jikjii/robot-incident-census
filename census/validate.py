"""Check data/incidents.csv against the schema described in README.md and METHODOLOGY.md."""

from __future__ import annotations

import csv
import re
import sys
from datetime import date
from pathlib import Path

COLUMNS = [
    "id", "date", "robot_type", "company", "location", "summary",
    "harm", "evidence", "source_tier", "sources", "added",
]
ROBOT_TYPES = {"surgical", "robotaxi", "warehouse", "industrial", "cobot", "humanoid", "delivery", "service", "other"}
HARM = {"fatality", "injury", "property", "near_miss", "none", "unknown"}
EVIDENCE = {"logs_public", "logs_cited", "logs_disputed", "logs_unavailable", "under_investigation", "unknown"}
SOURCE_TIERS = {"A", "B", "C"}
MAX_SUMMARY = 280

ID_RE = re.compile(r"^RIC-(\d{4})-(\d{3})$")
PARTIAL_DATE_RE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$")
FULL_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

DEFAULT_PATH = Path("data/incidents.csv")


def parse_partial_date(value: str) -> date:
    """Parse YYYY, YYYY-MM or YYYY-MM-DD and return the earliest day it could mean."""
    match = PARTIAL_DATE_RE.match(value)
    if not match:
        raise ValueError(f"'{value}' is not YYYY, YYYY-MM or YYYY-MM-DD")
    year, month, day = match.groups()
    return date(int(year), int(month or 1), int(day or 1))


def validate_rows(rows: list[dict[str, str]], today: date | None = None) -> list[str]:
    """Return one message per problem; an empty list means the data is valid."""
    today = today or date.today()
    errors: list[str] = []
    seen_ids: set[str] = set()

    for number, row in enumerate(rows, start=2):  # line 1 is the header
        label = f"line {number} ({row.get('id') or 'no id'})"

        def problem(message: str) -> None:
            errors.append(f"{label}: {message}")

        for column in COLUMNS:
            value = row.get(column)
            if value is None:
                problem(f"missing column {column}")
            elif value != value.strip():
                problem(f"{column} has leading or trailing spaces")
        if any(problem_value is None for problem_value in (row.get(c) for c in COLUMNS)):
            continue

        incident_id = row["id"]
        id_match = ID_RE.match(incident_id)
        if not id_match:
            problem("id must look like RIC-2026-001")
        elif incident_id in seen_ids:
            problem("duplicate id")
        seen_ids.add(incident_id)

        incident_date = None
        try:
            incident_date = parse_partial_date(row["date"])
            if incident_date > today:
                problem("date is in the future")
            if id_match and id_match.group(1) != row["date"][:4]:
                problem("the year in the id must match the incident year")
        except ValueError as exc:
            problem(f"date: {exc}")

        for column, allowed in (
            ("robot_type", ROBOT_TYPES),
            ("harm", HARM),
            ("evidence", EVIDENCE),
            ("source_tier", SOURCE_TIERS),
        ):
            if row[column] not in allowed:
                problem(f"{column} must be one of: {', '.join(sorted(allowed))}")

        for column in ("company", "location", "summary"):
            if not row[column]:
                problem(f"{column} is empty")
        if len(row["summary"]) > MAX_SUMMARY:
            problem(f"summary is {len(row['summary'])} characters; the limit is {MAX_SUMMARY}")
        if "\n" in row["summary"] or "\r" in row["summary"]:
            problem("summary must be one line")

        sources = row["sources"].split()
        if not sources:
            problem("at least one source is required")
        for source in sources:
            if not source.startswith("https://"):
                problem(f"source must be an https link: {source}")
        if len(set(sources)) != len(sources):
            problem("the same source is listed twice")

        if not FULL_DATE_RE.match(row["added"]):
            problem("added must be YYYY-MM-DD")
        else:
            try:
                added = date.fromisoformat(row["added"])
            except ValueError:
                problem("added is not a real date")
            else:
                if added > today:
                    problem("added is in the future")
                if incident_date and added < incident_date:
                    problem("added is earlier than the incident date")
    return errors


def validate_file(path: str | Path, today: date | None = None) -> tuple[int, list[str]]:
    """Return (number of incidents, problems)."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            return 0, [f"header must be exactly: {','.join(COLUMNS)}"]
        rows = list(reader)
    return len(rows), validate_rows(rows, today)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else DEFAULT_PATH
    count, errors = validate_file(path)
    if errors:
        for error in errors:
            print(error)
        print(f"FAIL: {len(errors)} problem(s) in {path}")
        return 1
    print(f"OK: {count} incident(s) in {path} pass every check")
    return 0
