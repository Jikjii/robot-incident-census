import csv
from pathlib import Path

from census import newcandidates

NHTSA = ["report_id", "report_version", "submitted", "incident_month", "reporting_entity", "operating_entity",
         "make", "model", "city", "state", "operator_type", "engagement", "crash_with", "highest_injury", "url"]


def write(path: Path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def nhtsa_row(report_id, city="Austin"):
    row = {c: "" for c in NHTSA}
    row.update(report_id=report_id, city=city, state="TX", operating_entity="Example AV",
               url=f"https://example.org/{report_id}")
    return row


def test_new_rows_are_those_whose_key_was_not_there_before(tmp_path):
    write(tmp_path / "old" / "nhtsa.csv", NHTSA, [nhtsa_row("1")])
    write(tmp_path / "new" / "nhtsa.csv", NHTSA, [nhtsa_row("1"), nhtsa_row("2")])
    columns, rows = newcandidates.new_rows(tmp_path / "old" / "nhtsa.csv", tmp_path / "new" / "nhtsa.csv")
    assert columns == NHTSA
    assert [r["report_id"] for r in rows] == ["2"]


def test_a_file_with_no_previous_copy_is_all_new(tmp_path):
    write(tmp_path / "new" / "nhtsa.csv", NHTSA, [nhtsa_row("1")])
    _, rows = newcandidates.new_rows(tmp_path / "old" / "nhtsa.csv", tmp_path / "new" / "nhtsa.csv")
    assert len(rows) == 1


def test_main_writes_an_issue_body_listing_new_rows(tmp_path, capsys):
    write(tmp_path / "old" / "nhtsa.csv", NHTSA, [nhtsa_row("1")])
    write(tmp_path / "new" / "nhtsa.csv", NHTSA, [nhtsa_row("1"), nhtsa_row("2", city="Dallas | TX")])
    out = tmp_path / "issue.md"
    assert newcandidates.main([str(tmp_path / "old"), str(tmp_path / "new"), "--out", str(out)]) == 0
    body = out.read_text()
    assert "## `nhtsa.csv`: 1 new" in body
    assert "| 2 |" in body and "Dallas \\| TX" in body
    assert "[open](https://example.org/2)" in body
    assert "https://example.org/1" not in body
    assert "1 new candidate(s)" in capsys.readouterr().out


def test_no_file_is_written_when_nothing_is_new_and_nothing_failed(tmp_path):
    write(tmp_path / "old" / "nhtsa.csv", NHTSA, [nhtsa_row("1")])
    write(tmp_path / "new" / "nhtsa.csv", NHTSA, [nhtsa_row("1")])
    out = tmp_path / "issue.md"
    out.write_text("stale")
    assert newcandidates.main([str(tmp_path / "old"), str(tmp_path / "new"), "--out", str(out)]) == 0
    assert not out.exists()


def test_failed_pulls_are_reported_even_with_no_new_rows(tmp_path):
    write(tmp_path / "old" / "nhtsa.csv", NHTSA, [nhtsa_row("1")])
    write(tmp_path / "new" / "nhtsa.csv", NHTSA, [nhtsa_row("1")])
    out = tmp_path / "issue.md"
    newcandidates.main([str(tmp_path / "old"), str(tmp_path / "new"), "--out", str(out), "--failed", "openfda"])
    assert "Pulls that failed this week: openfda." in out.read_text()


def test_long_lists_are_capped(tmp_path):
    rows = [nhtsa_row(str(n)) for n in range(newcandidates.MAX_ROWS_PER_FILE + 3)]
    write(tmp_path / "new" / "nhtsa.csv", NHTSA, rows)
    out = tmp_path / "issue.md"
    newcandidates.main([str(tmp_path / "old"), str(tmp_path / "new"), "--out", str(out)])
    assert "…and 3 more" in out.read_text()


def test_bad_arguments_print_usage(capsys):
    assert newcandidates.main(["only-one-dir"]) == 2
    assert "usage" in capsys.readouterr().err


def test_workflow_runs_every_pull_and_never_targets_main():
    workflow = (Path(__file__).parent.parent / ".github" / "workflows" / "weekly.yml").read_text()
    for pull in ("openfda", "nhtsa", "safetygate", "newcandidates"):
        assert f"python -m census {pull}" in workflow
    assert "git push origin census/next" in workflow
    assert "--force" not in workflow and "push origin main" not in workflow
    assert "gh issue create" in workflow
