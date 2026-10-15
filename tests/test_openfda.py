import csv
from datetime import date

from census import openfda


def report(key, received="20261001", event="Injury", code="NAY"):
    return {
        "mdr_report_key": key,
        "report_number": f"R{key}",
        "date_received": received,
        "date_of_event": "20260920",
        "event_type": event,
        "mdr_text": [{"text": "PATIENT NARRATIVE THAT MUST NOT BE KEPT"}],
        "patient": [{"patient_age": "50"}],
        "device": [{
            "manufacturer_d_name": "INTUITIVE SURGICAL, INC.",
            "brand_name": "DA VINCI XI",
            "device_report_product_code": code,
        }],
    }


def pager(reports, page_size=openfda.PAGE_SIZE):
    calls = []

    def fetch(url):
        calls.append(url)
        skip = int(url.rsplit("skip=", 1)[1])
        return {"meta": {"results": {"total": len(reports)}}, "results": reports[skip:skip + page_size]}

    return fetch, calls


def test_query_covers_codes_window_and_event_types():
    q = openfda.build_query(date(2026, 9, 1), date(2026, 10, 1))
    assert "device.device_report_product_code:(NAY)" in q
    assert "date_received:[20260901+TO+20261001]" in q
    assert "event_type:(Injury+Death)" in q
    url = openfda.build_url(q, skip=200)
    assert url.startswith(openfda.API + "?search=") and url.endswith("&limit=100&skip=200")
    assert " " not in url


def test_candidate_drops_narrative_and_patient_fields():
    row = openfda.to_candidate(report("123"))
    assert list(row) == openfda.COLUMNS
    assert row["date_received"] == "2026-10-01"
    assert row["date_of_event"] == "2026-09-20"
    assert row["url"].endswith("mdrfoi__id=123&pc=NAY")
    assert "NARRATIVE" not in " ".join(row.values())


def test_missing_or_bad_dates_become_empty():
    assert openfda.iso(None) == ""
    assert openfda.iso("2026") == ""


def test_pull_follows_pagination():
    reports = [report(str(i)) for i in range(250)]
    fetch, calls = pager(reports)
    rows = openfda.pull(date(2026, 9, 1), date(2026, 10, 1), fetch)
    assert len(rows) == 250
    assert len(calls) == 3


def test_pull_handles_no_results():
    rows = openfda.pull(date(2026, 9, 1), date(2026, 10, 1), lambda url: {"results": []})
    assert rows == []


def test_main_merges_without_duplicates(tmp_path):
    out = tmp_path / "candidates" / "openfda.csv"
    fetch, _ = pager([report("1", "20261001"), report("2", "20261005", event="Death")])
    assert openfda.main(["--days", "14", "--out", str(out)], fetch, today=date(2026, 10, 14)) == 0
    fetch, _ = pager([report("2", "20261005", event="Death"), report("3", "20261010")])
    assert openfda.main(["--since", "2026-10-01", "--out", str(out)], fetch, today=date(2026, 10, 14)) == 0
    with open(out, newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["mdr_report_key"] for r in rows] == ["3", "2", "1"]


def test_main_rejects_bad_arguments(tmp_path):
    out = str(tmp_path / "x.csv")
    assert openfda.main(["--bogus", "1"], lambda u: {}, today=date(2026, 10, 14)) == 2
    assert openfda.main(["--since", "2026-10-20", "--out", out], lambda u: {}, today=date(2026, 10, 14)) == 2
