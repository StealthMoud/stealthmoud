"""Render original, script-free SVG artwork for the security profile."""

from pathlib import Path
from html import escape


PALETTES = {
    "dark": {
        "bg": "#070d0a", "panel": "#0c1810", "ink": "#e3f0e5",
        "muted": "#9aafa0", "line": "#294431", "green": "#b6f45a",
        "cyan": "#6ae5f1", "pink": "#f17aad", "grid": "#27402f",
    },
    "light": {
        "bg": "#f0f5ec", "panel": "#e5eddf", "ink": "#183721",
        "muted": "#526b57", "line": "#b2c9ad", "green": "#3e6c08",
        "cyan": "#086d80", "pink": "#aa315c", "grid": "#bacdb3",
    },
}


def svg_frame(content, width, height, p, title, description):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="{p['grid']}" stroke-width="0.6"/>
  </pattern>
  <pattern id="crt" width="4" height="4" patternUnits="userSpaceOnUse">
    <path d="M0 1H4" stroke="{p['ink']}" stroke-opacity=".035"/>
  </pattern>
  <filter id="glow" x="-70%" y="-70%" width="240%" height="240%">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="type-clip"><rect class="type-mask" x="24" y="-23" width="325" height="33"/></clipPath>
  <clipPath id="glitch-cut"><path d="M0 145H700V159H0ZM0 174H700V183H0Z"/></clipPath>
</defs>
<style>
  text {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; fill: {p['ink']}; }}
  .muted {{ fill: {p['muted']}; }}
  .accent {{ fill: {p['green']}; }}
  .cyan {{ fill: {p['cyan']}; }}
  .line {{ stroke: {p['line']}; fill: none; }}
  .panel {{ fill: {p['panel']}; stroke: {p['line']}; }}
  .wordmark {{ font-size: 86px; font-weight: 800; letter-spacing: -5px; fill: {p['green']}; }}
  .sweep {{ animation: radar 12s linear infinite; transform-origin: 0 0; }}
  .ping {{ animation: ping 12s cubic-bezier(.18,.65,.3,1) infinite; }}
  .ping-b {{ animation-delay: -4s; }}
  .ping-c {{ animation-delay: -8s; }}
  .type-mask {{ animation: typing 12s steps(24,end) infinite; }}
  .cursor {{ animation: cursor 1.2s steps(1,end) infinite; }}
  .cursor-ready {{ animation: ready 12s steps(1,end) infinite; }}
  .phase {{ fill: {p['muted']}; animation: phase 12s steps(1,end) infinite; }}
  .phase-b {{ animation-name: phase-b; }}
  .phase-c {{ animation-name: phase-c; }}
  .glitch {{ opacity: 0; animation: glitch 12s steps(1,end) infinite; }}
  .trace {{ stroke: {p['green']}; stroke-width: 2; fill: none; stroke-dasharray: 20 1080; animation: transmit 8s cubic-bezier(.4,0,.3,1) infinite; }}
  .step {{ animation: step 12s steps(1,end) infinite; }}
  .step-b {{ animation-delay: -9s; }}
  .step-c {{ animation-delay: -6s; }}
  .step-d {{ animation-delay: -3s; }}
  @keyframes radar {{ to {{ transform: rotate(360deg); }} }}
  @keyframes ping {{ 0%,8% {{ opacity: 1; stroke-width: 2; }} 30%,100% {{ opacity: .15; stroke-width: 1; }} }}
  @keyframes typing {{ 0%,3% {{ width: 0; }} 23%,94% {{ width: 325px; }} 98%,100% {{ width: 0; }} }}
  @keyframes cursor {{ 0%,49% {{ opacity: 1; }} 50%,100% {{ opacity: 0; }} }}
  @keyframes ready {{ 0%,22% {{ opacity: 0; }} 23%,94% {{ opacity: 1; }} 95%,100% {{ opacity: 0; }} }}
  @keyframes phase {{ 0%,23% {{ fill: {p['muted']}; }} 24%,45% {{ fill: {p['green']}; }} 46%,100% {{ fill: {p['muted']}; }} }}
  @keyframes phase-b {{ 0%,45% {{ fill: {p['muted']}; }} 46%,68% {{ fill: {p['green']}; }} 69%,100% {{ fill: {p['muted']}; }} }}
  @keyframes phase-c {{ 0%,68% {{ fill: {p['muted']}; }} 69%,94% {{ fill: {p['green']}; }} 95%,100% {{ fill: {p['muted']}; }} }}
  @keyframes glitch {{ 0%,51% {{ opacity: 0; }} 52% {{ opacity: .8; transform: translateX(3px); }} 53% {{ opacity: .6; transform: translateX(-2px); }} 54%,100% {{ opacity: 0; }} }}
  @keyframes transmit {{ 0% {{ stroke-dashoffset: 20; opacity: 0; }} 8%,85% {{ opacity: 1; }} 100% {{ stroke-dashoffset: -1080; opacity: 0; }} }}
  @keyframes step {{ 0%,24% {{ stroke: {p['green']}; }} 25%,100% {{ stroke: {p['line']}; }} }}
  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{ animation: none !important; }}
    .type-mask {{ width: 325px; }}
    .cursor-ready {{ opacity: 1; }}
    .glitch {{ display: none; }}
    .trace {{ stroke-dasharray: none; opacity: .45; }}
  }}
