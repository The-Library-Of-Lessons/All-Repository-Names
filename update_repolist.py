import urllib.request
import json
import os

def fetch_repos(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Python-Urllib')
        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    break
                data = json.loads(response.read().decode())
                if not data:
                    break
                repos.extend([repo['name'] for repo in data])
                if len(data) < 100:
                    break
                page += 1
        except Exception as e:
            print(f"Error fetching repos: {e}")
            break
    return repos

def main():
    username = "The-Library-Of-Lessons"
    repo_list_file = "RepoList.md"

    # 1. Fetch remote repos
    remote_repos = fetch_repos(username)

    # 2. Read existing repos from RepoList.md
    if os.path.exists(repo_list_file):
        with open(repo_list_file, 'r') as f:
            existing_repos = {line.strip() for line in f if line.strip()}
    else:
        existing_repos = set()

    # 3. Filter out 'All-Repository-Names' and find missing ones
    new_repos = []
    for repo in remote_repos:
        if repo == "All-Repository-Names":
            continue
        if repo not in existing_repos:
            new_repos.append(repo)

    # 4. Append missing repos
    if new_repos:
        print(f"Adding {len(new_repos)} new repositories: {', '.join(new_repos)}")
        with open(repo_list_file, 'a') as f:
            # Ensure there is a newline if the file doesn't end with one
            if os.path.exists(repo_list_file) and os.path.getsize(repo_list_file) > 0:
                with open(repo_list_file, 'rb+') as rb:
                    rb.seek(-1, os.SEEK_END)
                    if rb.read(1) != b'\n':
                        f.write('\n')

            for repo in new_repos:
                f.write(f"{repo}\n")
    else:
        print("No new repositories to add.")

if __name__ == "__main__":
    main()
