import csv
from datetime import date

import pytest

from census.validate import COLUMNS, main, validate_file, validate_rows

TODAY = date(2026, 10, 12)

GOOD = {
    "id": "RIC-2026-001",
    "date": "2026-03-14",
    "robot_type": "warehouse",
    "company": "Example Robotics",
    "location": "Columbus, Ohio, US",
    "summary": "An autonomous mobile robot reportedly struck a worker during a shift change.",
    "harm": "injury",
    "evidence": "unknown",
    "source_tier": "A",
    "sources": "https://example.gov/report/123 https://news.example.com/story",
    "added": "2026-10-12",
}


def errors_for(**changes):
    return validate_rows([{**GOOD, **changes}], TODAY)


def test_good_row_passes():
    assert errors_for() == []


def test_partial_dates_are_allowed():
    assert errors_for(date="2026-03") == []
    assert errors_for(date="2026") == []


@pytest.mark.parametrize(
    "changes, fragment",
    [
        ({"id": "RIC-26-1"}, "id must look like"),
        ({"id": "RIC-2025-001"}, "year in the id"),
        ({"date": "2026-13-01"}, "date"),
        ({"date": "2027-01-01", "id": "RIC-2027-001"}, "future"),
        ({"robot_type": "drone"}, "robot_type"),
        ({"harm": "minor"}, "harm"),
        ({"evidence": "maybe"}, "evidence"),
        ({"source_tier": "D"}, "source_tier"),
        ({"company": ""}, "company is empty"),
        ({"summary": "x" * 281}, "limit is 280"),
        ({"sources": ""}, "at least one source"),
        ({"sources": "http://example.com"}, "https"),
        ({"sources": "https://a.example https://a.example"}, "twice"),
        ({"added": "2026-10"}, "added must be"),
        ({"added": "2026-03-01"}, "earlier than the incident"),
        ({"added": "2026-12-01"}, "added is in the future"),
        ({"company": " Example"}, "spaces"),
    ],
)
def test_bad_rows_are_caught(changes, fragment):
    errors = errors_for(**changes)
    assert errors, f"{changes} passed"
    assert any(fragment in error for error in errors), errors


def test_duplicate_ids_are_caught():
    errors = validate_rows([GOOD, dict(GOOD)], TODAY)
    assert any("duplicate id" in error for error in errors)


def _write(path, rows, header=COLUMNS):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for row in rows:
            writer.writerow([row[c] for c in COLUMNS])


def test_shipped_data_file_is_valid():
    count, errors = validate_file("data/incidents.csv")
    assert errors == []
    assert count >= 0


def test_wrong_header_is_caught(tmp_path):
    path = tmp_path / "incidents.csv"
    _write(path, [], header=COLUMNS[:-1])
    _, errors = validate_file(path, TODAY)
    assert errors and "header" in errors[0]


def test_cli_exit_codes(tmp_path, capsys):
    good = tmp_path / "good.csv"
    _write(good, [GOOD])
    assert main([str(good)]) == 0
    assert capsys.readouterr().out.startswith("OK: 1 incident")

    bad = tmp_path / "bad.csv"
    _write(bad, [{**GOOD, "harm": "minor"}])
    assert main([str(bad)]) == 1
    assert "FAIL" in capsys.readouterr().out