</style>
<path d="M17 1H{width - 26}L{width - 1} 26V{height - 17}L{width - 17} {height - 1}H26L1 {height - 26}V17Z" fill="{p['bg']}" stroke="{p['line']}" stroke-width="2"/>
{content}
</svg>
'''


def render_radar(p, x, y, scale=1):
    return f'''<g transform="translate({x} {y}) scale({scale})">
  <circle r="166" class="line" stroke-dasharray="2 9"/>
  <circle r="148" class="line"/>
  <circle r="112" class="line"/>
  <circle r="75" class="line"/>
  <path d="M-162 0H162M0-162V162" class="line" stroke-dasharray="3 7"/>
  <g class="sweep">
    <path d="M0 0V-147A147 147 0 0 1 127.3-73.5Z" fill="{p['green']}" opacity=".075"/>
    <path d="M0 0V-147" stroke="{p['green']}" stroke-width="1.5" opacity=".75"/>
    <circle cy="-147" r="3" fill="{p['green']}"/>
  </g>
  <path d="M-99-62-46-27M92-42 46-21M20 110 8 50" class="line"/>
  <circle cx="-99" cy="-62" r="12" fill="none" stroke="{p['green']}" class="ping"/>
  <circle cx="-99" cy="-62" r="4" fill="{p['green']}"/>
  <circle cx="92" cy="-42" r="12" fill="none" stroke="{p['cyan']}" class="ping ping-b"/>
  <circle cx="92" cy="-42" r="4" fill="{p['cyan']}"/>
  <circle cx="20" cy="110" r="12" fill="none" stroke="{p['green']}" class="ping ping-c"/>
  <circle cx="20" cy="110" r="4" fill="{p['green']}"/>
  <text x="-127" y="-84" font-size="12" class="muted">AUTH</text>
  <text x="105" y="-56" font-size="12" class="muted">INPUT</text>
  <text x="37" y="132" font-size="12" class="muted">STATE</text>
  <path d="M0-58 50-29V29L0 58-50 29V-29Z" fill="{p['bg']}" stroke="{p['green']}" stroke-opacity=".5"/>
  <g stroke-width="3" stroke-linecap="square" fill="none">
    <path d="M-9-19H-30V0H-9V19H-30" stroke="{p['green']}"/>
    <path d="M5 19V-19L18 0 31-19V19" stroke="{p['cyan']}"/>
  </g>
  <path d="M-176-122V-176H-122M122-176H176V-122M176 122V176H122M-122 176H-176V122" fill="none" stroke="{p['green']}" opacity=".65"/>
