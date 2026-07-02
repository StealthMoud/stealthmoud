import urllib.request
import re
import json
import datetime
import subprocess
import os

def fetch_recent_commits(username="stealthmoud"):
    # Fech recent commits from API with local git fallback
    token = os.getenv("GH_PAT")
    if token:
        url = f"https://api.github.com/users/{username}/events"
    else:
        url = f"https://api.github.com/users/{username}/events/public"
        
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
        
    commits_list = []
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            events = json.loads(response.read().decode())
            for event in events:
                if event.get("type") == "PushEvent":
                    repo_full_name = event.get("repo", {}).get("name", "")
                    repo_name = re.sub(rf"^{username}/", "", repo_full_name, flags=re.IGNORECASE)
                    
                    payload = event.get("payload", {})
                    sha = payload.get("head")
                    if not sha:
                        continue
                        
                    # Fetch commit details to get the message (since GitHub Events API removed commits payload)
                    try:
                        commit_url = f"https://api.github.com/repos/{repo_full_name}/commits/{sha}"
                        commit_req = urllib.request.Request(commit_url, headers={"User-Agent": "Mozilla/5.0"})
                        if token:
                            commit_req.add_header("Authorization", f"Bearer {token}")
                        with urllib.request.urlopen(commit_req, timeout=3) as commit_res:
                            commit_data = json.loads(commit_res.read().decode())
                            message = commit_data.get("commit", {}).get("message", "").split("\n")[0]
                            if len(message) > 60:
                                message = message[:57] + "..."
                            commits_list.append((repo_name, message, sha))
                    except Exception as ce:
                        print(f"Error fetching commit details for {repo_full_name}@{sha}: {ce}")
                        # Fallback if commit API details fetch fails
                        commits_list.append((repo_name, "pushed changes", sha))
                        
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

