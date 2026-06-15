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

def update_readme_commits(commits, contributions_file, streak_file, status_file):
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
        
        # 1. Update recent commits section
        pattern = r"<!-- RECENT_COMMITS_START -->.*?<!-- RECENT_COMMITS_END -->"
        replacement = f"<!-- RECENT_COMMITS_START -->\n\n{commits_text}\n\n<!-- RECENT_COMMITS_END -->"
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 2. Cache-bust the SVG links by updating filenames
        new_content = re.sub(
            r'src="https://raw\.githubusercontent\.com/StealthMoud/stealthmoud/main/contributions(?:_[^"]+)?\.svg(?:\?v=\d+)?"',
            f'src="https://raw.githubusercontent.com/StealthMoud/stealthmoud/main/{contributions_file}"',
            new_content
        )
        new_content = re.sub(
            r'src="https://raw\.githubusercontent\.com/StealthMoud/stealthmoud/main/streak(?:_[^"]+)?\.svg(?:\?v=\d+)?"',
            f'src="https://raw.githubusercontent.com/StealthMoud/stealthmoud/main/{streak_file}"',
            new_content
        )
        new_content = re.sub(
            r'src="https://raw\.githubusercontent\.com/StealthMoud/stealthmoud/main/status(?:_[^"]+)?\.svg(?:\?v=\d+)?"',
            f'src="https://raw.githubusercontent.com/StealthMoud/stealthmoud/main/{status_file}"',
            new_content
        )
        
        with open("README.md", "w") as f:
            f.write(new_content)
        print("Success! README.md updated with recent commits and cache-busted SVG paths.")
    except Exception as e:
        print(f"Error updating README.md: {e}")

def get_real_uptime():
    # Try to calculate repository age from first git commit
    try:
        import subprocess
        cmd = ["git", "log", "--reverse", "--format=%ct"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split("\n")
        if lines and lines[0]:
            first_commit_ts = int(lines[0].strip())
            now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
            uptime_seconds = now_ts - first_commit_ts
            uptime_days = int(uptime_seconds // 86400)
            uptime_hours = int((uptime_seconds % 86400) // 3600)
            uptime_mins = int((uptime_seconds % 3600) // 60)
            return f"{uptime_days}d {uptime_hours}h {uptime_mins}m"
    except Exception:
        pass

    # Try Linux proc if git query fails
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.read().split()[0])
        uptime_days = int(uptime_seconds // 86400)
        uptime_hours = int((uptime_seconds % 86400) // 3600)
        uptime_mins = int((uptime_seconds % 3600) // 60)
        return f"{uptime_days}d {uptime_hours}h {uptime_mins}m"
    except Exception:
        pass
        
    # Try macOS sysctl if previous fails
    try:
        import subprocess
        res = subprocess.run(["sysctl", "-n", "kern.boottime"], capture_output=True, text=True)
        sec_match = re.search(r"sec = (\d+)", res.stdout)
        if sec_match:
            boot_time = float(sec_match.group(1))
            now_epoch = datetime.datetime.now(datetime.timezone.utc).timestamp()
            uptime_seconds = now_epoch - boot_time
            uptime_days = int(uptime_seconds // 86400)
            uptime_hours = int((uptime_seconds % 86400) // 3600)
            uptime_mins = int((uptime_seconds % 3600) // 60)
            return f"{uptime_days}d {uptime_hours}h {uptime_mins}m"
    except Exception:
        pass
        
    # Fallback to datetime baseline
    now = datetime.datetime.now()
    return f"{now.day}d {now.hour}h {now.minute}m"

def get_real_cpu_mem():
    cpu_str = "0.0%"
    mem_str = "0.0 GB / 0.0 GB"
    
    # 1. Try Linux proc file system
    try:
        # Memory metrics parsing
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
        mem_total_match = re.search(r"MemTotal:\s+(\d+)\s+kB", meminfo)
        mem_free_match = re.search(r"MemFree:\s+(\d+)\s+kB", meminfo)
        buffers_match = re.search(r"Buffers:\s+(\d+)\s+kB", meminfo)
        cached_match = re.search(r"Cached:\s+(\d+)\s+kB", meminfo)
        if mem_total_match and mem_free_match:
            total = int(mem_total_match.group(1)) / 1024 / 1024
            free = int(mem_free_match.group(1)) / 1024 / 1024
            buffers = int(buffers_match.group(1) if buffers_match else 0) / 1024 / 1024
            cached = int(cached_match.group(1) if cached_match else 0) / 1024 / 1024
            used = total - free - buffers - cached
            mem_str = f"{used:.2f} GB / {total:.1f} GB"
            
        # CPU loading
        with open("/proc/loadavg", "r") as f:
            load = f.read().split()
        import os
        cpu_count = os.cpu_count() or 2
        cpu_pct = (float(load[0]) / cpu_count) * 100
        cpu_str = f"{min(cpu_pct, 100.0):.1f}%"
        return cpu_str, mem_str
    except Exception:
        pass
        
    # 2. Try macOS system commands
    try:
        import subprocess
        import os
        # Total Memory
        res = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True)
        total_bytes = int(res.stdout.strip())
        total_gb = total_bytes / 1024 / 1024 / 1024
        
        # vm_stat page details
        res = subprocess.run(["vm_stat"], capture_output=True, text=True)
        lines = res.stdout.split("\n")
        page_size = 4096
        free_pages = 0
        inactive_pages = 0
        speculative_pages = 0
        for line in lines:
            if "page size of" in line:
                page_size = int(re.search(r"page size of (\d+) bytes", line).group(1))
            elif "Pages free:" in line:
                free_pages = int(line.split()[-1].replace(".", ""))
            elif "Pages inactive:" in line:
                inactive_pages = int(line.split()[-1].replace(".", ""))
            elif "Pages speculative:" in line:
                speculative_pages = int(line.split()[-1].replace(".", ""))
        used_gb = total_gb - ((free_pages + inactive_pages + speculative_pages) * page_size / 1024 / 1024 / 1024)
        mem_str = f"{max(used_gb, 0.1):.2f} GB / {total_gb:.1f} GB"
        
        # CPU load
        res = subprocess.run(["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True)
        load_val = float(res.stdout.split()[1])
        cpu_count = os.cpu_count() or 4
        cpu_pct = (load_val / cpu_count) * 100
        cpu_str = f"{min(cpu_pct, 100.0):.1f}%"
        return cpu_str, mem_str
    except Exception:
        pass
        
    # Fallback to simulated variables if hardware checks fail
    now = datetime.datetime.now()
    cpu_sim = f"{(now.minute * 7 + now.second) % 18 + 7.2:.1f}%"
    mem_sim = f"{4.2 + ((now.minute * 9) % 30) / 10.0:.2f} GB / 16.0 GB"
    return cpu_sim, mem_sim

def generate_status_svg(latest_commit_msg, latest_repo=None, filename="status.svg"):
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

    # Get real hardware metrics
    uptime_str = get_real_uptime()
    cpu_val, mem_val = get_real_cpu_mem()

    # Dynamic target based on latest repository action
    if latest_repo:
        current_target = f"Working on {latest_repo}"
    else:
        # Rotating targets depending on the day of the week
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
    svg.append(f'  <text x="{width - 15}" y="185" class="term-lbl" text-anchor="end">Uptime: {uptime_str}</text>')
    
    svg.append('</svg>')
    
    svg_content = "\n".join(svg)
    try:
        with open(filename, "w") as f:
            f.write(svg_content)
        print(f"Success! {filename} generated.")
        return True
    except Exception as e:
        print(f"Error writing {filename}: {e}")
        return False