</g>'''


def render_terminal(p, x, y, mobile=False):
    size = 21 if mobile else 17
    gap = 38 if mobile else 34
    return f'''<g transform="translate({x} {y})" font-size="{size}">
  <text class="accent">$</text>
  <text x="24" clip-path="url(#type-clip)">trace --scope local-lab</text>
  <g class="cursor-ready"><rect x="{307 if mobile else 258}" y="-{size - 3}" width="9" height="{size}" fill="{p['green']}" class="cursor"/></g>
  <text y="{gap}" class="phase">[+] map the attack surface</text>
  <text y="{gap * 2}" class="phase phase-b">[+] inspect trust boundaries</text>
  <text y="{gap * 3}" class="phase phase-c">[+] reproduce &amp; document</text>
</g>'''


def render_hero(theme, mobile=False):
    p = PALETTES[theme]
    if mobile:
        width, height = 640, 820
        content = f'''
  <rect x="325" y="60" width="285" height="720" fill="url(#grid)" opacity=".45"/>
  <path d="M1 56H639" class="line"/>
  <circle cx="29" cy="29" r="4" fill="{p['green']}"/><circle cx="45" cy="29" r="4" fill="{p['cyan']}"/><circle cx="61" cy="29" r="4" fill="{p['line']}"/>
  <text x="84" y="35" font-size="17" class="muted">stealthmoud@lab:~</text>
  <text x="31" y="98" font-size="16" class="cyan" letter-spacing="2">SECURITY RESEARCH / OPEN SOURCE</text>
  <text x="27" y="174" class="wordmark" style="font-size:78px">STEALTHMOUD</text>
  <g class="glitch" clip-path="url(#glitch-cut)"><text x="27" y="174" class="wordmark" style="font-size:78px;fill:{p['cyan']}">STEALTHMOUD</text></g>
  <text x="32" y="215" font-size="19" class="muted" letter-spacing="2">MAHMOUD MOHSENI</text>
  <text x="32" y="265" font-size="28">Follow the input.</text>
  <text x="32" y="301" font-size="28">Question the trust.</text>
  <path d="M32 337H608" class="line"/>
  {render_terminal(p, 34, 382, True)}
  <text x="34" y="569" font-size="17" class="cyan" letter-spacing="2">RESEARCH CONSOLE</text>
  <text x="34" y="616" font-size="25" class="accent">WEB + API</text>
  <text x="34" y="653" font-size="19">AUTH / ACCESS</text>
  <text x="34" y="690" font-size="19">BACKEND LOGIC</text>
  <text x="34" y="736" font-size="15" class="muted">[ LOCAL LAB SIMULATION ]</text>
  {render_radar(p, 465, 650, .67)}
  <path d="M32 772H608" class="line"/><path d="M32 772H608" class="trace"/>
  <text x="34" y="802" font-size="15" class="muted">CURIOSITY IS THE ENTRY POINT.</text>
'''
    else:
        width, height = 1200, 560
        content = f'''
  <rect x="746" y="57" width="430" height="450" fill="url(#grid)" opacity=".45"/>
  <path d="M1 56H1199" class="line"/>
  <circle cx="31" cy="29" r="4" fill="{p['green']}"/><circle cx="48" cy="29" r="4" fill="{p['cyan']}"/><circle cx="65" cy="29" r="4" fill="{p['line']}"/>
  <text x="89" y="35" font-size="16" class="muted">stealthmoud@lab:~</text>
  <text x="1155" y="35" text-anchor="end" font-size="13" class="muted" letter-spacing="2">PUBLIC RESEARCH CONSOLE</text>
  <text x="47" y="107" font-size="14" class="cyan" letter-spacing="2">SECURITY RESEARCH / BACKEND ENGINEERING</text>
  <text x="42" y="189" class="wordmark">STEALTHMOUD</text>
  <g class="glitch" clip-path="url(#glitch-cut)"><text x="42" y="189" class="wordmark" style="fill:{p['cyan']}">STEALTHMOUD</text></g>
  <text x="48" y="228" font-size="17" class="muted" letter-spacing="3">MAHMOUD MOHSENI</text>
  <text x="48" y="277" font-size="23">Follow the input. Question the trust.</text>
  <path d="M48 306H672" class="line"/>
  {render_terminal(p, 49, 348)}
  <path d="M720 91V476" class="line" stroke-dasharray="2 8"/>
  <text x="953" y="91" text-anchor="middle" font-size="13" class="muted" letter-spacing="3">ATTACK SURFACE</text>
  {render_radar(p, 953, 286)}
  <text x="953" y="493" text-anchor="middle" font-size="12" class="muted" letter-spacing="1.5">[ LOCAL LAB SIMULATION ]</text>
  <path d="M48 506H1152" class="line"/><path d="M48 506H1152" class="trace"/>
  <text x="48" y="537" font-size="13" class="accent" letter-spacing="1.5">WEB + API SECURITY</text>
  <text x="380" y="537" font-size="13" class="muted" letter-spacing="1.5">AUTH / ACCESS / BACKEND LOGIC</text>
  <text x="1152" y="537" text-anchor="end" font-size="13" class="cyan" letter-spacing="1.5">CURIOSITY IS THE ENTRY POINT.</text>
