import urllib.request
import re
import os

def generate_svg():
    username = "stealthmoud"
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode()
    except Exception as e:
        print(f"Error fetching contributions: {e}")
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

    # Parse level grid
    grid = []  # 7 rows of 53 weeks
    for day_index, tr_block in enumerate(tr_blocks):
        cells = re.findall(r"<td[^>]*class=\"[^\"]*ContributionCalendar-day[^\"]*\"[^>]*>", tr_block)
        row_levels = []
        for cell in cells:
            level_match = re.search(r'data-level="(\d+)"', cell)
            level = int(level_match.group(1)) if level_match else 0
            row_levels.append(level)
        grid.append(row_levels)

    # Verify grid dimensions
    num_weeks = len(grid[0])
    print(f"Grid dimensions: 7 rows x {num_weeks} columns.")

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
    # Dimensions: 53 weeks * 13px = 689px + labels margin
    svg_width = 780
    svg_height = 165

    # Colors (GitHub Dark Theme exact specs)
    bg_color = "#0D1117"
    border_color = "#30363D"
    text_color = "#8B949E"
    colors = {
        0: "#161B22",  # Level 0
        1: "#0E4429",  # Level 1
        2: "#006D32",  # Level 2
        3: "#26A641",  # Level 3
        4: "#39D353",  # Level 4
    }

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none">')
    # Background and border
    svg.append(f'  <rect width="{svg_width}" height="{svg_height}" rx="6" fill="{bg_color}" stroke="{border_color}" stroke-width="1"/>')

    # Font styles
    font_family = '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'
    svg.append('  <style>')
    svg.append(f'    .lbl {{ font-family: {font_family}; font-size: 9px; fill: {text_color}; }}')
    svg.append(f'    .title {{ font-family: {font_family}; font-size: 11px; font-weight: 600; fill: {text_color}; }}')
    svg.append('  </style>')

    # 1. Month Labels
    for col_idx, label in months_labels:
        x_pos = 32 + col_idx * 13
        svg.append(f'  <text x="{x_pos}" y="20" class="lbl">{label}</text>')

    # 2. Weekday Labels
    svg.append('  <text x="10" y="47" class="lbl">Mon</text>')
    svg.append('  <text x="10" y="73" class="lbl">Wed</text>')
    svg.append('  <text x="10" y="99" class="lbl">Fri</text>')

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
            svg.append(f'  <rect x="{x_pos}" y="{y_pos}" width="10" height="10" rx="2" ry="2" fill="{color}"/>')

    # 4. Total count text (bottom left)
    svg.append(f'  <text x="32" y="145" class="lbl">{total_contribs} contributions in the last year</text>')

    # 5. Legend (bottom right)
    legend_start_x = svg_width - 130
    svg.append(f'  <text x="{legend_start_x - 30}" y="145" class="lbl">Less</text>')
    for lvl in range(5):
        lx = legend_start_x + lvl * 13
        svg.append(f'  <rect x="{lx}" y="136" width="10" height="10" rx="2" ry="2" fill="{colors[lvl]}"/>')
    svg.append(f'  <text x="{legend_start_x + 5 * 13 + 5}" y="145" class="lbl">More</text>')

    svg.append('</svg>')

    # Write to file
    svg_content = "\n".join(svg)
    try:
        with open("contributions.svg", "w") as f:
            f.write(svg_content)
        print("Success! contributions.svg generated.")
        return True
    except Exception as e:
        print(f"Error writing contributions.svg: {e}")
        return False

def fetch_streak():
    username = "stealthmoud"
    url = f"https://streak-stats.demolab.com/?user={username}&hide_border=true&background=0d1117&stroke=6366f1&ring=6366f1&fire=818cf8&currStreakLabel=6366f1&sideNums=c9d1d9&sideLabels=c9d1d9&dates=c9d1d9"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read()
            with open("streak.svg", "wb") as f:
                f.write(content)
        print("Success! streak.svg generated.")
        return True
    except Exception as e:
        print(f"Error fetching streak stats: {e}")
        return False

if __name__ == "__main__":
    generate_svg()
    fetch_streak()
