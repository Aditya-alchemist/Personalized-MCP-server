from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from tools.portfolio import get_portfolio_summary
from tools.github import list_repos, get_repo_details
from tools.contracts import get_contract_state, call_contract_function
from tools.linkedin import get_linkedin_profile, get_linkedin_recent_posts
from tools.twitter import get_twitter_profile, get_recent_tweets
from tools.email_draft import build_email_context
from tools.health import get_integration_health

load_dotenv()
mcp = FastMCP("Aditya Personal MCP Server")


@mcp.tool()
def portfolio_summary() -> dict:
    """Get Aditya's portfolio overview, about section and projects."""
    return get_portfolio_summary()


@mcp.tool()
def github_repos() -> list:
    """List all public GitHub repos with stars and descriptions."""
    return list_repos()


@mcp.tool()
def github_repo_details(repo_name: str) -> dict:
    """Get README, language and details of a specific repo."""
    return get_repo_details(repo_name)


@mcp.tool()
def contract_state(address: str, abi_path: str) -> dict:
    """Read on-chain state of a deployed Sepolia contract."""
    return get_contract_state(address, abi_path)


@mcp.tool()
def contract_call(address: str, abi_path: str, fn_name: str) -> dict:
    """Call any view/pure function on a deployed contract."""
    return call_contract_function(address, abi_path, fn_name)


@mcp.tool()
def linkedin_profile(username: str) -> dict:
    """Get LinkedIn profile summary, headline and skills."""
    return get_linkedin_profile(username)


@mcp.tool()
def linkedin_posts(username: str, count: int = 5) -> list:
    """Get recent LinkedIn posts with likes and comments."""
    return get_linkedin_recent_posts(username, count)


@mcp.tool()
def twitter_profile(username: str) -> dict:
    """Get Twitter/X profile with follower and tweet count."""
    return get_twitter_profile(username)


@mcp.tool()
def twitter_recent_posts(username: str, count: int = 10) -> list:
    """Get recent tweets with likes and retweets."""
    return get_recent_tweets(username, count)


@mcp.tool()
def integration_health() -> dict:
    """Report env and integration readiness for portfolio, GitHub, contracts, LinkedIn, and X."""
    return get_integration_health()


@mcp.prompt()
def cold_email_draft(recipient_role: str, company: str) -> str:
    """Generate a cold email using Aditya's portfolio and GitHub context."""
    context = build_email_context()
    return f"""
You are writing a professional cold email on behalf of a developer.

Here is their context:
{context}

Write a concise, personalized cold email to a {recipient_role} at {company}.
Highlight relevant blockchain/DeFi projects. Keep it under 150 words.
"""


if __name__ == "__main__":
    mcp.run(transport="stdio")