'''
    content += f'<rect x="18" y="58" width="{width - 36}" height="{height - 77}" fill="url(#crt)" pointer-events="none"/>'
    return svg_frame(
        content, width, height, p,
        "StealthMoud — Mahmoud Mohseni / security research console",
        "An animated hacker terminal and radar illustrate local security research. "
        "Follow the input. Question the trust. Web and API security, authentication, "
        "access control, and backend engineering. Motion stops with reduced-motion preferences.",
    )


def render_flow(theme, mobile=False):
    p = PALETTES[theme]
    stages = [
        ("SCOPE", "Define the boundaries"),
        ("INSPECT", "Follow the request"),
        ("REPRODUCE", "Verify the behavior"),
        ("DOCUMENT", "Keep the evidence"),
    ]
    width, height = (640, 354) if mobile else (1200, 150)
    content = []
    for i, (name, detail) in enumerate(stages):
        extra = f"step-{chr(97 + i)}" if i else ""
        if mobile:
            y = 43 + i * 85
            content.append(f'<text x="33" y="{y}" font-size="21" class="accent">0{i + 1}</text>')
            content.append(f'<circle cx="85" cy="{y - 7}" r="5" class="step {extra}" fill="{p["bg"]}" stroke="{p["line"]}" stroke-width="2"/>')
            content.append(f'<text x="110" y="{y}" font-size="24" class="accent">{name}</text>')
            content.append(f'<text x="110" y="{y + 28}" font-size="21" class="muted">{detail}</text>')
            if i < 3:
                content.append(f'<path d="M85 {y + 8}V{y + 63}" class="line"/>')
        else:
            x = 28 + i * 294
            content.append(f'<path d="M{x + 54} 29H{x + 254}" class="line"/>')
            content.append(f'<circle cx="{x + 12}" cy="29" r="8" class="step {extra}" fill="{p["bg"]}" stroke="{p["line"]}" stroke-width="2"/>')
            content.append(f'<text x="{x + 34}" y="34" font-size="13" class="muted">0{i + 1}</text>')
            content.append(f'<text x="{x + 3}" y="79" font-size="22" class="accent">{name}</text>')
            content.append(f'<text x="{x + 3}" y="113" font-size="15" class="muted">{detail}</text>')
    return svg_frame(
        "\n".join(content), width, height, p, "The research loop",
        "Scope: define the boundaries. Inspect: follow the request. "
        "Reproduce: verify the behavior. Document: keep the evidence.",
    )


def main():
    assets = Path(__file__).resolve().parents[1] / "assets"
    assets.mkdir(exist_ok=True)
    for theme in PALETTES:
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            for name, render in (("hero", render_hero), ("flow", render_flow)):
                artwork = render(theme, mobile)
                (assets / f"{name}-{theme}{suffix}.svg").write_text(
                    artwork, encoding="utf-8"
                )
                # Picture sources select this version even when an embedded SVG
                # does not inherit the host page's reduced-motion preference.
                static_artwork = artwork.replace(
                    "@media (prefers-reduced-motion: reduce)", "@media all"
                )
                (assets / f"{name}-{theme}{suffix}-static.svg").write_text(
                    static_artwork, encoding="utf-8"
                )


if __name__ == "__main__":
    main()
