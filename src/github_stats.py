import urllib.request
import json
import re
import os
import sys

LANGUAGE_COLORS = {
    "JavaScript": "#f1e05a",
    "Python": "#3572a5",
    "TypeScript": "#3178c6",
    "C": "#555555",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "PHP": "#4f5d95",
    "Java": "#b07219",
    "Shell": "#89e051",
    "Go": "#00add8",
    "Rust": "#dea584",
    "Ruby": "#701516",
    "C++": "#f34b7d",
    "C#": "#178600",
    "Dart": "#00b4ab",
    "Vue": "#41b883",
    "Swift": "#f05138",
    "Kotlin": "#A97BFF",
    "Objective-C": "#438eff",
    "PowerShell": "#012456",
    "Makefile": "#427819",
}

def fetch_stats_data(username="stealthmoud"):
    token = os.getenv("GH_PAT")
    headers = {"User-Agent": "Mozilla/5.0"}
    if token:
        headers["Authorization"] = f"token {token}"
        
    print("Fetching repositories...")
    repos = []
    page = 1
    while True:
        if token:
            url = f"https://api.github.com/user/repos?per_page=100&type=owner&page={page}"
        else:
            url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
            
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                page_repos = json.loads(res.read().decode())
                if not page_repos:
                    break
                repos.extend(page_repos)
                if len(page_repos) < 100:
                    break
                page += 1
        except Exception as e:
            print(f"Error fetching repos on page {page}: {e}")
            break
            
    # Filter out forks
    repos = [r for r in repos if not r.get("fork", False)]
    
    total_stars = 0
    languages_bytes = {}
    print(f"Gathering languages for {len(repos)} non-fork repositories...")
    for idx, r in enumerate(repos):
        total_stars += r.get("stargazers_count", 0)
        lang_url = r.get("languages_url")
        if lang_url:
            req_lang = urllib.request.Request(lang_url, headers=headers)
            try:
                # Fast timeout per repository to prevent blocking the entire sync
                with urllib.request.urlopen(req_lang, timeout=3) as res_lang:
                    repo_langs = json.loads(res_lang.read().decode())
                    for lang, bytes_count in repo_langs.items():
                        languages_bytes[lang] = languages_bytes.get(lang, 0) + bytes_count
            except Exception:
                # Fallback to primary language if fetch fails
                primary = r.get("language")
                if primary:
                    languages_bytes[primary] = languages_bytes.get(primary, 0) + 1000
                    
    # Fetch total commits
    print("Fetching total commits count...")
    total_commits = 0
    req_commits = urllib.request.Request(
        f"https://api.github.com/search/commits?q=author:{username}",
        headers=headers
    )
    try:
        with urllib.request.urlopen(req_commits, timeout=10) as res:
            data = json.loads(res.read().decode())
            total_commits = data.get("total_count", 0)
    except Exception as e:
        print(f"Error fetching commits: {e}")
        # Default fallback
        total_commits = 1139
        
    # Fetch total issues
    print("Fetching total issues count...")
    total_issues = 0
    req_issues = urllib.request.Request(
        f"https://api.github.com/search/issues?q=author:{username}+type:issue",
        headers=headers
    )
    try:
        with urllib.request.urlopen(req_issues, timeout=10) as res:
            data = json.loads(res.read().decode())
            total_issues = data.get("total_count", 0)
    except Exception as e:
        print(f"Error fetching issues: {e}")
        
    # Fetch total PRs
    print("Fetching total PRs count...")
    total_prs = 0
    req_prs = urllib.request.Request(
        f"https://api.github.com/search/issues?q=author:{username}+type:pr",
        headers=headers
    )
    try:
        with urllib.request.urlopen(req_prs, timeout=10) as res:
            data = json.loads(res.read().decode())
            total_prs = data.get("total_count", 0)
    except Exception as e:
        print(f"Error fetching PRs: {e}")
        
    return {
        "stars": total_stars,
        "commits": total_commits,
        "prs": total_prs,
        "issues": total_issues,
        "languages": languages_bytes
    }

def calculate_grade(stats):
    # Standard grade calculation based on stars, commits, PRs, and issues
    commits = stats.get("commits", 0)
    stars = stats.get("stars", 0)
    prs = stats.get("prs", 0)
    issues = stats.get("issues", 0)
    
    score = (commits * 0.2) + (stars * 10.0) + (prs * 5.0) + (issues * 5.0)
    
    if score >= 1000:
        return "S+"
    elif score >= 750:
        return "S"
    elif score >= 500:
        return "A+"
    elif score >= 350:
        return "A"
    elif score >= 200:
        return "B+"
    elif score >= 100:
        return "B"
    elif score >= 50:
        return "C+"
    else:
        return "C"

