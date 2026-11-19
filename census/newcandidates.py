"""List the candidates the weekly pulls added, as the body of a review issue.

The weekly GitHub Action copies data/candidates/ aside, runs the pulls, then calls

    python -m census newcandidates PREVIOUS_DIR CURRENT_DIR --out ISSUE.md [--failed NAME,NAME]

Each candidate file is keyed on its first column (MAUDE report key, SGO report ID, Safety Gate reference).
A row is new when its key was not in the previous copy of the same file. The issue body lists new rows per
file with the columns a reviewer needs and a link, plus any pulls that failed. The file is written only when
there is something to review (new rows or a failed pull), so the workflow opens an issue only then.
Candidates are leads, not incidents: nothing here goes into data/incidents.csv without checking.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

USAGE = "usage: python -m census newcandidates PREVIOUS_DIR CURRENT_DIR --out PATH [--failed NAME,NAME]"

# Columns shown in the issue for each known file; unknown files show their first four columns.
SHOWN = {
    "openfda.csv": ["date_received", "event_type", "manufacturer", "brand_name"],
    "nhtsa.csv": ["incident_month", "operating_entity", "city", "state", "highest_injury"],
    "eu_safety_gate.csv": ["published", "country", "product", "brand", "risk_types"],
}
MAX_ROWS_PER_FILE = 50  # keeps the issue readable; the rest are counted


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def new_rows(previous: Path, current: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Return (columns, rows in current whose first-column key is not in previous)."""
    columns, rows = read_rows(current)
    if not columns:
        return [], []
    _, old = read_rows(previous)
    key = columns[0]
    seen = {row.get(key, "") for row in old}
    return columns, [row for row in rows if row.get(key, "") not in seen]


def cell(value: str) -> str:
    return " ".join((value or "").split()).replace("|", "\\|")


def render(found: dict[str, tuple[list[str], list[dict[str, str]]]], failed: list[str]) -> str:
    total = sum(len(rows) for _, rows in found.values())
    lines = [f"The weekly pulls added {total} candidate(s). Candidates are leads, not incidents: check each "
             "against METHODOLOGY.md and open its sources before adding a row to `data/incidents.csv`.", ""]
    if failed:
        lines += [f"Pulls that failed this week: {', '.join(failed)}. See the workflow run log.", ""]
    for name, (columns, rows) in sorted(found.items()):
        if not rows:
            continue
        shown = [c for c in SHOWN.get(name, columns[1:5]) if c in columns]
        lines += [f"## `{name}`: {len(rows)} new", "",
                  "| " + " | ".join([columns[0], *shown, "link"]) + " |",
                  "|" + "---|" * (len(shown) + 2)]
        for row in rows[:MAX_ROWS_PER_FILE]:
            link = row.get("url", "")
            values = [cell(row.get(columns[0], "")), *(cell(row.get(c, "")) for c in shown),
                      f"[open]({link})" if link.startswith("https://") else ""]
            lines.append("| " + " | ".join(values) + " |")
        if len(rows) > MAX_ROWS_PER_FILE:
            lines.append(f"\n…and {len(rows) - MAX_ROWS_PER_FILE} more in `data/candidates/{name}`.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    options = {"--out": "", "--failed": ""}
    positional: list[str] = []
    while args:
        arg = args.pop(0)
        if arg in options:
            if not args:
                print(USAGE, file=sys.stderr)
                return 2
            options[arg] = args.pop(0)
        else:
            positional.append(arg)
    if len(positional) != 2 or not options["--out"]:
        print(USAGE, file=sys.stderr)
        return 2
    previous, current = (Path(p) for p in positional)
    failed = [name for name in options["--failed"].split(",") if name]
    found = {path.name: new_rows(previous / path.name, path) for path in sorted(current.glob("*.csv"))}
    total = sum(len(rows) for _, rows in found.values())
    out = Path(options["--out"])
    if total or failed:
        out.write_text(render(found, failed), encoding="utf-8")
    elif out.exists():
        out.unlink()
    print(f"{total} new candidate(s); {len(failed)} failed pull(s)")
    return 0
