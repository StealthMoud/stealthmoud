import urllib.request

def fetch_streak(username="stealthmoud", filename="streak.svg"):
    # Fech raw streak stats from demolab
    url = f"https://streak-stats.demolab.com/?user={username}&hide_border=true&background=0d1117&stroke=6366f1&ring=6366f1&fire=818cf8&currStreakLabel=6366f1&currStreakNum=ffffff&sideNums=ffffff&sideLabels=c9d1d9&dates=c9d1d9"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode('utf-8')
            
            # Replaces the animation to prevent Safari rendering glitchs
            content = content.replace("animation: currstreak 0.6s linear forwards", "opacity: 0; animation: fadein 0.5s linear forwards 0.9s")
            
            with open(filename, "w") as f:
                f.write(content)
        print(f"Success! {filename} generated and post-processed.")
        return True
    except Exception as e:
        print(f"Error fetching/processing streak stats: {e}")
        return False
