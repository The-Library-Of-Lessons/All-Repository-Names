import os
import json
import urllib.request
import subprocess
import sys

# Try to import content, but provide a message if it's missing
try:
    from missing_topics_content import TOPICS_CONTENT
except ImportError:
    print("Error: missing_topics_content.py not found. Please ensure it is in the same directory.")
    TOPICS_CONTENT = {}

def get_github_repos(org_name, token=None):
    """Fetches the list of repository names for the given organization/user."""
    url = f"https://api.github.com/users/{org_name}/repos?per_page=100"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            repos = json.loads(response.read().decode())
            return [repo['name'] for repo in repos]
    except Exception as e:
        print(f"Error fetching repos: {e}")
        # Fallback to local discovery if API fails or is rate-limited
        return [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]

def create_github_repo(org_name, repo_name, token):
    """Creates a new repository on GitHub (requires a valid GITHUB_TOKEN)."""
    if not token:
        print(f"Skipping remote repository creation for '{repo_name}' as GITHUB_TOKEN is not set.")
        return False

    url = f"https://api.github.com/user/repos" # Use /orgs/{org_name}/repos if it's an organization
    # To determine if org_name is a user or org, we'd need more logic.
    # Defaulting to user-owned for simplicity or checking if org exists.

    data = json.dumps({
        "name": repo_name,
        "auto_init": False,
        "description": f"Interactive guide for {repo_name.replace('-', ' ')}"
    }).encode('utf-8')

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 201:
                print(f"Successfully created GitHub repository: {repo_name}")
                return True
    except urllib.error.HTTPError as e:
        if e.code == 422: # Already exists or other validation error
            print(f"Note: Repository '{repo_name}' might already exist on GitHub or has invalid name.")
        else:
            print(f"Error creating repository '{repo_name}': {e}")
    except Exception as e:
        print(f"Failed to create repository '{repo_name}': {e}")
    return False

def setup_local_repo(topic_dir):
    """Initializes a local git repository and sets the branch to main."""
    try:
        # Check if already a git repo
        if not os.path.exists(os.path.join(topic_dir, ".git")):
            subprocess.run(['git', 'init', topic_dir], check=True, capture_output=True)
            # Switch to main branch
            subprocess.run(['git', '-C', topic_dir, 'checkout', '-b', 'main'], check=True, capture_output=True)
            print(f"Initialized local git repository in {topic_dir} and set branch to 'main'.")
    except Exception as e:
        print(f"Error setting up local git repo in {topic_dir}: {e}")

def sync():
    org_name = "The-Library-Of-Lessons"
    repolist_file = 'RepoList.md'
    token = os.environ.get("GITHUB_TOKEN")

    if not os.path.exists(repolist_file):
        print(f"Error: {repolist_file} not found.")
        return

    if not os.path.exists('template.html'):
        print("Error: template.html not found. Cannot generate guides.")
        return

    with open(repolist_file, 'r') as f:
        topics = [line.strip() for line in f if line.strip()]

    # Exclude 'All-Repository-Names' as per guidelines
    existing_repos = get_github_repos(org_name, token)

    for topic in topics:
        if topic == "All-Repository-Names":
            continue

        if topic not in existing_repos:
            print(f"\n--- Syncing missing topic: {topic} ---")

            # 1. Create GitHub Repo (if token provided)
            create_github_repo(org_name, topic, token)

            # 2. Create local directory
            if not os.path.exists(topic):
                os.makedirs(topic)
                print(f"Created local directory: {topic}")

            # 3. Setup local git and branch
            setup_local_repo(topic)

            # 4. Generate Content
            content = TOPICS_CONTENT.get(topic)
            if not content:
                print(f"Warning: No predefined content found for {topic} in missing_topics_content.py")
                continue

            temp_content_file = f"temp_content_{topic}.json"
            with open(temp_content_file, 'w') as f:
                json.dump(content, f, indent=2)

            try:
                subprocess.run(['python3', 'generator.py', temp_content_file], check=True)
                print(f"Successfully generated index.html for {topic}")
            except subprocess.CalledProcessError as e:
                print(f"Error running generator for {topic}: {e}")
            finally:
                if os.path.exists(temp_content_file):
                    os.remove(temp_content_file)

if __name__ == "__main__":
    sync()
