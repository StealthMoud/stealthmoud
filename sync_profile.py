import time
import os
import glob
import sys
from src.contributions import generate_svg
from src.streak import fetch_streak
from src.system_status import fetch_recent_commits, update_readme_commits, generate_status_svg

def clean_old_assets(keep_suffixes=[]):
    # Clean up old compiled SVGs to prevent accumulation
    for pattern in ["contributions_*.svg", "streak_*.svg", "status_*.svg"]:
        for filepath in glob.glob(pattern):
            if any(suffix in filepath for suffix in keep_suffixes):
                continue
            try:
                os.remove(filepath)
                print(f"Removed old asset: {filepath}")
            except Exception as e:
                print(f"Error removing {filepath}: {e}")

def main():
    username = "stealthmoud"
    
    # Generate timestamp for new file versions
    timestamp = int(time.time())
    contributions_file = f"contributions_{timestamp}.svg"
    streak_file = f"streak_{timestamp}.svg"
    status_file = f"status_{timestamp}.svg"
    
    print("Refreshing profile contribution grid...")
    if not generate_svg(username, contributions_file):
        print("Error: Failed to generate contributions grid.")
        sys.exit(1)
    
    print("Fetching and cleaning streak card stats...")
    if not fetch_streak(username, streak_file):
        print("Error: Failed to fetch streak card stats.")
        if os.path.exists(contributions_file):
            os.remove(contributions_file)
        sys.exit(1)
    
    print("Updating system logs and status monitor...")
    commits = fetch_recent_commits(username)
    
    # Update README with the new timestamped file links and recent commits
    update_readme_commits(commits, contributions_file, streak_file, status_file)
    
    latest_msg = commits[0][1] if commits else "initial update"
    latest_repo = commits[0][0] if commits else None
    
    if not generate_status_svg(latest_msg, latest_repo, status_file):
        print("Error: Failed to generate status SVG.")
        if os.path.exists(contributions_file):
            os.remove(contributions_file)
        if os.path.exists(streak_file):
            os.remove(streak_file)
        sys.exit(1)
    
    # Clean old timestamped files only after everything generated successfully
    clean_old_assets(keep_suffixes=[contributions_file, streak_file, status_file])
    print("Profile synchronization completed successfully.")

if __name__ == "__main__":
    main()
