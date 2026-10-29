"""Build the original profile artwork. Python standard library only."""

from pathlib import Path


PALETTES = {
    "dark": {
        "bg": "#0c1b25", "panel": "#102530", "ink": "#edf5f4",
        "muted": "#9fb7c3", "line": "#28434f", "teal": "#69d6cd",
        "copper": "#f1b184", "grid": "#24404c",
    },
    "light": {
        "bg": "#f1f6f6", "panel": "#ffffff", "ink": "#153543",
        "muted": "#4e6977", "line": "#c2d5d9", "teal": "#087e80",
        "copper": "#a85226", "grid": "#d8e5e7",
    },
}


def render_hero(theme, mobile=False):
    p = PALETTES[theme]
    width, height = (640, 560) if mobile else (1200, 420)
    diagram = '''
    <g transform="translate(742 99)">
      <text x="0" y="0" class="label" font-size="13" letter-spacing="2">INSIDE THE REQUEST</text>
      <path d="M17 126H139M139 126H193M139 126V65H193M139 126V187H193" class="trace"/>
      <path d="M211 65H360V126H386M211 187H360V126" class="trace"/>
      <path d="M139 29V225" stroke="COPPER" stroke-width="1.5" stroke-dasharray="4 6"/>
      <rect x="-5" y="102" width="80" height="48" rx="8" class="panel"/>
      <path d="m10 118 9 8-9 8m15 0h11" stroke="TEAL" stroke-width="2" fill="none"/>
      <text x="45" y="131" class="mono" font-size="12">req</text>
      <g class="packet"><rect x="87" y="122" width="8" height="8" rx="2" fill="COPPER"/></g>
      <g transform="translate(193 42)">
        <rect width="146" height="46" rx="7" class="panel"/>
        <circle cx="21" cy="23" r="5" fill="TEAL"/>
        <text x="39" y="28" class="mono" font-size="14">identity</text>
      </g>
      <g transform="translate(193 103)">
        <rect width="146" height="46" rx="7" class="panel"/>
        <path d="m16 23 5 5 8-10" stroke="TEAL" stroke-width="2" fill="none"/>
        <text x="39" y="28" class="mono" font-size="14">input</text>
      </g>
      <g transform="translate(193 164)">
        <rect width="146" height="46" rx="7" class="panel"/>
        <rect x="16" y="18" width="10" height="10" rx="2" fill="TEAL"/>
        <text x="39" y="28" class="mono" font-size="14">access</text>
      </g>
      <circle cx="386" cy="126" r="5" fill="TEAL"/>
      <text x="139" y="249" text-anchor="middle" class="label" font-size="12" style="fill:COPPER">TRUST BOUNDARY</text>
    </g>'''.replace("COPPER", p["copper"]).replace("TEAL", p["teal"])

    if mobile:
        content = '''
  <path d="m36 42 12-10m-12 10 12 10m21-20 12 10-12 10m-9-23-9 26" class="mark"/>
  <text x="99" y="49" class="label" font-size="16" letter-spacing="2">MAHMOUD MOHSENI</text>
  <text x="34" y="151" class="wordmark" font-size="76">StealthMoud<tspan fill="TEAL">.</tspan></text>
  <text x="37" y="211" class="tagline" font-size="30">Understand the system.</text>
  <text x="37" y="252" class="tagline" font-size="30">Test the assumptions.</text>
  <path d="M37 310H603" class="trace"/>
  <text x="37" y="350" class="label" font-size="18">WEB SECURITY / BACKEND SYSTEMS</text>
  <g transform="translate(37 390)">
    <rect width="566" height="111" rx="10" class="panel"/>
    <text x="22" y="35" class="label" font-size="16" letter-spacing="2">FOLLOW THE REQUEST</text>
    <path d="M104 72H218M320 72H416" class="trace"/>
    <text x="22" y="79" class="mono" font-size="21">input</text>
    <text x="224" y="79" class="mono" font-size="21" style="fill:TEAL">inspect</text>
    <text x="422" y="79" class="mono" font-size="21">verify</text>
    <path d="M166 51V94M377 51V94" stroke="COPPER" stroke-dasharray="3 4"/>
    <circle cx="166" cy="72" r="5" fill="COPPER"/>
    <circle cx="377" cy="72" r="5" fill="COPPER"/>
  </g>
  <text x="37" y="538" class="label" font-size="16" letter-spacing="2">SECURITY RESEARCH &amp; OPEN SOURCE</text>'''
    else:
        content = '''
  <path d="m45 47 12-10m-12 10 12 10m21-20 12 10-12 10m-9-23-9 26" class="mark"/>
  <text x="109" y="53" class="label" font-size="14" letter-spacing="2.1">MAHMOUD MOHSENI / SECURITY &amp; SOFTWARE</text>
  <text x="43" y="173" class="wordmark" font-size="87">StealthMoud<tspan fill="TEAL">.</tspan></text>
  <text x="48" y="238" class="tagline" font-size="30">Understand the system.</text>
  <text x="48" y="280" class="tagline" font-size="30">Test the assumptions.</text>
  <path d="M48 328H645" class="trace"/>
  <text x="48" y="363" class="label" font-size="13" letter-spacing="1.5">WEB SECURITY</text>
  <circle cx="198" cy="358" r="2" fill="COPPER"/>
  <text x="218" y="363" class="label" font-size="13" letter-spacing="1.5">BACKEND SYSTEMS</text>
  <circle cx="407" cy="358" r="2" fill="COPPER"/>
  <text x="427" y="363" class="label" font-size="13" letter-spacing="1.5">OPEN SOURCE</text>
  <path d="M695 99V353" class="trace"/>
''' + diagram

    content = content.replace("TEAL", p["teal"]).replace("COPPER", p["copper"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">StealthMoud — Mahmoud Mohseni</title>
  <desc id="desc">Web security, backend systems, and open source. Understand the system. Test the assumptions. A request diagram illustrates identity, input, and access checks across a trust boundary.</desc>
  <defs>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M28 0H0V28" fill="none" stroke="{p['grid']}" stroke-width="0.6"/>
    </pattern>
  </defs>
  <style>
    .wordmark {{ font-family: 'Trebuchet MS', 'Segoe UI', sans-serif; font-weight: 700; letter-spacing: -4px; fill: {p['ink']}; }}
    .tagline {{ font-family: 'Trebuchet MS', 'Segoe UI', sans-serif; fill: {p['ink']}; }}
    .label {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; fill: {p['muted']}; }}
    .mono {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; fill: {p['ink']}; }}
    .trace {{ fill: none; stroke: {p['line']}; stroke-width: 1.5; }}
    .panel {{ fill: {p['panel']}; stroke: {p['line']}; stroke-width: 1.5; }}
    .mark {{ fill: none; stroke: {p['teal']}; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }}
    .packet {{ animation: inspect 4.5s ease-in-out 1; }}
    @keyframes inspect {{ 0% {{ transform: translateX(-10px); opacity: 0; }} 20% {{ opacity: 1; }} 65% {{ transform: translateX(45px); }} 100% {{ transform: translateX(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .packet {{ animation: none; }} }}
  </style>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="16" fill="{p['bg']}" stroke="{p['line']}"/>
  <rect x="{340 if mobile else 715}" y="17" width="{280 if mobile else 466}" height="{height - 34}" fill="url(#grid)" opacity="0.55"/>
  <path d="M25 1H{width - 25}" stroke="{p['teal']}" stroke-width="2"/>
  <path d="M{width - 155} 1H{width - 25}" stroke="{p['copper']}" stroke-width="2"/>
{content}
</svg>
'''


def main():
    assets = Path(__file__).resolve().parents[1] / "assets"
    assets.mkdir(exist_ok=True)
    for theme in PALETTES:
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            (assets / f"hero-{theme}{suffix}.svg").write_text(
                render_hero(theme, mobile), encoding="utf-8"
            )


if __name__ == "__main__":
    main()
