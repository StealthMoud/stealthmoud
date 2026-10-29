from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from src.contributions import fetch_calendar, parse_calendar, render_calendar
import sync_profile


def calendar_html(total="123", days=365):
    start = date(2025, 10, 30)
    cells = "".join(
        f'<td data-date="{start + timedelta(days=i)}" data-level="{i % 5}"></td>'
        for i in range(days)
    )
    return (
        '<h2 id="js-contribution-activity-description">'
        f'{total} contributions in the last year</h2><table>{cells}</table>'
    )


PROFILE = (
    "authored introduction\n"
    + sync_profile.START + "\nPending maintenance\n" + sync_profile.END
    + "\nauthored projects and contact\n"
)


class DailyMaintenanceTests(unittest.TestCase):
    def test_next_day_updates_only_the_maintenance_block(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text(PROFILE)
            with patch.object(sync_profile, "ROOT", root), patch.object(
                sync_profile, "fetch_calendar", return_value=parse_calendar(calendar_html())
            ), patch.object(sync_profile, "today_in_rome") as today:
                today.return_value = date(2026, 10, 29)
                self.assertEqual(sync_profile.main(), 0)
                first = (root / "README.md").read_text()
                today.return_value = date(2026, 10, 30)
                self.assertEqual(sync_profile.main(), 0)
                second = (root / "README.md").read_text()
            self.assertIn("<strong>2026-10-29</strong>", first)
            self.assertIn("<strong>2026-10-30</strong>", second)
            for content in (first, second):
                self.assertTrue(content.startswith("authored introduction\n"))
                self.assertTrue(content.endswith("\nauthored projects and contact\n"))

    def test_missing_or_duplicate_markers_fail_without_fetching(self):
        for invalid in ("authored profile", PROFILE + sync_profile.START):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                (root / "README.md").write_text(invalid)
                with patch.object(sync_profile, "ROOT", root), patch.object(
                    sync_profile, "fetch_calendar"
                ) as fetch:
                    self.assertEqual(sync_profile.main(), 1)
                    fetch.assert_not_called()
                self.assertEqual((root / "README.md").read_text(), invalid)

    def test_future_date_fails_without_backdating(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            content = PROFILE.replace("Pending maintenance", "Automated maintenance: <strong>2026-10-30</strong>")
            (root / "README.md").write_text(content)
            with patch.object(sync_profile, "ROOT", root), patch.object(
                sync_profile, "today_in_rome", return_value=date(2026, 10, 29)
            ), patch.object(sync_profile, "fetch_calendar") as fetch:
                self.assertEqual(sync_profile.main(), 1)
                fetch.assert_not_called()
            self.assertEqual((root / "README.md").read_text(), content)


class CalendarTests(unittest.TestCase):
    def test_calendar_preserves_source_total_and_activity(self):
        calendar = parse_calendar(calendar_html("6,257"))
        self.assertEqual(calendar["total"], 6257)
        self.assertEqual(len(calendar["days"]), 365)
        self.assertEqual(calendar["days"][4][1], 4)
        for theme in ("dark", "light"):
            svg = render_calendar(calendar, theme)
            root = ET.fromstring(svg)
            self.assertIn("6,257 contributions", svg)
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")

    def test_missing_total_never_invents_a_number(self):
        with self.assertRaises(ValueError):
            parse_calendar(calendar_html("unavailable"))

    def test_incomplete_or_invalid_calendar_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_calendar(calendar_html(days=20))
        with self.assertRaises(ValueError):
            parse_calendar(calendar_html().replace('data-level="4"', 'data-level="9"', 1))
        with self.assertRaises(ValueError):
            parse_calendar(calendar_html().replace('2025-11-02', '2025-11-01', 1))

    @patch("src.contributions.urllib.request.urlopen")
    def test_fetch_is_public_even_with_a_token_in_environment(self, request):
        request.return_value.__enter__.return_value.read.return_value = calendar_html().encode()
        with patch.dict("os.environ", {"GH_PAT": "never-send-this-token"}):
            fetch_calendar("StealthMoud")
        args, kwargs = request.call_args
        self.assertEqual(args[0].full_url, "https://github.com/users/StealthMoud/contributions")
        self.assertFalse(args[0].has_header("Authorization"))
        self.assertEqual(kwargs["timeout"], 20)

    def test_fetch_failure_keeps_calendar_and_records_honest_status(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "assets").mkdir()
            for theme in ("dark", "light"):
                (root / "assets" / f"activity-{theme}.svg").write_text("previous")
            (root / "README.md").write_text(PROFILE)
            with patch.object(sync_profile, "ROOT", root), patch.object(
                sync_profile, "fetch_calendar", side_effect=OSError("offline")
            ):
                self.assertEqual(sync_profile.main(), 0)
            content = (root / "README.md").read_text()
            self.assertIn("Calendar retained from the last successful refresh.", content)
            self.assertTrue(content.startswith("authored introduction\n"))
            self.assertTrue(content.endswith("\nauthored projects and contact\n"))
            for asset in (root / "assets").iterdir():
                self.assertEqual(asset.read_text(), "previous")

    def test_same_day_is_noop_without_fetching_or_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text(PROFILE)
            with patch.object(sync_profile, "ROOT", root), patch.object(
                sync_profile, "fetch_calendar", return_value=parse_calendar(calendar_html())
            ) as fetch, patch.object(
                sync_profile, "today_in_rome", return_value=date(2026, 10, 29)
            ):
                self.assertEqual(sync_profile.main(), 0)
                paths = [root / "README.md", *(root / "assets").iterdir()]
                before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
                self.assertEqual(sync_profile.main(), 0)
                after = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
                self.assertEqual(before, after)
                self.assertEqual(fetch.call_count, 1)
            self.assertEqual(len(after), 3)


if __name__ == "__main__":
    unittest.main()
