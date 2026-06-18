import urllib.request
import re
import datetime
import time

def generate_svg(username="stealthmoud", filename="contributions.svg"):
    # Fech public contribution HTML page and parse it
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    html = None
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode()
                break
        except Exception as e:
            print(f"Attempt {attempt}/{max_retries} failed to fetch contributions: {e}")
            if attempt < max_retries:
                time.sleep(2 * attempt)
            else:
                print(f"All {max_retries} attempts to fetch contributions failed.")
                return False


    # Extract total contributions text
    total_contribs_match = re.search(
        r'<h2[^>]*id="js-contribution-activity-description"[^>]*>\s*([\d,]+)\s+contributions\s+in\s+the\s+last\s+year',
        html,
        re.IGNORECASE
    )
    total_contribs = total_contribs_match.group(1) if total_contribs_match else "2,500+"

    # Extract the table body (tbody)
    tbody_match = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    if not tbody_match:
        print("Error: tbody not found in HTML.")
        return False
    tbody_content = tbody_match.group(1)

    # Extract rows (tr)
    tr_blocks = re.findall(r"<tr[^>]*>.*?</tr>", tbody_content, re.DOTALL)
    if len(tr_blocks) != 7:
        print(f"Error: Expected 7 rows in table body, found {len(tr_blocks)}.")
        return False

    # Pars level grid from html
    grid = []  # 7 rows of 53 weeks
    date_to_coords = {}
    latest_date = ""
    latest_coords = (0, 0)
    for day_index, tr_block in enumerate(tr_blocks):
        cells = re.findall(r"<td[^>]*class=\"[^\"]*ContributionCalendar-day[^\"]*\"[^>]*>", tr_block)
        row_levels = []
        for col_idx, cell in enumerate(cells):
            level_match = re.search(r'data-level="(\d+)"', cell)
            level = int(level_match.group(1)) if level_match else 0
            row_levels.append(level)
            
            date_match = re.search(r'data-date="([^"]+)"', cell)
            if date_match:
                date_str = date_match.group(1)
                date_to_coords[date_str] = (day_index, col_idx)
                if date_str > latest_date:
                    latest_date = date_str
                    latest_coords = (day_index, col_idx)
        grid.append(row_levels)

    # Verify grid dimensions
    num_weeks = len(grid[0])

    # Extract month labels from thead
    thead_match = re.search(r"<thead>(.*?)</thead>", html, re.DOTALL)
    months_labels = []
    if thead_match:
        thead_content = thead_match.group(1)
        td_labels = re.findall(
            r"<td[^>]*class=\"[^\"]*ContributionCalendar-label[^\"]*\"[^>]*>.*?</td>",
            thead_content,
            re.DOTALL
        )
        col_offset = 0
        for td in td_labels:
            colspan_match = re.search(r'colspan="(\d+)"', td)
            colspan = int(colspan_match.group(1)) if colspan_match else 1
            text_match = re.search(r'<span aria-hidden="true"[^>]*>([^<]+)</span>', td)
            if text_match:
                month_text = text_match.group(1)
                months_labels.append((col_offset, month_text))
            col_offset += colspan

    # Generate SVG Content
    svg_width = 780
    svg_height = 165

    # Premium Indigo HSL Theme Palette with high-contast step scaling
    bg_color = "#0D1117"
    border_color = "#30363D"
    text_color = "#8B949E"
    colors = {
        0: "#161B22",  # Level 0 (GitHub empty grid)
        1: "#2d2b63",  # Level 1 (Vibrant low activity indigo)
        2: "#4f49be",  # Level 2 (Vibrant medium activity indigo)
        3: "#746df3",  # Level 3 (Accent indigo)
        4: "#9a93ff",  # Level 4 (Bright glowing indigo)
    }

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none">')
    
    # Custom glow defnition for hover
    svg.append('  <defs>')
    svg.append('    <filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%">')
    svg.append('      <feGaussianBlur stdDeviation="3" result="blur" />')
    svg.append('      <feMerge>')
    svg.append('        <feMergeNode in="blur" />')
    svg.append('        <feMergeNode in="SourceGraphic" />')
    svg.append('      </feMerge>')
    svg.append('    </filter>')
    # Gradient for card border
    svg.append('    <linearGradient id="card-border" x1="0%" y1="0%" x2="100%" y2="100%">')
    svg.append('      <stop offset="0%" stop-color="#30363D" />')
    svg.append('      <stop offset="50%" stop-color="#6366f1" stop-opacity="0.4" />')
    svg.append('      <stop offset="100%" stop-color="#30363D" />')
    svg.append('    </linearGradient>')
    svg.append('  </defs>')

    # Background and border
    svg.append(f'  <rect width="{svg_width}" height="{svg_height}" rx="6" fill="{bg_color}" stroke="url(#card-border)" stroke-width="1.2"/>')

    # Font styles and spring-like hover and wave animations
    font_family = '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'
    svg.append('  <style>')
    svg.append(f'    .lbl {{ font-family: {font_family}; font-size: 9px; fill: {text_color}; }}')
    svg.append(f'    .title {{ font-family: {font_family}; font-size: 11px; font-weight: 600; fill: #ffffff; }}')
    svg.append('    .contrib-day {')
    svg.append('      transition: transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275), fill 0.2s, stroke 0.2s;')
    svg.append('      transform-box: fill-box;')
    svg.append('      transform-origin: center;')
    svg.append('      animation: wave 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.2) both;')
    svg.append('    }')
    svg.append('    .contrib-day:hover {')
    svg.append('      transform: scale(1.35);')
    svg.append('      stroke: #8f7aff;')
    svg.append('      stroke-width: 1;')
    svg.append('      fill: #8f7aff !important;')
    svg.append('      filter: url(#neon-glow);')
    svg.append('      cursor: pointer;')
    svg.append('    }')
    svg.append('    .contrib-today {')
    svg.append('      stroke: #9a93ff;')
    svg.append('      stroke-width: 1.5;')
    svg.append('      animation: today-pulse 2s infinite ease-in-out, wave 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.2) both;')
    svg.append('    }')
    svg.append('    .today-indicator {')
    svg.append('      animation: indicator-glow 1.5s infinite ease-in-out;')
    svg.append('      transform-box: fill-box;')
    svg.append('      transform-origin: center;')
    svg.append('      filter: url(#neon-glow);')
    svg.append('    }')
    svg.append('    @keyframes wave {')
    svg.append('      0% { opacity: 0; transform: scale(0.3) translateY(4px); }')
    svg.append('      70% { transform: scale(1.05); }')
    svg.append('      100% { opacity: 1; transform: scale(1) translateY(0); }')
    svg.append('    }')
    svg.append('    @keyframes today-pulse {')
    svg.append('      0%, 100% {')
    svg.append('        stroke-opacity: 0.5;')
    svg.append('        stroke-width: 1;')
    svg.append('        filter: drop-shadow(0 0 2px rgba(154, 147, 255, 0.4));')
    svg.append('      }')
    svg.append('      50% {')
    svg.append('        stroke-opacity: 1;')
    svg.append('        stroke-width: 2;')
    svg.append('        filter: drop-shadow(0 0 6px rgba(154, 147, 255, 0.9));')
    svg.append('      }')
    svg.append('    }')
    svg.append('    @keyframes indicator-glow {')
    svg.append('      0%, 100% { opacity: 0.5; transform: scale(0.8); }')
    svg.append('      50% { opacity: 1; transform: scale(1.3); }')
    svg.append('    }')
    svg.append('  </style>')

    # 1. Month Labels
    for col_idx, label in months_labels:
        x_pos = 32 + col_idx * 13
        svg.append(f'  <text x="{x_pos}" y="20" class="lbl">{label}</text>')

    # 2. Weekday Labels
    svg.append('  <text x="10" y="47" class="lbl">Mon</text>')
    svg.append('  <text x="10" y="73" class="lbl">Wed</text>')
    svg.append('  <text x="10" y="99" class="lbl">Fri</text>')

    # Detect current day to highlight today
    now = datetime.datetime.now(datetime.timezone.utc)
    local_now = now + datetime.timedelta(hours=2) # Europe/Rome offset
    local_date_str = local_now.strftime("%Y-%m-%d")

    if local_date_str in date_to_coords:
        today_row, today_col = date_to_coords[local_date_str]
    else:
        today_row, today_col = latest_coords

    # 3. Calendar squares
    for day_idx in range(7):
        y_pos = 28 + day_idx * 13
        for col_idx in range(num_weeks):
            x_pos = 32 + col_idx * 13
            # Check range
            if col_idx < len(grid[day_idx]):
                level = grid[day_idx][col_idx]
            else:
                level = 0
            color = colors.get(level, colors[0])
            
            is_today = (day_idx == today_row and col_idx == today_col)
            classes = "contrib-day"
            if is_today:
                classes += " contrib-today"
                
            delay = min(col_idx * 0.012, 0.65)
            svg.append(f'  <rect x="{x_pos}" y="{y_pos}" width="10" height="10" rx="2.2" fill="{color}" class="{classes}" style="animation-delay: {delay:.3f}s;"/>')
            
            if is_today:
                # Add small pulsing neon target dot at top-right of today block
                svg.append(f'  <circle cx="{x_pos + 10}" cy="{y_pos}" r="2" fill="#9a93ff" class="today-indicator"/>')

    # 4. Total count text (bottom left)
    svg.append(f'  <text x="32" y="146" class="lbl">{total_contribs} contributions in the last year</text>')

    # 5. Legend (bottom right)
    legend_start_x = svg_width - 130
    svg.append(f'  <text x="{legend_start_x - 30}" y="146" class="lbl">Less</text>')
    for lvl in range(5):
        lx = legend_start_x + lvl * 13
        svg.append(f'  <rect x="{lx}" y="137" width="10" height="10" rx="2.2" fill="{colors[lvl]}" class="contrib-day"/>')
    svg.append(f'  <text x="{legend_start_x + 5 * 13 + 5}" y="146" class="lbl">More</text>')

    svg.append('</svg>')

    # Write to file
    svg_content = "\n".join(svg)
    try:
        with open(filename, "w") as f:
            f.write(svg_content)
        print(f"Success! {filename} generated.")
        return True
    except Exception as e:
        print(f"Error writing {filename}: {e}")
        return False
