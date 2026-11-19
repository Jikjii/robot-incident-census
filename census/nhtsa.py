"""Pull NHTSA Standing General Order crash reports for automated driving systems (ADS).

Only the ADS file is read; Level 2 driver-assistance reports live in a separate file and are out of scope.
The pull writes candidates to data/candidates/nhtsa.csv for a person to review. A report is the
operator's own account, not a finding, so nothing here goes into data/incidents.csv without checking.
To protect the people involved, the candidate file keeps no narrative, VIN, address or coordinates,
only identifiers, months, place, the reported injury level and a link to the public data file.
"""

from __future__ import annotations

import csv
import io
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

DATA_URL = "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADS.csv"
DEFAULT_OUT = Path("data/candidates/nhtsa.csv")
MONTHS = {m: i for i, m in enumerate(
    ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), start=1)}

# Candidate column -> column in NHTSA's file.
FIELDS = {
    "report_id": "Report ID",
    "report_version": "Report Version",
    "submitted": "Report Submission Date",
    "incident_month": "Incident Date",
    "reporting_entity": "Reporting Entity",
    "operating_entity": "Operating Entity",
    "make": "Make",
    "model": "Model",
    "city": "City",
    "state": "State",
    "operator_type": "Driver / Operator Type",
    "engagement": "Engagement Status",
    "crash_with": "Crash With",
    "highest_injury": "Highest Injury Severity Alleged",
}
COLUMNS = [*FIELDS, "url"]

Fetch = Callable[[str], str]


def http_fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "robot-incident-census"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")


def month(value: str | None) -> str:
    """Turn NHTSA's MON-YYYY (for example SEP-2026) into YYYY-MM; return '' when absent or malformed."""
    parts = (value or "").strip().upper().split("-")
    if len(parts) == 2 and parts[0] in MONTHS and parts[1].isdigit() and len(parts[1]) == 4:
        return f"{parts[1]}-{MONTHS[parts[0]]:02d}"
    return ""


def version(row: dict[str, str]) -> int:
    try:
        return int(row.get("report_version") or 0)
    except ValueError:
        return 0


def to_candidate(record: dict[str, str]) -> dict[str, str]:
    """Keep identifiers, months and place only; narrative and identifying fields are deliberately dropped."""
    row = {column: (record.get(source) or "").strip() for column, source in FIELDS.items()}
    row["submitted"] = month(row["submitted"])
    row["incident_month"] = month(row["incident_month"])
    row["url"] = DATA_URL
    return row


def parse(text: str, since_month: str, until_month: str) -> list[dict[str, str]]:
    """Return the latest version of each report submitted in the window (months as YYYY-MM, inclusive)."""
    latest: dict[str, dict[str, str]] = {}
    for record in csv.DictReader(io.StringIO(text)):
        row = to_candidate(record)
        if not row["report_id"] or not row["submitted"]:
            continue
        if not since_month <= row["submitted"] <= until_month:
            continue
        current = latest.get(row["report_id"])
        if current is None or version(row) >= version(current):
            latest[row["report_id"]] = row
    return list(latest.values())


def pull(since: date, until: date, fetch: Fetch = http_fetch) -> list[dict[str, str]]:
    return parse(fetch(DATA_URL), f"{since:%Y-%m}", f"{until:%Y-%m}")


def merge(existing: list[dict[str, str]], new: list[dict[str, str]]) -> list[dict[str, str]]:
    """Combine without duplicates (the higher report version wins) and sort newest first."""
    by_id = {row["report_id"]: row for row in existing}
    for row in new:
        current = by_id.get(row["report_id"])
        if current is None or version(row) >= version(current):
            by_id[row["report_id"]] = row
    return sorted(by_id.values(), key=lambda r: (r["submitted"], r["report_id"]), reverse=True)


def read_candidates(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as handle:
        return [{c: row.get(c, "") for c in COLUMNS} for row in csv.DictReader(handle)]


def write_candidates(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


USAGE = "usage: python -m census nhtsa [--days N | --since YYYY-MM-DD] [--until YYYY-MM-DD] [--out PATH]"


def main(argv: list[str] | None = None, fetch: Fetch = http_fetch, today: date | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    today = today or date.today()
    options = {"--days": "60", "--since": "", "--until": "", "--out": str(DEFAULT_OUT)}
    while args:
        flag = args.pop(0)
        if flag not in options or not args:
            print(USAGE, file=sys.stderr)
            return 2
        options[flag] = args.pop(0)
    try:
        until = date.fromisoformat(options["--until"]) if options["--until"] else today
        since = (date.fromisoformat(options["--since"]) if options["--since"]
                 else until - timedelta(days=int(options["--days"])))
    except ValueError as exc:
        print(f"{exc}\n{USAGE}", file=sys.stderr)
        return 2
    if since > until:
        print("--since is after --until", file=sys.stderr)
        return 2
    out = Path(options["--out"])
    new = pull(since, until, fetch)
    existing = read_candidates(out)
    rows = merge(existing, new)
    write_candidates(out, rows)
    added = len(rows) - len(existing)
    print(f"NHTSA SGO (ADS) submitted {since:%Y-%m}..{until:%Y-%m}: {len(new)} report(s), {added} new; "
          f"{len(rows)} in {out}")
    return 0
