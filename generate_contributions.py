import os
import requests

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

if not USERNAME or not TOKEN:
    raise EnvironmentError("Missing GITHUB_USERNAME or GITHUB_TOKEN environment variable.")

headers = {"Authorization": f"token {TOKEN}"}

def get_contributed_repos():
    repos = set()
    page = 1

    while True:
        url = f"https://api.github.com/users/{USERNAME}/events/public?page={page}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            break

        events = resp.json()
        if not events:
            break

        for event in events:
            repo = event.get("repo", {}).get("name")
            if repo:
                repos.add(repo)

        page += 1

    return sorted(repos)

def format_repo_list(repos):
    lines = ["> Projects that i worked on / contributed to:\n"]
    for repo in repos:
        lines.append(f"- 🔗 [https://github.com/{repo}](https://github.com/{repo})")
    return "\n".join(lines)

def update_readme(new_projects_md):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start_token = "> Projects that i worked on / contributed to:"
    start_idx = content.find(start_token)

    if start_idx == -1:
        print("❌ Section not found in README.md")
        return

    end_idx = content.find("---", start_idx)
    if end_idx == -1:
        end_idx = len(content)

    updated = content[:start_idx] + new_projects_md + "\n\n" + content[end_idx:]
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

    print("✅ README.md updated successfully.")

if __name__ == "__main__":
    repos = get_contributed_repos()
    new_md = format_repo_list(repos)
    update_readme(new_md)