def generate_stats_svg(stats, filename="stats.svg"):
    grade = calculate_grade(stats)
    
    # dimensions matching 495x195
    width = 495
    height = 195
    
    bg_color = "#0D1117"
    border_color = "#30363D"
    accent_color = "#6366f1"
    sub_color = "#8b949e"
    text_color = "#c9d1d9"
    
    # SVG elements
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">')
    
    # Definitions
    svg.append('  <defs>')
    svg.append('    <linearGradient id="stats-card-border" x1="0%" y1="0%" x2="100%" y2="100%">')
    svg.append('      <stop offset="0%" stop-color="#30363D" />')
    svg.append('      <stop offset="50%" stop-color="#6366f1" stop-opacity="0.4" />')
    svg.append('      <stop offset="100%" stop-color="#30363D" />')
    svg.append('    </linearGradient>')
    svg.append('    <linearGradient id="grade-circle-grad" x1="0%" y1="0%" x2="100%" y2="100%">')
    svg.append('      <stop offset="0%" stop-color="#6366f1" />')
    svg.append('      <stop offset="100%" stop-color="#9a93ff" />')
    svg.append('    </linearGradient>')
    svg.append('  </defs>')
    
    # Background and Border
    svg.append(f'  <rect width="{width}" height="{height}" rx="6" fill="{bg_color}" stroke="url(#stats-card-border)" stroke-width="1.2"/>')
    
    # Styles
    font_family = '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'
    svg.append('  <style>')
    svg.append(f'    .title {{ font-family: {font_family}; font-size: 14px; font-weight: bold; fill: {accent_color}; animation: fadein 0.5s ease-out both; }}')
    svg.append(f'    .stat-label {{ font-family: {font_family}; font-size: 11.5px; fill: {text_color}; font-weight: 500; }}')
    svg.append(f'    .stat-value {{ font-family: {font_family}; font-size: 11.5px; fill: #ffffff; font-weight: bold; }}')
    svg.append(f'    .grade-circle {{ transform-box: fill-box; transform-origin: center; animation: spin-draw 1.2s cubic-bezier(0.4, 0, 0.2, 1) both; }}')
    svg.append(f'    .grade-text {{ font-family: {font_family}; font-size: 22px; font-weight: 800; fill: #ffffff; text-shadow: 0 0 8px rgba(99, 102, 241, 0.6); }}')
    svg.append('    @keyframes fadein { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }')
    svg.append('    @keyframes spin-draw { from { stroke-dashoffset: 251; transform: rotate(-90deg); } to { stroke-dashoffset: 50; transform: rotate(270deg); } }')
    svg.append('  </style>')
    
    # Title
    svg.append(f'  <text x="25" y="35" class="title">Mahmoud Mohseni\'s GitHub Stats</text>')
    
    # Stats entries
    stats_list = [
        ("Total Stars Earned:", stats.get("stars", 0), "M 25,65 m -6,0 a 6,6 0 1,0 12,0 a 6,6 0 1,0 -12,0 M 22,65 L 28,65 M 25,62 L 25,68"), # star icon simpl
        ("Total Commits:", stats.get("commits", 0), "M 25,90 m -6,0 a 6,6 0 1,0 12,0 a 6,6 0 1,0 -12,0 M 23,87 L 27,93 M 27,87 L 23,93"), # commit icon simpl
        ("Total PRs:", stats.get("prs", 0), "M 25,115 m -6,0 a 6,6 0 1,0 12,0 a 6,6 0 1,0 -12,0 M 25,109 L 25,121"), # pr icon simpl
        ("Total Issues:", stats.get("issues", 0), "M 25,140 m -6,0 a 6,6 0 1,0 12,0 a 6,6 0 1,0 -12,0"), # issue icon simpl
        ("Contributed to (last year):", 0, "M 25,165 m -6,0 a 6,6 0 1,0 12,0 a 6,6 0 1,0 -12,0") # contrib icon simpl
    ]
    
    # Draw Stats rows
    y_start = 65
    y_step = 25
    for idx, (label, val, icon_path) in enumerate(stats_list):
        y_pos = y_start + idx * y_step
        # Icon representation (small simple visual indicators)
        svg.append(f'  <circle cx="30" cy="{y_pos - 4}" r="5" stroke="{accent_color}" stroke-width="1" fill="none"/>')
        svg.append(f'  <circle cx="30" cy="{y_pos - 4}" r="1.5" fill="{accent_color}"/>')
        
        delay = 0.1 + idx * 0.05
        svg.append(f'  <text x="48" y="{y_pos}" class="stat-label" style="animation: fadein 0.5s ease-out {delay:.2f}s both;">{label}</text>')
        svg.append(f'  <text x="215" y="{y_pos}" class="stat-value" style="animation: fadein 0.5s ease-out {delay:.2f}s both;">{val:,}</text>')
        
    # Grade Badge on Right side
    cx = 385
    cy = 105
    r = 40
    # Perimeter = 2 * pi * r = 251.2
    svg.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" stroke="#161b22" stroke-width="6" fill="none"/>')
    svg.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" stroke="url(#grade-circle-grad)" stroke-width="6" fill="none" stroke-dasharray="251.2" stroke-dashoffset="50" stroke-linecap="round" class="grade-circle"/>')
    svg.append(f'  <text x="{cx}" y="{cy + 8}" text-anchor="middle" class="grade-text">{grade}</text>')
    
    svg.append('</svg>')
    
    with open(filename, "w") as f:
        f.write("\n".join(svg))
    print(f"Stats SVG written successfully to {filename}")
    return True

def generate_languages_svg(stats, filename="languages.svg"):
    # Sort and calculate percentages
    languages = stats.get("languages", {})
    total_bytes = sum(languages.values())
    
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    
    # dimensions matching 495x195
    width = 495
    height = 195
    
    bg_color = "#0D1117"
    border_color = "#30363D"
    accent_color = "#6366f1"
    text_color = "#c9d1d9"
    sub_color = "#8b949e"
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">')
    # Progress bar dimensions
    bar_x = 25
    bar_y = 52
    bar_w = 445
    bar_h = 10
    
    # Definitions
    svg.append('  <defs>')
    svg.append('    <linearGradient id="langs-card-border" x1="0%" y1="0%" x2="100%" y2="100%">')
    svg.append('      <stop offset="0%" stop-color="#30363D" />')
    svg.append('      <stop offset="50%" stop-color="#6366f1" stop-opacity="0.4" />')
    svg.append('      <stop offset="100%" stop-color="#30363D" />')
    svg.append('    </linearGradient>')
    # Rounded bar mask to clip ends of the segment track
    svg.append('    <mask id="bar-mask">')
    svg.append(f'      <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5" fill="#ffffff" />')
    svg.append('    </mask>')
    svg.append('  </defs>')
    
    # Background and Border
    svg.append(f'  <rect width="{width}" height="{height}" rx="6" fill="{bg_color}" stroke="url(#langs-card-border)" stroke-width="1.2"/>')
    
    # Styles
    font_family = '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'
    svg.append('  <style>')
    svg.append(f'    .title {{ font-family: {font_family}; font-size: 14px; font-weight: bold; fill: {accent_color}; animation: fadein 0.5s ease-out both; }}')
    svg.append(f'    .lang-lbl {{ font-family: {font_family}; font-size: 11px; fill: {text_color}; font-weight: bold; }}')
    svg.append(f'    .lang-pct {{ font-family: {font_family}; font-size: 11px; fill: {sub_color}; }}')
    svg.append('    .bar-segment {')
    svg.append('      animation: bar-grow 0.8s cubic-bezier(0.1, 0.8, 0.2, 1) both;')
    svg.append('      transform-box: fill-box;')
    svg.append('      transform-origin: left center;')
    svg.append('    }')
    svg.append('    @keyframes fadein { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }')
    svg.append('    @keyframes bar-grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }')
    svg.append('  </style>')
    
    # Title
    svg.append(f'  <text x="25" y="35" class="title">Most Used Languages</text>')
    
    # Display top 8 languages
    display_langs = []
    if total_bytes > 0:
        current_x = bar_x
        # Add background track
        svg.append(f'  <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5" fill="#161b22" />')
        
        for name, size in sorted_langs[:8]:
            pct = (size / total_bytes) * 100
            if pct < 0.1:
                continue
            color = LANGUAGE_COLORS.get(name, "#8b949e")
            segment_w = (size / total_bytes) * bar_w
            
            # Draw segment with rounding mask
            svg.append(f'  <rect x="{current_x}" y="{bar_y}" width="{segment_w}" height="{bar_h}" fill="{color}" class="bar-segment" mask="url(#bar-mask)" />')
            display_langs.append((name, pct, color))
            current_x += segment_w
        
    # Draw details (max 8 languages, 2 columns of 4 rows)
    col1_x = 30
    col2_x = 255
    y_start = 88
    y_step = 24
    
    for idx, (name, pct, color) in enumerate(display_langs[:8]):
        col = idx // 4
        row = idx % 4
        x_pos = col1_x if col == 0 else col2_x
        y_pos = y_start + row * y_step
        
        # Indicator circle
        svg.append(f'  <circle cx="{x_pos}" cy="{y_pos - 4}" r="4.5" fill="{color}" />')
        # Labels
        svg.append(f'  <text x="{x_pos + 14}" y="{y_pos}" class="lang-lbl">{name}</text>')
        svg.append(f'  <text x="{x_pos + 14 + len(name) * 7.5}" y="{y_pos}" class="lang-pct">{pct:.2f}%</text>')
        
    svg.append('</svg>')
    
    with open(filename, "w") as f:
        f.write("\n".join(svg))
    print(f"Languages SVG written successfully to {filename}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        # Quick CLI test run
        stats = fetch_stats_data()
        generate_stats_svg(stats)
        generate_languages_svg(stats)
