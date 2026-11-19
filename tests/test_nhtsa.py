import csv
import io
from datetime import date

from census import nhtsa

HEADER = [
    "Report ID", "Report Version", "Reporting Entity", "Report Submission Date", "VIN", "Make", "Model",
    "Driver / Operator Type", "Engagement Status", "Operating Entity", "Incident Date", "Address", "City",
    "State", "Latitude", "Crash With", "Highest Injury Severity Alleged", "Narrative",
]


def record(report_id, submitted="SEP-2026", version="1", injury="Property Damage. No Injured Reported"):
    return {
        "Report ID": report_id, "Report Version": version, "Reporting Entity": "Example AV, Inc.",
        "Report Submission Date": submitted, "VIN": "VIN-MUST-NOT-BE-KEPT", "Make": "EXAMPLE",
        "Model": "Robotaxi", "Driver / Operator Type": "None", "Engagement Status": "Verified Engaged",
        "Operating Entity": "Example AV, Inc.", "Incident Date": "AUG-2026",
        "Address": "ADDRESS-MUST-NOT-BE-KEPT", "City": "Austin", "State": "TX", "Latitude": "30.1",
        "Crash With": "SUV", "Highest Injury Severity Alleged": injury,
        "Narrative": "NARRATIVE THAT MUST NOT BE KEPT",
    }


def csv_text(records):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=HEADER)
    writer.writeheader()
    writer.writerows(records)
    return buffer.getvalue()


def test_month_parsing():
    assert nhtsa.month("SEP-2026") == "2026-09"
    assert nhtsa.month("jan-2025") == "2025-01"
    for bad in (None, "", "2026-09", "SEPT-2026", "SEP-26"):
        assert nhtsa.month(bad) == ""


def test_candidate_drops_narrative_and_identifying_fields():
    row = nhtsa.to_candidate(record("1-1"))
    assert list(row) == nhtsa.COLUMNS
    assert row["submitted"] == "2026-09"
    assert row["incident_month"] == "2026-08"
    assert row["url"] == nhtsa.DATA_URL
    kept = " ".join(row.values())
    assert "MUST NOT BE KEPT" not in kept and "VIN" not in kept and "30.1" not in kept


def test_parse_keeps_window_and_latest_version():
    text = csv_text([
        record("1-1", "JUN-2026"),
        record("2-2", "AUG-2026", version="1"),
        record("2-2", "SEP-2026", version="2", injury="Minor W/O Hospitalization"),
        record("3-3", "OCT-2026"),
        record("", "SEP-2026"),
    ])
    rows = nhtsa.parse(text, "2026-08", "2026-09")
    assert [r["report_id"] for r in rows] == ["2-2"]
    assert rows[0]["report_version"] == "2"
    assert rows[0]["highest_injury"] == "Minor W/O Hospitalization"


def test_pull_reads_only_the_ads_file():
    calls = []

    def fetch(url):
        calls.append(url)
        return csv_text([record("1-1")])

    rows = nhtsa.pull(date(2026, 9, 1), date(2026, 10, 1), fetch)
    assert calls == [nhtsa.DATA_URL] and "ADS" in calls[0]
    assert len(rows) == 1


def test_main_merges_without_duplicates(tmp_path):
    out = tmp_path / "candidates" / "nhtsa.csv"
    fetch = lambda url: csv_text([record("1-1", "AUG-2026"), record("2-2", "SEP-2026")])
    assert nhtsa.main(["--days", "60", "--out", str(out)], fetch, today=date(2026, 10, 21)) == 0
    fetch = lambda url: csv_text([record("2-2", "SEP-2026", version="2"), record("3-3", "OCT-2026")])
    assert nhtsa.main(["--since", "2026-09-01", "--out", str(out)], fetch, today=date(2026, 10, 21)) == 0
    with open(out, newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["report_id"] for r in rows] == ["3-3", "2-2", "1-1"]
    assert rows[1]["report_version"] == "2"


def test_main_rejects_bad_arguments(tmp_path):
    out = str(tmp_path / "x.csv")
    assert nhtsa.main(["--bogus", "1"], lambda u: "", today=date(2026, 10, 21)) == 2
    assert nhtsa.main(["--since", "2026-10-30", "--out", out], lambda u: "", today=date(2026, 10, 21)) == 2
