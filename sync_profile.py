"""Entry point for refreshing the GitHub profile README and its SVG assets.

Regenerates the contribution grid, streak card, stats card, languages card
and status monitor, then rewrites README.md to point at the new files.
Each stage is timestamped so previously published assets stay valid via
GitHub's CDN cache until the README swap completes.
"""

import time
import os
import glob
import sys
from src.contributions import generate_svg
from src.streak import fetch_streak
from src.system_status import fetch_recent_commits, update_readme_commits, generate_status_svg
from src.github_stats import fetch_stats_data, generate_stats_svg, generate_languages_svg

USERNAME = "stealthmoud"
ASSET_PATTERNS = ["contributions_*.svg", "streak_*.svg", "status_*.svg", "stats_*.svg", "languages_*.svg"]


def clean_old_assets(keep_suffixes=()):
    """Remove previously generated SVGs, keeping only the given filenames."""
    for pattern in ASSET_PATTERNS:
        for filepath in glob.glob(pattern):
            if any(suffix in filepath for suffix in keep_suffixes):
                continue
            try:
                os.remove(filepath)
                print(f"Removed old asset: {filepath}")
            except OSError as e:
                print(f"Error removing {filepath}: {e}")


def abort(message, *files_to_remove):
    """Print an error, discard any partially generated assets, and exit."""
    print(f"Error: {message}")
    for filepath in files_to_remove:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    sys.exit(1)


def main():
    timestamp = int(time.time())
    contributions_file = f"contributions_{timestamp}.svg"
    streak_file = f"streak_{timestamp}.svg"
    status_file = f"status_{timestamp}.svg"
    stats_file = f"stats_{timestamp}.svg"
    languages_file = f"languages_{timestamp}.svg"

    print("Refreshing profile contribution grid...")
    if not generate_svg(USERNAME, contributions_file):
        abort("Failed to generate contributions grid.")

    print("Fetching and processing streak card stats...")
    if not fetch_streak(USERNAME, streak_file):
        abort("Failed to fetch streak card stats.", contributions_file)

    print("Fetching GitHub profile stats and language breakdown...")
    try:
        stats_data = fetch_stats_data(USERNAME)
    except Exception as e:
        abort(f"Failed to fetch GitHub stats data: {e}", contributions_file, streak_file)

    print("Generating GitHub stats card...")
    if not generate_stats_svg(stats_data, stats_file):
        abort("Failed to generate stats SVG.", contributions_file, streak_file)

    print("Generating top languages card...")
    if not generate_languages_svg(stats_data, languages_file):
        abort("Failed to generate languages SVG.", contributions_file, streak_file, stats_file)

    print("Updating recent activity log and status monitor...")
    commits = fetch_recent_commits(USERNAME)

    # Rewrite README.md with the new timestamped asset links and latest commits
    update_readme_commits(commits, contributions_file, streak_file, status_file, stats_file, languages_file)

    latest_msg = commits[0][1] if commits else "initial update"
    latest_repo = commits[0][0] if commits else None

    if not generate_status_svg(latest_msg, latest_repo, status_file):
        abort("Failed to generate status SVG.", contributions_file, streak_file, stats_file, languages_file)

    # Only prune old assets once every new file has generated successfully
    clean_old_assets(keep_suffixes=[contributions_file, streak_file, status_file, stats_file, languages_file])
    print("Profile synchronization completed successfully.")


if __name__ == "__main__":
    main()
