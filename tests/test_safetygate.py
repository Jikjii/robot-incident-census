import csv
from datetime import date
from urllib.parse import parse_qs, urlparse

from census import safetygate


def alert(alert_id, name, specific="", brand="", published="2026-10-20T15:08:17.752+00:00"):
    return {
        "id": alert_id, "reference": f"SR/{alert_id:05d}/26", "publicationDate": published,
        "product": {"name": name, "nameSpecific": specific, "brands": [{"brand": brand}] if brand else []},
        "risk": {"riskType": [{"name": "INJURIES"}]},
    }


def detail(category="OTHER", description="The robot arm may move unexpectedly."):
    return {
        "country": {"name": "Germany"},
        "product": {"productCategory": {"name": category}},
        "risk": {"riskType": [{"name": "INJURIES"}, {"name": "CUTS"}],
                 "versions": [{"language": {"key": "DE"}, "riskDescription": "Deutsch"},
                              {"language": {"key": "EN"}, "riskDescription": description + "\n  More."}]},
    }


class FakeApi:
    """Two weekly reports in October 2026 (one outside the window), alerts paged two at a time."""

    def __init__(self):
        self.calls = []
        self.alerts = {
            "11": [alert(1, "Robotic lawn mower"), alert(2, "Glass mug"), alert(3, "Vacuum", "X1 Robot"),
                   alert(4, "Bath toy", "Robot Fish")],
            "12": [alert(5, "Industrial robot arm")],
        }
        self.details = {1: detail(), 3: detail(description="Charger overheats."), 4: detail("TOYS"),
                        5: detail()}

    def __call__(self, method, url, body):
        self.calls.append((method, url, body))
        path = urlparse(url).path
        if path.endswith("webreport/all"):
            assert method == "POST" and body["language"] == "en"
            if (body["year"], body["month"]) != (2026, 10):
                return {"content": [], "last": True}
            return {"content": [
                {"id": 11, "code": "Report-2026-42", "publicationDate": "2026-10-22T22:00:00.000+00:00"},
                {"id": 12, "code": "Report-2026-39", "publicationDate": "2026-10-01T22:00:00.000+00:00"},
            ], "last": True}
        if path.endswith("webreport/notifications"):
            query = parse_qs(urlparse(url).query)
            report = query["search"][0].split("|:|")[1]
            page = int(query["page"][0])
            items = self.alerts[report][page * 2:page * 2 + 2]
            return {"content": items, "last": page * 2 + 2 >= len(self.alerts[report])}
        alert_id = int(path.rsplit("/", 1)[1])
        return self.details[alert_id]


def test_robot_keyword_match():
    assert safetygate.is_robot(alert(1, "Robotic lawn mower"))
    assert safetygate.is_robot(alert(1, "Vacuum cleaner", "Robot vacuum S8"))
    assert safetygate.is_robot(alert(1, "Mobile platform", brand="ACME Cobot"))
    assert safetygate.is_robot(alert(1, "Automated guided vehicle"))
    assert not safetygate.is_robot(alert(1, "Glass mug"))
    assert not safetygate.is_robot(alert(1, "Charger", "Laptop charger"))


def test_months_cross_year():
    assert safetygate.months(date(2025, 11, 20), date(2026, 2, 1)) == [(2025, 11), (2025, 12), (2026, 1), (2026, 2)]


def test_pull_filters_window_keywords_and_toys():
    api = FakeApi()
    rows = safetygate.pull(date(2026, 10, 10), date(2026, 10, 31), api)
    assert [r["reference"] for r in rows] == ["SR/00001/26", "SR/00003/26"]
    first = rows[0]
    assert first["weekly_report"] == "Report-2026-42"
    assert first["published"] == "2026-10-20"
    assert first["country"] == "Germany"
    assert first["risk_types"] == "INJURIES; CUTS"
    assert first["risk_description"] == "The robot arm may move unexpectedly. More."
    assert first["url"] == "https://ec.europa.eu/safety-gate-alerts/screen/webReport/alertDetail/1"
    # The report outside the window is never paged, and only matching alerts get a detail call.
    detail_calls = [u for _, u, _ in api.calls if "/notification/" in u]
    assert len(detail_calls) == 3
    assert not any("WEB_REPORT%7C%3A%7C12" in u for _, u, _ in api.calls)


def test_main_writes_and_merges(tmp_path):
    out = tmp_path / "eu_safety_gate.csv"
    args = ["--since", "2026-10-10", "--until", "2026-10-31", "--out", str(out)]
    assert safetygate.main(args, fetch=FakeApi()) == 0
    assert safetygate.main(args, fetch=FakeApi()) == 0  # a second run adds no duplicates
    with open(out, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == safetygate.COLUMNS
        assert len(list(reader)) == 2


def test_main_rejects_bad_options(tmp_path):
    assert safetygate.main(["--since"], fetch=FakeApi()) == 2
    assert safetygate.main(["--since", "2026-11-01", "--until", "2026-10-01"], fetch=FakeApi()) == 2
    assert safetygate.main(["--bogus", "1"], fetch=FakeApi()) == 2