def update_readme_commits(commits, contributions_file, streak_file, status_file, stats_file, languages_file):
    try:
        with open("README.md", "r") as f:
            content = f.read()
        
        new_content = content
        
        # 1. Update recent commits section if we have commits
        if commits:
            formatted_commits = ["### System Logs"]
            for repo, msg, sha in commits:
                short_sha = sha[:7]
                commit_url = f"https://github.com/StealthMoud/{repo}/commit/{sha}"
                formatted_commits.append(f"- **{repo}** — `{msg}` [#{short_sha}]({commit_url})")
            
            commits_text = "\n".join(formatted_commits)
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
        # Custom Stats Card replacement (from Vercel URL or our raw github URL)
        new_content = re.sub(
            r'src="(?:https://github-readme-stats\.vercel\.app/api\?username=stealthmoud[^"]*|https://raw\.githubusercontent\.com/StealthMoud/stealthmoud/main/stats(?:_[^"]+)?\.svg(?:\?v=\d+)?)"',
            f'src="https://raw.githubusercontent.com/StealthMoud/stealthmoud/main/{stats_file}"',
            new_content
        )
        # Custom Languages Card replacement (from Vercel URL or our raw github URL)
        new_content = re.sub(
            r'src="(?:https://github-readme-stats\.vercel\.app/api/top-langs/[^"]*|https://raw\.githubusercontent\.com/StealthMoud/stealthmoud/main/languages(?:_[^"]+)?\.svg(?:\?v=\d+)?)"',
            f'src="https://raw.githubusercontent.com/StealthMoud/stealthmoud/main/{languages_file}"',
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
        # Memory metrics parsing using MemAvailable for accuracy
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
        mem_total_match = re.search(r"MemTotal:\s+(\d+)\s+kB", meminfo)
        mem_free_match = re.search(r"MemFree:\s+(\d+)\s+kB", meminfo)
        mem_avail_match = re.search(r"MemAvailable:\s+(\d+)\s+kB", meminfo)
        buffers_match = re.search(r"Buffers:\s+(\d+)\s+kB", meminfo)
        cached_match = re.search(r"Cached:\s+(\d+)\s+kB", meminfo)
        
        if mem_total_match:
            total = int(mem_total_match.group(1)) / 1024 / 1024
            if mem_avail_match:
                avail = int(mem_avail_match.group(1)) / 1024 / 1024
                used = total - avail
            elif mem_free_match:
                free = int(mem_free_match.group(1)) / 1024 / 1024
                buffers = int(buffers_match.group(1) if buffers_match else 0) / 1024 / 1024
                cached = int(cached_match.group(1) if cached_match else 0) / 1024 / 1024
                used = total - free - buffers - cached
            else:
                used = 0.0
            mem_str = f"{max(used, 0.0):.2f} GB / {total:.1f} GB"
            
        # CPU usage via /proc/stat (real-time utilization over 100ms delta)
        try:
            def get_cpu_times():
                with open("/proc/stat", "r") as f:
                    line = f.readline().split()
                # Sum columns excluding "cpu" label
                total_time = sum(map(float, line[1:]))
                idle_time = float(line[4]) # idle column index 4
                return total_time, idle_time

            t1_total, t1_idle = get_cpu_times()
            import time
            time.sleep(0.1)
            t2_total, t2_idle = get_cpu_times()

            total_delta = t2_total - t1_total
            idle_delta = t2_idle - t1_idle
            if total_delta > 0:
                cpu_pct = (total_delta - idle_delta) / total_delta * 100
                cpu_str = f"{min(max(cpu_pct, 0.0), 100.0):.1f}%"
            else:
                cpu_str = "0.0%"
        except Exception:
            # Fallback to loadavg
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
        stats = {}
        for line in lines:
            if "page size of" in line:
                page_size = int(re.search(r"page size of (\d+) bytes", line).group(1))
            else:
                match = re.search(r"Pages\s+([^:]+):\s+(\d+)", line)
                if match:
                    key, val = match.groups()
                    stats[key.strip()] = int(val.replace(".", ""))
                    
        # Real Apple used memory formula: active + wired + occupied by compressor
        active_pages = stats.get("active", 0)
        wired_pages = stats.get("wired down", 0)
        compressor_pages = stats.get("occupied by compressor", 0)
        
        used_gb = (active_pages + wired_pages + compressor_pages) * page_size / 1024 / 1024 / 1024
        mem_str = f"{used_gb:.2f} GB / {total_gb:.1f} GB"
        
        # CPU usage via top (real-time utilization)
        try:
            res = subprocess.run(["top", "-l", "1"], capture_output=True, text=True)
            for line in res.stdout.split("\n"):
                if "CPU usage:" in line:
                    matches = re.findall(r"(\d+\.\d+)%\s+idle", line)
                    if matches:
                        idle_pct = float(matches[0])
                        cpu_pct = 100.0 - idle_pct
                        cpu_str = f"{min(max(cpu_pct, 0.0), 100.0):.1f}%"
                        break
        except Exception:
            # Fallback to sysctl loadavg
            res = subprocess.run(["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True)
            loads = re.findall(r"\d+\.\d+", res.stdout)
            load_val = float(loads[0]) if loads else 0.5
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
    
    # Gradient definitions for border and progress bar
    svg.append('  <defs>')
    svg.append('    <linearGradient id="status-card-border" x1="0%" y1="0%" x2="100%" y2="100%">')
    svg.append('      <stop offset="0%" stop-color="#30363D" />')
    svg.append('      <stop offset="50%" stop-color="#6366f1" stop-opacity="0.4" />')
    svg.append('      <stop offset="100%" stop-color="#30363D" />')
    svg.append('    </linearGradient>')
    svg.append('    <linearGradient id="progress-gradient" x1="0%" y1="0%" x2="100%" y2="0%">')
    svg.append('      <stop offset="0%" stop-color="#6366f1" />')
    svg.append('      <stop offset="100%" stop-color="#9a93ff" />')
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
    svg.append(f'    .window-title {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size: 10px; fill: {sub_color}; animation: fade-in 0.5s ease-out 0.2s both; }}')
    svg.append('    .win-btn {')
    svg.append('      animation: slide-down 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.2) both;')
    svg.append('      transform-box: fill-box;')
    svg.append('      transform-origin: center;')
    svg.append('    }')
    svg.append('    .window-divider {')
    svg.append('      animation: scale-x 0.5s cubic-bezier(0.175, 0.885, 0.32, 1) 0.25s both;')
    svg.append('      transform-box: fill-box;')
    svg.append('      transform-origin: center;')
    svg.append('    }')
    svg.append('    .term-line {')
    svg.append('      animation: term-slide 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.1) both;')
    svg.append('      transform-box: fill-box;')
    svg.append('      transform-origin: left center;')
    svg.append('    }')
    svg.append('    .bar-fill {')
    svg.append('      animation: bar-grow 1s cubic-bezier(0.1, 0.8, 0.2, 1) 0.6s both;')
    svg.append('      transform-box: fill-box;')
    svg.append('      transform-origin: left center;')
    svg.append('    }')
    svg.append('    .bottom-bar {')
    svg.append('      animation: slide-up 0.5s ease-out 0.9s both;')
    svg.append('      transform-box: fill-box;')
    svg.append('      transform-origin: bottom center;')
    svg.append('    }')
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
    svg.append('    @keyframes slide-down {')
    svg.append('      from { opacity: 0; transform: translateY(-4px); }')
    svg.append('      to { opacity: 1; transform: translateY(0); }')
    svg.append('    }')
    svg.append('    @keyframes slide-up {')
    svg.append('      from { opacity: 0; transform: translateY(4px); }')
    svg.append('      to { opacity: 1; transform: translateY(0); }')
    svg.append('    }')
    svg.append('    @keyframes fade-in {')
    svg.append('      from { opacity: 0; }')
    svg.append('      to { opacity: 1; }')
    svg.append('    }')
    svg.append('    @keyframes scale-x {')
    svg.append('      from { transform: scaleX(0); }')
    svg.append('      to { transform: scaleX(1); }')
    svg.append('    }')
    svg.append('    @keyframes term-slide {')
    svg.append('      from { opacity: 0; transform: translateX(-8px); }')
    svg.append('      to { opacity: 1; transform: translateX(0); }')
    svg.append('    }')
    svg.append('    @keyframes bar-grow {')
    svg.append('      from { transform: scaleX(0); }')
    svg.append('      to { transform: scaleX(1); }')
    svg.append('    }')
    svg.append('  </style>')
    
    # Window Header (Mac terminal-style with staggered slide-down)
    svg.append('  <circle cx="15" cy="15" r="4" fill="#f87171" opacity="0.8" class="win-btn" style="animation-delay: 0.05s;"/>')
    svg.append('  <circle cx="27" cy="15" r="4" fill="#fbbf24" opacity="0.8" class="win-btn" style="animation-delay: 0.1s;"/>')
    svg.append('  <circle cx="39" cy="15" r="4" fill="#34d399" opacity="0.8" class="win-btn" style="animation-delay: 0.15s;"/>')
    svg.append(f'  <text x="60" y="18" class="window-title">system_monitor.sh</text>')
    svg.append(f'  <line x1="0" y1="28" x2="{width}" y2="28" stroke="{border_color}" stroke-width="1" class="window-divider"/>')
    
    # Command prompt
    svg.append(f'  <text x="15" y="47" class="term-cmd term-line" style="animation-delay: 0.25s;">$ ./stealthmoud --status</text>')
    
    # Terminal text lines (staggered entries)
    svg.append(f'  <text x="15" y="68" class="term-lbl term-line" style="animation-delay: 0.35s;">TIMEZONE     :</text>')
    svg.append(f'  <text x="120" y="68" class="term-val term-line" style="animation-delay: 0.35s;">Europe/Rome (UTC+2)</text>')
    
    svg.append(f'  <text x="15" y="86" class="term-lbl term-line" style="animation-delay: 0.45s;">SYSTEM SYNC  :</text>')
    svg.append(f'  <text x="120" y="86" class="term-val term-line" style="animation-delay: 0.45s;">{date_str} {time_str}<tspan fill="{accent_color}" class="cursor">█</tspan></text>')
    
    svg.append(f'  <text x="15" y="104" class="term-lbl term-line" style="animation-delay: 0.55s;">YEAR PROGRESS:</text>')
    # Modern glowing progress bar instead of ASCII block text
    svg.append(f'  <rect x="120" y="97" width="130" height="8" rx="4" fill="#161b22" stroke="#30363D" stroke-width="0.8" class="term-line" style="animation-delay: 0.55s;"/>')
    svg.append(f'  <rect x="120" y="97" width="{130 * progress / 100}" height="8" rx="4" fill="url(#progress-gradient)" class="bar-fill"/>')
    svg.append(f'  <text x="260" y="104" class="term-val term-line" style="animation-delay: 0.55s;">{progress:.2f}%</text>')
    
    # Shorten commit message if too long for terminal
    term_commit = latest_commit_msg
    if len(term_commit) > 35:
        term_commit = term_commit[:32] + "..."
        
    svg.append(f'  <text x="15" y="122" class="term-lbl term-line" style="animation-delay: 0.65s;">LAST UPDATE  :</text>')
    svg.append(f'  <text x="120" y="122" class="term-val term-line" style="animation-delay: 0.65s;">{term_commit}</text>')
    
    svg.append(f'  <text x="15" y="140" class="term-lbl term-line" style="animation-delay: 0.75s;">CPU / MEM    :</text>')
    svg.append(f'  <text x="120" y="140" class="term-val term-line" style="animation-delay: 0.75s;">{cpu_val} | {mem_val}</text>')
    
    # Bottom status bar
    svg.append(f'  <rect x="0" y="170" width="{width}" height="25" fill="#161b22" opacity="0.3" class="bottom-bar"/>')
    svg.append(f'  <line x1="0" y1="170" x2="{width}" y2="170" stroke="{border_color}" stroke-width="1" class="bottom-bar"/>')
    
    # Pulsing status heartbeat dot
    svg.append('  <g style="transform-origin: 15px 182px; transform-box: fill-box;" class="pulse-dot bottom-bar">')
    svg.append('    <circle cx="15" cy="182" r="3.5" fill="#34d399"/>')
    svg.append('  </g>')
    
    svg.append(f'  <text x="26" y="185" class="term-val bottom-bar" style="animation-delay: 0.95s;">Active: {current_target}</text>')
    svg.append(f'  <text x="{width - 15}" y="185" class="term-lbl bottom-bar" text-anchor="end" style="animation-delay: 0.95s;">Uptime: {uptime_str}</text>')
    
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
