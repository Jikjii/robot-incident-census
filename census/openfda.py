"""Pull FDA adverse event reports (MAUDE, via openFDA) for robot-assisted surgical systems.

The pull writes candidates to data/candidates/openfda.csv for a person to review. A report is an
allegation that a device may have been involved, not a finding, so nothing here goes into
data/incidents.csv without checking. To protect patients, the candidate file keeps no narrative text,
only the report's identifiers and a link to its public MAUDE page.
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Iterable

API = "https://api.fda.gov/device/event.json"
# NAY: "System, Surgical, Computer Controlled Instrument" (robot-assisted surgical systems such as da Vinci).
PRODUCT_CODES = ("NAY",)
# Malfunctions with no safety impact are out of scope, so only injury and death reports are pulled.
EVENT_TYPES = ("Injury", "Death")
PAGE_SIZE = 100
MAX_SKIP = 25000  # openFDA refuses skip values above this
DEFAULT_OUT = Path("data/candidates/openfda.csv")
MAUDE_URL = "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfmaude/detail.cfm?mdrfoi__id={key}&pc={code}"

COLUMNS = [
    "mdr_report_key", "report_number", "date_received", "date_of_event", "event_type",
    "manufacturer", "brand_name", "product_code", "url",
]

Fetch = Callable[[str], dict]


def build_query(since: date, until: date, product_codes: Iterable[str] = PRODUCT_CODES,
                event_types: Iterable[str] = EVENT_TYPES) -> str:
    """Return the openFDA search expression for reports received between two dates, inclusive."""
    codes = "+".join(product_codes)
    events = "+".join(event_types)
    return (
        f"device.device_report_product_code:({codes})"
        f"+AND+date_received:[{since:%Y%m%d}+TO+{until:%Y%m%d}]"
        f"+AND+event_type:({events})"
    )


def build_url(search: str, skip: int = 0, limit: int = PAGE_SIZE) -> str:
    # openFDA reads '+' as a space and needs ':', '[', ']', '(' and ')' unescaped.
    return f"{API}?search={urllib.parse.quote(search, safe='+:[]()')}&limit={limit}&skip={skip}"


def http_fetch(url: str) -> dict:
    """Fetch one page; a 404 from openFDA means no matching reports."""
    request = urllib.request.Request(url, headers={"User-Agent": "robot-incident-census"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"results": []}
        raise


def iso(value: str | None) -> str:
    """Turn openFDA's YYYYMMDD into YYYY-MM-DD; return '' when absent or malformed."""
    if value and len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return ""


def to_candidate(report: dict) -> dict[str, str]:
    """Keep identifiers and dates only; narrative and patient fields are deliberately dropped."""
    devices = report.get("device") or [{}]
    device = devices[0]
    key = str(report.get("mdr_report_key", "")).strip()
    code = (device.get("device_report_product_code") or "").strip()
    return {
        "mdr_report_key": key,
        "report_number": str(report.get("report_number", "")).strip(),
        "date_received": iso(report.get("date_received")),
        "date_of_event": iso(report.get("date_of_event")),
        "event_type": (report.get("event_type") or "").strip(),
        "manufacturer": (device.get("manufacturer_d_name") or "").strip(),
        "brand_name": (device.get("brand_name") or "").strip(),
        "product_code": code,
        "url": MAUDE_URL.format(key=urllib.parse.quote(key), code=urllib.parse.quote(code)) if key else "",
    }


def pull(since: date, until: date, fetch: Fetch = http_fetch) -> list[dict[str, str]]:
    """Return one candidate per report received in the window, following openFDA's pagination."""
    search = build_query(since, until)
    candidates: list[dict[str, str]] = []
    skip = 0
    while skip <= MAX_SKIP:
        page = fetch(build_url(search, skip))
        results = page.get("results") or []
        candidates.extend(to_candidate(r) for r in results)
        total = page.get("meta", {}).get("results", {}).get("total", len(results))
        skip += PAGE_SIZE
        if not results or skip >= total:
            break
    return [c for c in candidates if c["mdr_report_key"]]


def merge(existing: list[dict[str, str]], new: list[dict[str, str]]) -> list[dict[str, str]]:
    """Combine without duplicates (newer data wins) and sort newest first."""
    by_key = {row["mdr_report_key"]: row for row in existing}
    by_key.update({row["mdr_report_key"]: row for row in new})
    return sorted(by_key.values(), key=lambda r: (r["date_received"], r["mdr_report_key"]), reverse=True)


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


USAGE = "usage: python -m census openfda [--days N | --since YYYY-MM-DD] [--until YYYY-MM-DD] [--out PATH]"


def main(argv: list[str] | None = None, fetch: Fetch = http_fetch, today: date | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    today = today or date.today()
    options = {"--days": "30", "--since": "", "--until": "", "--out": str(DEFAULT_OUT)}
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
    print(f"openFDA {since}..{until}: {len(new)} report(s), {added} new; {len(rows)} in {out}")
    return 0
