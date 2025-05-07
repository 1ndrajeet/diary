import os
import glob
from datetime import datetime
import subprocess

# Directory where the script runs (tmp folder as repository root)
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# Git branch to use (new repositories typically use 'main')
BRANCH = "main"

# GitHub repository URL for the diary (replace with your new repository)
REPO_URL = "https://github.com/1ndrajeet/diary.git"  # Update this

def get_today_filename():
    """Generate filename in DD-MM-YYYY.txt format."""
    return datetime.now().strftime("%d-%m-%Y.txt")

def create_today_file():
    """Create a file named DD-MM-YYYY.txt in the tmp directory."""
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    day_of_week = today.strftime("%A")
    note = "This is a daily diary entry. Add your thoughts or notes here!"
    
    content = f"Date: {date_str}\nDay: {day_of_week}\nNote: {note}\n"
    filename = os.path.join(REPO_DIR, get_today_filename())
    with open(filename, "w") as f:
        f.write(content)
    print(f"Created {filename}")
    return filename

def delete_old_txt_files(current_file):
    """Delete all .txt files except the current DD-MM-YYYY.txt in tmp."""
    txt_files = glob.glob(os.path.join(REPO_DIR, "*.txt"))
    for file in txt_files:
        if file != current_file:
            os.remove(file)
            print(f"Deleted {file}")

def ensure_git_setup():
    """Ensure the tmp directory is a Git repository connected to the remote."""
    try:
        os.chdir(REPO_DIR)
        # Check if .git exists
        if not os.path.exists(".git"):
            print("Initializing Git repository in tmp...")
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "remote", "add", "origin", REPO_URL], check=True)
            # Create an initial commit if the repo is empty
            with open("README.md", "w") as f:
                f.write("# Diary Repository\n\nThis repository stores daily diary entries.")
            subprocess.run(["git", "add", "README.md"], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

        # Verify remote URL
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
        if result.stdout.strip() != REPO_URL:
            print(f"Updating remote URL to {REPO_URL}")
            subprocess.run(["git", "remote", "set-url", "origin", REPO_URL], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error setting up Git repository: {e}")
        exit(1)

def git_commit_and_push(filename):
    """Add, commit, and push changes to GitHub using Git CLI."""
    try:
        # Change to the repository directory (tmp)
        os.chdir(REPO_DIR)

        # Check if the branch exists
        result = subprocess.run(["git", "rev-parse", "--verify", BRANCH], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Branch {BRANCH} does not exist. Creating it...")
            subprocess.run(["git", "checkout", "-b", BRANCH], check=True)

        # Git add
        relative_filename = os.path.basename(filename)
        # subprocess.run(["git", "add", relative_filename], check=True)
        subprocess.run(["git", "add", '.'])
        print("Git add completed")

        # Git commit
        commit_message = f"Update {relative_filename} for {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("Git commit completed")

        # Git push
        subprocess.run(["git", "push", "origin", BRANCH], check=True)
        print("Git push completed")

    except subprocess.CalledProcessError as e:
        print(f"Error during Git operation: {e}")
        exit(1)

def main():
    """Main function to orchestrate the process."""
    ensure_git_setup()
    filename = create_today_file()
    delete_old_txt_files(filename)
    git_commit_and_push(filename)

if __name__ == "__main__":
    main()