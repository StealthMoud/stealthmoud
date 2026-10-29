"""Refresh the profile's public contribution calendars without editing the README."""

from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET

from src.contributions import fetch_calendar, render_calendar


ROOT = Path(__file__).resolve().parent


def main():
    try:
        calendar = fetch_calendar("StealthMoud")
        rendered = {
            ROOT / "assets" / f"activity-{theme}.svg": render_calendar(calendar, theme)
            for theme in ("dark", "light")
        }
        # Validate every result before replacing any of the published assets.
        for content in rendered.values():
            ET.fromstring(content)
        for path, content in rendered.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and path.read_text(encoding="utf-8") == content:
                continue
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
        print("Public contribution calendars refreshed. README unchanged.")
    except Exception as error:
        print(f"Calendar refresh failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
