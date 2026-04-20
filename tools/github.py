import base64
import os
from typing import Any

from github import Github, GithubException


def _client() -> Github:
    token = os.getenv("GITHUB_PAT", "").strip()
    if token:
        return Github(token)
    return Github()


def _username() -> str:
    return os.getenv("GITHUB_USERNAME", "").strip()


def list_repos() -> list[dict[str, Any]]:
    username = _username()
    if not username:
        return [{"ok": False, "error": "Missing GITHUB_USERNAME in environment."}]

    try:
        gh = _client()
        user = gh.get_user(username)
        repos = []
        for repo in user.get_repos(sort="updated"):
            repos.append(
                {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "url": repo.html_url,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                }
            )
        return repos
    except GithubException as exc:
        return [{"ok": False, "error": f"GitHub API error: {exc.data or str(exc)}"}]
    except Exception as exc:
        return [{"ok": False, "error": f"Failed to list repositories: {exc}"}]


def get_repo_details(repo_name: str) -> dict[str, Any]:
    username = _username()
    if not username:
        return {"ok": False, "error": "Missing GITHUB_USERNAME in environment."}

    repo_name = repo_name.strip()
    if not repo_name:
        return {"ok": False, "error": "repo_name is required."}

    try:
        gh = _client()
        repo = gh.get_repo(f"{username}/{repo_name}")
        readme_text = None
        try:
            readme = repo.get_readme()
            readme_text = base64.b64decode(readme.content).decode("utf-8", errors="replace")
        except GithubException:
            readme_text = None

        return {
            "ok": True,
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "language": repo.language,
            "topics": repo.get_topics(),
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "url": repo.html_url,
            "readme": readme_text,
        }
    except GithubException as exc:
        return {"ok": False, "error": f"GitHub API error: {exc.data or str(exc)}"}
    except Exception as exc:
        return {"ok": False, "error": f"Failed to get repository details: {exc}"}
