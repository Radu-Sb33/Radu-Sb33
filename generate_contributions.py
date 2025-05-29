import os
import requests

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

if not USERNAME or not TOKEN:
    raise EnvironmentError("GITHUB_USERNAME or GITHUB_TOKEN is not set!")

headers = {"Authorization": f"token {TOKEN}"}

def get_contributed_repos():
    repos = set()
    page = 1
    print("🔍 Caut evenimente publice pentru utilizatorul:", USERNAME)

    while True:
        url = f"https://api.github.com/users/{USERNAME}/events/public?page={page}"
        response = requests.get(url, headers=headers)
        events = response.json()

        if not events or response.status_code != 200:
            break

        for event in events:
            if "repo" in event:
                repos.add(event["repo"]["name"])
        page += 1

    return list(repos)

def get_repo_data(repo_full_name):
    repo_url = f"https://api.github.com/repos/{repo_full_name}"
    commits_url = f"{repo_url}/commits?author={USERNAME}"
    langs_url = f"{repo_url}/languages"

    repo_data = requests.get(repo_url, headers=headers).json()
    commit_data = requests.get(commits_url, headers=headers).json()
    langs_data = requests.get(langs_url, headers=headers).json()

    name = repo_data.get("full_name", repo_full_name)
    commit_count = len(commit_data) if isinstance(commit_data, list) else 0
    languages = ", ".join(langs_data.keys())

    return name, commit_count, languages

def generate_markdown(repos_data):
    md = "## 📊 Repozitoare Contribuite\n\n"
    md += "| 📂 Repository | 🧾 Commit-uri | 🧠 Limbaje |\n"
    md += "|--------------|---------------|------------|\n"
    for name, commits, langs in repos_data:
        md += f"| [{name}](https://github.com/{name}) | {commits} | {langs or '-'} |\n"
    return md

def update_readme(table):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    new_section = generate_markdown(table)
    if "## 📊 Repozitoare Contribuite" in content:
        pre = content.split("## 📊 Repozitoare Contribuite")[0].strip()
        content = f"{pre}\n\n{new_section}"
    else:
        content += f"\n\n{new_section}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ README.md actualizat.")

if __name__ == "__main__":
    repos = get_contributed_repos()
    print(f"🔧 Procesăm {len(repos)} repo-uri...")

    results = []
    for repo in repos:
        try:
            results.append(get_repo_data(repo))
        except Exception as e:
            print(f"⚠️ Eroare la {repo}: {e}")

    update_readme(results)
