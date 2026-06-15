import urllib.request
import re
import json
import datetime
import subprocess

def fetch_recent_commits(username="stealthmoud"):
    # Fech recent public commits from API with local git fallback
    url = f"https://api.github.com/users/{username}/events/public"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    commits_list = []
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            events = json.loads(response.read().decode())
            for event in events:
                if event.get("type") == "PushEvent":
                    repo_name = event.get("repo", {}).get("name", "").replace(f"{username}/", "")
                    payload = event.get("payload", {})
                    commits = payload.get("commits", [])
                    for commit in commits:
                        message = commit.get("message", "").split("\n")[0]
                        if len(message) > 60:
                            message = message[:57] + "..."
                        sha = commit.get("sha", "")
                        commits_list.append((repo_name, message, sha))
                        if len(commits_list) >= 5:
                            break
                if len(commits_list) >= 5:
                    break
    except Exception as e:
        print(f"Error fetching commits from API: {e}")
        
    # Local fallback if public events are empty or fetch failed
    if not commits_list:
        try:
            cmd = ["git", "log", "-n", "5", "--pretty=format:%h|%s|%H"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            for line in res.stdout.strip().split("\n"):
                if "|" in line:
                    short_sha, message, sha = line.split("|", 2)
                    commits_list.append(("stealthmoud", message, sha))
        except Exception as e:
            print(f"Error fetching local git logs: {e}")
            
    return commits_list

def update_readme_commits(commits):
    if not commits:
        return
    
    formatted_commits = ["### System Logs"]
    for repo, msg, sha in commits:
        short_sha = sha[:7]
        commit_url = f"https://github.com/StealthMoud/{repo}/commit/{sha}"
        formatted_commits.append(f"- **{repo}** — `{msg}` [#{short_sha}]({commit_url})")
    
    commits_text = "\n".join(formatted_commits)
    
    try:
        with open("README.md", "r") as f:
            content = f.read()
        
        pattern = r"<!-- RECENT_COMMITS_START -->.*?<!-- RECENT_COMMITS_END -->"
        replacement = f"<!-- RECENT_COMMITS_START -->\n\n{commits_text}\n\n<!-- RECENT_COMMITS_END -->"
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open("README.md", "w") as f:
            f.write(new_content)
        print("Success! README.md updated with recent commits.")
    except Exception as e:
        print(f"Error updating README.md: {e}")

def generate_status_svg(latest_commit_msg):
    now = datetime.datetime.now(datetime.timezone.utc)
    # Adjust to Europe/Rome timezone (UTC+2)
    local_now = now + datetime.timedelta(hours=2)
    
    # Calculate year progress percentge
    day_of_year = local_now.timetuple().tm_yday
    year = local_now.year
    is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
    total_days = 366 if is_leap else 365
    progress = (day_of_year / total_days) * 100
    
    # Format year progress bar (20 blocks)
    filled_blocks = int(progress / 5)
    bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
    
    # Format local time string
    time_str = local_now.strftime("%H:%M:%S")
    date_str = local_now.strftime("%Y-%m-%d")

    # Uptime simulation
    uptime_days = (day_of_year % 14) + 2
    uptime_str = f"{uptime_days}d {local_now.hour}h {local_now.minute}m"

    # CPU and memory variations
    cpu_val = f"{(local_now.minute * 7 + local_now.second) % 18 + 7.2:.1f}%"
    mem_val = f"{4.2 + ((local_now.minute * 9) % 30) / 10.0:.2f} GB / 16.0 GB"

    # Rotating tasks depending on the day of the week
    targets = [
        "Web App PenTesting [OWASP-T10]",
        "JWT Exploit Research [active]",
        "Automated CVE-2025 Payload Scan",
        "Blind SQL Injection Mapping",
        "Exploit Payload Development",
        "CTF Challenge Playground",
        "Red Team Infra Configuration"
    ]
    current_target = targets[local_now.weekday()]

    # Dimensions: 495x195 (exactly matches streak card)
    width = 495
    height = 195
    
    bg_color = "#0D1117"
    border_color = "#30363D"
    text_color = "#c9d1d9"
    accent_color = "#6366f1"
    sub_color = "#8b949e"
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">')
    
    # Gradient for card border
    svg.append('  <defs>')
    svg.append('    <linearGradient id="status-card-border" x1="0%" y1="0%" x2="100%" y2="100%">')
    svg.append('      <stop offset="0%" stop-color="#30363D" />')
    svg.append('      <stop offset="50%" stop-color="#6366f1" stop-opacity="0.4" />')
    svg.append('      <stop offset="100%" stop-color="#30363D" />')
    svg.append('    </linearGradient>')
    svg.append('  </defs>')

    # Background and border
    svg.append(f'  <rect width="{width}" height="{height}" rx="6" fill="{bg_color}" stroke="url(#status-card-border)" stroke-width="1.2"/>')
    
    # CSS Styles for animations and terminal font
    font_family = 'Consolas, "Fira Code", Monaco, monospace'
    svg.append('  <style>')
    svg.append(f'    .term-lbl {{ font-family: {font_family}; font-size: 11px; fill: {sub_color}; }}')
    svg.append(f'    .term-val {{ font-family: {font_family}; font-size: 11px; fill: {text_color}; }}')
    svg.append(f'    .term-cmd {{ font-family: {font_family}; font-size: 11px; fill: {accent_color}; font-weight: bold; }}')
    svg.append(f'    .term-bar {{ font-family: {font_family}; font-size: 11px; fill: {accent_color}; }}')
    svg.append(f'    .window-title {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size: 10px; fill: {sub_color}; }}')
    svg.append('    .cursor {')
    svg.append('      animation: blink 1.2s step-end infinite;')
    svg.append('      fill: #6366f1;')
    svg.append('    }')
    svg.append('    .pulse-dot {')
    svg.append('      animation: pulse 1.8s ease-in-out infinite;')
    svg.append('    }')
    svg.append('    @keyframes blink {')
    svg.append('      from, to { opacity: 0; }')
    svg.append('      50% { opacity: 1; }')
    svg.append('    }')
    svg.append('    @keyframes pulse {')
    svg.append('      0% { opacity: 0.4; transform: scale(0.95); }')
    svg.append('      50% { opacity: 1; transform: scale(1.15); }')
    svg.append('      100% { opacity: 0.4; transform: scale(0.95); }')
    svg.append('    }')
    svg.append('  </style>')
    
    # Window Header (Mac terminal-style)
    svg.append('  <circle cx="15" cy="15" r="4" fill="#f87171" opacity="0.8"/>')
    svg.append('  <circle cx="27" cy="15" r="4" fill="#fbbf24" opacity="0.8"/>')
    svg.append('  <circle cx="39" cy="15" r="4" fill="#34d399" opacity="0.8"/>')
    svg.append(f'  <text x="60" y="18" class="window-title">system_monitor.sh</text>')
    svg.append(f'  <line x1="0" y1="28" x2="{width}" y2="28" stroke="{border_color}" stroke-width="1"/>')
    
    # Command prompt
    svg.append(f'  <text x="15" y="47" class="term-cmd">$ ./stealthmoud --status</text>')
    
    # Terminal text
    svg.append(f'  <text x="15" y="68" class="term-lbl">TIMEZONE     :</text>')
    svg.append(f'  <text x="120" y="68" class="term-val">Europe/Rome (UTC+2)</text>')
    
    svg.append(f'  <text x="15" y="86" class="term-lbl">SYSTEM SYNC  :</text>')
    svg.append(f'  <text x="120" y="86" class="term-val">{date_str} {time_str}</text>')
    svg.append('  <rect x="238" y="77" width="2" height="10" class="cursor"/>')  # Blinking cursor right next to date-time
    
    svg.append(f'  <text x="15" y="104" class="term-lbl">YEAR PROGRESS:</text>')
    svg.append(f'  <text x="120" y="104" class="term-bar">{bar}</text>')
    svg.append(f'  <text x="260" y="104" class="term-val">{progress:.2f}%</text>')
    
    # Shorten commit message if too long for terminal
    term_commit = latest_commit_msg
    if len(term_commit) > 35:
        term_commit = term_commit[:32] + "..."
        
    svg.append(f'  <text x="15" y="122" class="term-lbl">LAST UPDATE  :</text>')
    svg.append(f'  <text x="120" y="122" class="term-val">{term_commit}</text>')
    
    svg.append(f'  <text x="15" y="140" class="term-lbl">CPU / MEM    :</text>')
    svg.append(f'  <text x="120" y="140" class="term-val">{cpu_val} | {mem_val}</text>')
    
    # Bottom status bar
    svg.append(f'  <rect x="0" y="170" width="{width}" height="25" fill="#161b22" opacity="0.3"/>')
    svg.append(f'  <line x1="0" y1="170" x2="{width}" y2="170" stroke="{border_color}" stroke-width="1"/>')
    
    # Pulsing status heartbeat dot
    svg.append('  <g style="transform-origin: 15px 182px; transform-box: fill-box;" class="pulse-dot">')
    svg.append('    <circle cx="15" cy="182" r="3.5" fill="#34d399"/>')
    svg.append('  </g>')
    
    svg.append(f'  <text x="26" y="185" class="term-val">Active: {current_target}</text>')
    svg.append(f'  <text x="{width - 90}" y="185" class="term-lbl">Uptime: {uptime_str}</text>')
    
    svg.append('</svg>')
    
    svg_content = "\n".join(svg)
    try:
        with open("status.svg", "w") as f:
            f.write(svg_content)
        print("Success! status.svg generated.")
        return True
    except Exception as e:
        print(f"Error writing status.svg: {e}")
        return False
