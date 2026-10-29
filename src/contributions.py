"""Render the public GitHub contribution calendar without authenticated data."""

from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
import re
import urllib.request


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
        self.heading = []
        self.in_heading = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h2" and attrs.get("id") == "js-contribution-activity-description":
            self.in_heading = True
        if tag != "td" or "data-date" not in attrs:
            return
        day = date.fromisoformat(attrs["data-date"])
        level = int(attrs["data-level"])
        if level not in range(5) or day in self.days:
            raise ValueError("Invalid or duplicate contribution day")
        self.days[day] = level

    def handle_data(self, data):
        if self.in_heading:
            self.heading.append(data)

    def handle_endtag(self, tag):
        if tag == "h2":
            self.in_heading = False


def parse_calendar(document):
    parser = CalendarParser()
    parser.feed(document)
    heading = " ".join(" ".join(parser.heading).split())
    match = re.search(r"([\d,]+)\s+contributions?\s+in the last year", heading)
    if not match:
        raise ValueError("Public contribution total not found")
    days = sorted(parser.days.items())
    if not 350 <= len(days) <= 371:
        raise ValueError("Expected a complete annual contribution calendar")
    if (days[-1][0] - days[0][0]).days != len(days) - 1:
        raise ValueError("Contribution calendar contains missing dates")
    return {"total": int(match.group(1).replace(",", "")), "days": days}


def fetch_calendar(username):
    if not re.fullmatch(r"[A-Za-z0-9-]+", username):
        raise ValueError("Invalid GitHub username")
    request = urllib.request.Request(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "StealthMoud-profile-calendar"},
    )
    # Deliberately unauthenticated, even if the environment contains GH_PAT.
    with urllib.request.urlopen(request, timeout=20) as response:
        return parse_calendar(response.read().decode("utf-8"))


def render_calendar(calendar, theme="dark"):
    if theme == "dark":
        bg, text, muted, line = "#070d0a", "#e3f0e5", "#9aafa0", "#294431"
        colors = ["#142719", "#2d4821", "#48712a", "#76ac3a", "#b6f45a"]
    elif theme == "light":
        bg, text, muted, line = "#f0f5ec", "#183721", "#526b57", "#b2c9ad"
        colors = ["#dfe9d8", "#b9d694", "#85b75b", "#5e8d27", "#3e6c08"]
    else:
        raise ValueError("Unknown calendar theme")

    days = calendar["days"]
    first = days[0][0]
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    title = f'{calendar["total"]:,} contributions in the last year'
    through = days[-1][0].strftime("%d %b %Y")
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="218" '
        'viewBox="0 0 960 218" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">Public GitHub contribution calendar through {through}. '
        'Darker or brighter squares indicate higher activity.</desc>',
        f'<rect x="1" y="1" width="958" height="216" rx="12" fill="{bg}" stroke="{line}"/>',
        '<style>text {font-family: -apple-system, BlinkMacSystemFont, '
        '"Segoe UI", Helvetica, Arial, sans-serif;}'
        f'.label {{font-size: 11px; fill: {muted};}}</style>',
        f'<text x="30" y="29" fill="{text}" font-size="14" font-weight="600">{escape(title)}</text>',
    ]
    for row, label in ((1, "M"), (3, "W"), (5, "F")):
        svg.append(f'<text x="22" y="{65 + row * 16}" class="label">{label}</text>')
    for day, level in days:
        index = (day - start).days
        x, y = 44 + (index // 7) * 16, 54 + (index % 7) * 16
        if day.day == 1:
            svg.append(f'<text x="{x}" y="47" class="label">{day.strftime("%b")}</text>')
        svg.append(
            f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{colors[level]}">'
            f'<title>{day.isoformat()}: activity level {level} of 4</title></rect>'
        )
    svg.append(f'<text x="30" y="195" class="label">Public profile · through {through}</text>')
    svg.append('<text x="777" y="195" class="label">Less</text>')
    for level, color in enumerate(colors):
        svg.append(f'<rect x="{810 + level * 16}" y="185" width="12" height="12" rx="3" fill="{color}"/>')
    svg.append('<text x="897" y="195" class="label">More</text>')
    svg.append("</svg>")
    return "\n".join(svg) + "\n"
