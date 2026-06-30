import os
import json
import subprocess
import urllib.request
import urllib.parse
import sys

# Constants
GITHUB_USERNAME = 'The-Library-Of-Lessons'
REPO_LIST_FILE = 'RepoList.md'
TEMPLATE_FILE = 'template.html'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN') # Requires user to set this environment variable

def run_command(command, cwd=None):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e.stderr}")
        return None

def get_topics_from_md(filepath):
    """Reads topic slugs from the markdown file."""
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return []
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def get_existing_github_repos():
    """Fetches list of existing repositories for the organization/user."""
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return [repo['name'] for repo in data]
    except Exception as e:
        print(f"Warning: Could not fetch GitHub repos ({e}). Using empty list as fallback.")
        return []

def create_github_repo(repo_name):
    """Creates a new repository on GitHub via the API."""
    if not GITHUB_TOKEN:
        print(f"[SIMULATION] Skipping remote creation of '{repo_name}' (GITHUB_TOKEN not set).")
        return True

    url = "https://api.github.com/user/repos" # Or orgs/{org}/repos if applicable
    data = json.dumps({
        "name": repo_name,
        "description": f"Interactive guide for {repo_name.replace('-', ' ')}",
        "auto_init": False
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', 'Mozilla/5.0')

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 201:
                print(f"Successfully created GitHub repository: {repo_name}")
                return True
    except Exception as e:
        print(f"Error creating repository '{repo_name}': {e}")
    return False

def setup_local_git_and_push(repo_name, directory):
    """Initializes local git, commits files, and pushes to main branch."""
    print(f"Setting up local repository in {directory}...")
    run_command("git init", cwd=directory)
    run_command("git add index.html", cwd=directory)
    run_command("git commit -m 'Initial commit: Generate interactive guide'", cwd=directory)
    run_command("git branch -M main", cwd=directory)

    if GITHUB_TOKEN:
        remote_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"
        run_command(f"git remote add origin {remote_url}", cwd=directory)
        print(f"Pushing to https://github.com/{GITHUB_USERNAME}/{repo_name}.git...")
        run_command("git push -u origin main", cwd=directory)
    else:
        print(f"[SIMULATION] git remote add origin https://github.com/{GITHUB_USERNAME}/{repo_name}.git")
        print(f"[SIMULATION] git push -u origin main")

def main():
    # 1. Analyze: Read desired topics
    topics = get_topics_from_md(REPO_LIST_FILE)
    if not topics: return

    # 2. Check: Fetch existing repos
    existing_repos = get_existing_github_repos()

    missing_topics = [t for t in topics if t not in existing_repos]
    print(f"Identified {len(missing_topics)} topics requiring new repositories.")

    if not missing_topics:
        print("All topics are currently synced with GitHub.")
        return

    # Import content data
    try:
        from missing_topics_content import MISSING_TOPICS_DATA
        from generator import generate_html
    except ImportError as e:
        print(f"Error: Missing required local scripts ({e}). Ensure generator.py and missing_topics_content.py are present.")
        return

    for topic in missing_topics:
        print(f"\n--- Processing: {topic} ---")
        content = MISSING_TOPICS_DATA.get(topic)
        if not content:
            print(f"  Skipping: No content data available for topic slug '{topic}'.")
            continue

        # 3. Create: Local directory and file
        os.makedirs(topic, exist_ok=True)
        output_file = os.path.join(topic, 'index.html')

        try:
            generate_html(content['topic_name'], content, TEMPLATE_FILE, output_file)
            print(f"  Generated interactive guide: {output_file}")

            # 4. GitHub Operations
            if create_github_repo(topic):
                setup_local_git_and_push(topic, topic)

        except Exception as e:
            print(f"  Failed to process {topic}: {e}")

if __name__ == "__main__":
    main()
