from src.contributions import generate_svg
from src.streak import fetch_streak
from src.system_status import fetch_recent_commits, update_readme_commits, generate_status_svg

def main():
    username = "stealthmoud"
    
    # Run the updates sequenially
    print("Refreshing profile contribution grid...")
    generate_svg(username)
    
    print("Fetching and cleaning streak card stats...")
    fetch_streak(username)
    
    print("Updating system logs and generating status monitor...")
    commits = fetch_recent_commits(username)
    update_readme_commits(commits)
    
    latest_msg = commits[0][1] if commits else "initial setup"
    latest_repo = commits[0][0] if commits else None
    generate_status_svg(latest_msg, latest_repo)
    
    print("Profile synchronization completed successfully.")

if __name__ == "__main__":
    main()
