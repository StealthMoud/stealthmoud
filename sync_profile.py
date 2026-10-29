"""Perform one transparent profile-maintenance update per Europe/Rome day."""

from datetime import date, datetime
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from src.contributions import fetch_calendar, render_calendar


ROOT = Path(__file__).resolve().parent
START = "<!-- PROFILE_REFRESH:START -->"
END = "<!-- PROFILE_REFRESH:END -->"


def today_in_rome():
    return datetime.now(ZoneInfo("Europe/Rome")).date()


def status_block(content):
    if content.count(START) != 1 or content.count(END) != 1:
        raise ValueError("README must have exactly one profile refresh block")
    start, end = content.index(START), content.index(END)
    if end < start:
        raise ValueError("Profile refresh markers are reversed")
    return start, end + len(END), content[start:end + len(END)]


def last_refresh_day(block):
    match = re.search(r"Automated maintenance: <strong>(\d{4}-\d{2}-\d{2})</strong>", block)
    return date.fromisoformat(match.group(1)) if match else None


def write_if_changed(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as output:
            temporary = Path(output.name)
            output.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    try:
        readme = ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        start, end, block = status_block(content)
        today = today_in_rome()
        last = last_refresh_day(block)
        if last == today:
            print(f"Already maintained on {today} (Europe/Rome). No changes.")
            return 0
        if last and last > today:
            raise ValueError("README refresh date is in the future")

        calendar_status = "Calendar refreshed."
        try:
            calendar = fetch_calendar("StealthMoud")
            rendered = {
                ROOT / "assets" / f"activity-{theme}.svg": render_calendar(calendar, theme)
                for theme in ("dark", "light")
            }
            # Validate both results before replacing any published calendar.
            for asset in rendered.values():
                ET.fromstring(asset)
            for path, asset in rendered.items():
                write_if_changed(path, asset)
        except Exception as error:
            print(f"Calendar unavailable; keeping the last snapshot: {error}", file=sys.stderr)
            calendar_status = "Calendar retained from the last successful refresh."

        updated = (
            f"{START}\n"
            f"<sub>Automated maintenance: <strong>{today.isoformat()}</strong> "
            f"(Europe/Rome) · {calendar_status}</sub>\n"
            f"{END}"
        )
        write_if_changed(readme, content[:start] + updated + content[end:])
        print(f"Daily maintenance recorded for {today} (Europe/Rome).")
    except Exception as error:
        print(f"Profile maintenance failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
