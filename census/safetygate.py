"""Pull EU Safety Gate alerts for robots and automated machinery.

Safety Gate publishes a weekly report of alerts. The pull lists the weekly reports published in the
window, pages through each report's alerts, keeps the ones whose product name, specific name or brand
matches a robot keyword, and fetches each match's detail to add its category, notifying country, risk
types and the authority's risk description. Candidates go to data/candidates/eu_safety_gate.csv for a
person to review; many will be out of scope (for example a robot vacuum's charger or battery), so nothing
here goes into data/incidents.csv without checking. Safety Gate alerts describe products, not people, so
the risk description is kept.

The endpoints are the public ones the Safety Gate website itself calls (no key needed).
"""

from __future__ import annotations

import csv
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

API = "https://ec.europa.eu/safety-gate-alerts/public/api/"
ALERT_URL = "https://ec.europa.eu/safety-gate-alerts/screen/webReport/alertDetail/"
DEFAULT_OUT = Path("data/candidates/eu_safety_gate.csv")
MAX_PAGES = 100  # a weekly report holds a few hundred alerts at most; this only guards against loops

ROBOT_RE = re.compile(
    r"\brobot|\bcobot|\bautonomous\b|\bself[- ]driving\b|\bdriverless\b|\bAGV\b|\bAMR\b"
    r"|automated guided|automatic lawn ?mower|robotic",
    re.IGNORECASE,
)

# Toys shaped like robots are not robots in the methodology's sense.
EXCLUDED_CATEGORIES = {"TOYS"}

COLUMNS = [
    "reference", "published", "weekly_report", "country", "product", "product_specific", "brand",
    "category", "risk_types", "risk_description", "url",
]

# fetch(method, url, json_body_or_None) -> parsed JSON
Fetch = Callable[[str, str, Any], Any]


def http_fetch(method: str, url: str, body: Any = None) -> Any:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method, headers={
        "User-Agent": "robot-incident-census", "Accept": "application/json",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def day(value: str | None) -> str:
    """Return the YYYY-MM-DD part of an ISO timestamp, or '' when absent or malformed."""
    text = (value or "")[:10]
    try:
        date.fromisoformat(text)
    except ValueError:
        return ""
    return text


def months(since: date, until: date) -> list[tuple[int, int]]:
    result, current = [], date(since.year, since.month, 1)
    while current <= until:
        result.append((current.year, current.month))
        current = date(current.year + current.month // 12, current.month % 12 + 1, 1)
    return result


def paged(get_page: Callable[[int], Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for page in range(MAX_PAGES):
        payload = get_page(page) or {}
        items.extend(payload.get("content") or [])
        if payload.get("last", True) or not payload.get("content"):
            break
    return items


def weekly_reports(since: date, until: date, fetch: Fetch) -> list[dict[str, str]]:
    """Weekly reports published between since and until (inclusive), oldest first."""
    reports = {}
    for year, month in months(since, until):
        for report in paged(lambda page: fetch("POST", API + "webreport/all", {
                "year": year, "month": month, "language": "en", "page": str(page)})):
            published = day(report.get("publicationDate"))
            if report.get("id") and published and since.isoformat() <= published <= until.isoformat():
                reports[report["id"]] = {"id": str(report["id"]), "code": report.get("code") or "",
                                         "published": published}
    return sorted(reports.values(), key=lambda r: r["published"])


def report_alerts(report_id: str, fetch: Fetch) -> list[dict[str, Any]]:
    def get_page(page: int) -> Any:
        query = urllib.parse.urlencode({"language": "en", "page": page, "search": f"WEB_REPORT|:|{report_id}"})
        return fetch("GET", f"{API}webreport/notifications?{query}", None)
    return paged(get_page)


def brands(product: dict[str, Any]) -> str:
    return "; ".join(b.get("brand", "").strip() for b in product.get("brands") or [] if b.get("brand"))


def is_robot(alert: dict[str, Any]) -> bool:
    product = alert.get("product") or {}
    text = " ".join(str(product.get(k) or "") for k in ("name", "nameSpecific", "description"))
    return bool(ROBOT_RE.search(f"{text} {brands(product)}"))


def english(versions: list[dict[str, Any]] | None, field: str) -> str:
    versions = versions or []
    chosen = next((v for v in versions if (v.get("language") or {}).get("key") == "EN"), None)
    chosen = chosen or (versions[0] if versions else {})
    return " ".join(str(chosen.get(field) or "").split())


def to_candidate(alert: dict[str, Any], detail: dict[str, Any] | None, report_code: str) -> dict[str, str]:
    detail = detail or {}
    product = {**(alert.get("product") or {}), **(detail.get("product") or {})}
    risk = detail.get("risk") or alert.get("risk") or {}
    return {
        "reference": (alert.get("reference") or "").strip(),
        "published": day(alert.get("publicationDate")),
        "weekly_report": report_code,
        "country": ((detail.get("country") or {}).get("name") or "").strip(),
        "product": (product.get("name") or "").strip(),
        "product_specific": (product.get("nameSpecific") or "").strip(),
        "brand": brands(product),
        "category": ((product.get("productCategory") or {}).get("name") or "").strip(),
        "risk_types": "; ".join(r.get("name", "") for r in risk.get("riskType") or [] if r.get("name")),
        "risk_description": english(risk.get("versions"), "riskDescription"),
        "url": f"{ALERT_URL}{alert.get('id')}",
    }


def pull(since: date, until: date, fetch: Fetch = http_fetch) -> list[dict[str, str]]:
    rows = []
    for report in weekly_reports(since, until, fetch):
        for alert in report_alerts(report["id"], fetch):
            if alert.get("id") and is_robot(alert):
                detail = fetch("GET", f"{API}notification/{alert['id']}?language=en", None)
                row = to_candidate(alert, detail, report["code"])
                if row["category"] not in EXCLUDED_CATEGORIES:
                    rows.append(row)
    return rows


def merge(existing: list[dict[str, str]], new: list[dict[str, str]]) -> list[dict[str, str]]:
    """Combine without duplicates (a newer pull of the same alert wins) and sort newest first."""
    by_ref = {row["reference"]: row for row in existing}
    by_ref.update({row["reference"]: row for row in new})
    return sorted(by_ref.values(), key=lambda r: (r["published"], r["reference"]), reverse=True)


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


USAGE = "usage: python -m census safetygate [--days N | --since YYYY-MM-DD] [--until YYYY-MM-DD] [--out PATH]"


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
    print(f"EU Safety Gate weekly reports {since}..{until}: {len(new)} robot alert(s), {added} new; "
          f"{len(rows)} in {out}")
    return 0
