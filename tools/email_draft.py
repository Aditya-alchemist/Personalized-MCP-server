from tools.github import list_repos
from tools.portfolio import get_portfolio_summary


def build_email_context() -> str:
    portfolio = get_portfolio_summary()
    repos = list_repos()

    lines = []

    if isinstance(portfolio, dict) and portfolio.get("ok"):
        lines.append(f"Portfolio title: {portfolio.get('title') or 'N/A'}")
        about = portfolio.get("about") or ""
        if about:
            lines.append(f"About: {about[:400]}")

        projects = portfolio.get("projects") or []
        if projects:
            lines.append("Projects:")
            for project in projects[:5]:
                name = project.get("name") or "Untitled"
                description = project.get("description") or ""
                lines.append(f"- {name}: {description[:140]}")

    if repos and isinstance(repos, list) and not repos[0].get("ok") is False:
        lines.append("GitHub repos:")
        for repo in repos[:5]:
            name = repo.get("name")
            stars = repo.get("stars")
            description = repo.get("description") or ""
            lines.append(f"- {name} ({stars} stars): {description[:120]}")

    if not lines:
        lines.append("No context found. Check API credentials and URLs in environment variables.")

    return "\n".join(lines)
