import os
import requests

# Preia variabilele de mediu
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

if not USERNAME or not TOKEN:
    raise EnvironmentError("Missing GITHUB_USERNAME or GITHUB_TOKEN environment variable.")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_contributed_repos():
    print(f"🔍 Fetching events for user: {USERNAME}")
    repos = set()
    page = 1

    while True:
        url = f"https://api.github.com/users/{USERNAME}/events/public?page={page}"
        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            print(f"⚠️ Error fetching events: {resp.status_code}")
            break

        events = resp.json()
        if not events:
            break

        for event in events:
            repo = event.get("repo", {}).get("name")
            if repo:
                repos.add(repo)

        page += 1

    print(f"✅ Found {len(repos)} unique repositories.")
    return sorted(repos)

def format_repo_list(repos):
    lines = []
    lines.append("<!-- CONTRIBUTIONS-START -->")
    lines.append("\n> Projects that I worked on / contributed to:\n")

    for repo in repos:
        lines.append(f"- 🔗 [https://github.com/{repo}](https://github.com/{repo})")

    lines.append("<!-- CONTRIBUTIONS-END -->")
    return "\n".join(lines)

def update_readme(new_section):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start_token = "<!-- CONTRIBUTIONS-START -->"
    end_token = "<!-- CONTRIBUTIONS-END -->"

    start_idx = content.find(start_token)
    end_idx = content.find(end_token)

    if start_idx == -1 or end_idx == -1:
        print("❌ CONTRIBUTIONS section markers not found in README.md.")
        return

    updated = (
        content[:start_idx].rstrip()
        + "\n"
        + new_section
        + "\n"
        + content[end_idx + len(end_token):]
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

    print("✅ README.md updated successfully.")

if __name__ == "__main__":
    repos = get_contributed_repos()
    new_md = format_repo_list(repos)
    update_readme(new_md)
