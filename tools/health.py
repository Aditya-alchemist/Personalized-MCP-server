import importlib.util
import os
from typing import Any

from web3 import Web3


def _has_env(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def _check_rpc_connectivity(timeout_seconds: int = 5) -> dict[str, Any]:
    rpc_url = os.getenv("RPC_URL", "").strip()
    if not rpc_url:
        return {"configured": False, "reachable": False, "error": "Missing RPC_URL."}

    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": timeout_seconds}))
        connected = w3.is_connected()
        chain_id = w3.eth.chain_id if connected else None
        return {"configured": True, "reachable": connected, "chain_id": chain_id}
    except Exception as exc:
        return {"configured": True, "reachable": False, "error": str(exc)}


def get_integration_health() -> dict[str, Any]:
    env_status = {
        "PORTFOLIO_URL": _has_env("PORTFOLIO_URL"),
        "GITHUB_USERNAME": _has_env("GITHUB_USERNAME"),
        "GITHUB_PAT": _has_env("GITHUB_PAT"),
        "RPC_URL": _has_env("RPC_URL"),
        "LINKEDIN_EMAIL": _has_env("LINKEDIN_EMAIL"),
        "LINKEDIN_PASSWORD": _has_env("LINKEDIN_PASSWORD"),
        "X_BEARER_TOKEN": _has_env("X_BEARER_TOKEN"),
        "X_API_KEY": _has_env("X_API_KEY"),
        "X_API_SECRET": _has_env("X_API_SECRET"),
        "X_ACCESS_TOKEN": _has_env("X_ACCESS_TOKEN"),
        "X_ACCESS_SECRET": _has_env("X_ACCESS_SECRET"),
    }

    linkedin_package_installed = importlib.util.find_spec("linkedin_api") is not None

    integrations = {
        "portfolio": {
            "configured": env_status["PORTFOLIO_URL"],
            "required_env": ["PORTFOLIO_URL"],
        },
        "github": {
            "configured": env_status["GITHUB_USERNAME"],
            "required_env": ["GITHUB_USERNAME"],
            "optional_env": ["GITHUB_PAT"],
        },
        "contracts": {
            "required_env": ["RPC_URL"],
            "rpc": _check_rpc_connectivity(),
        },
        "linkedin": {
            "configured": env_status["LINKEDIN_EMAIL"] and env_status["LINKEDIN_PASSWORD"],
            "required_env": ["LINKEDIN_EMAIL", "LINKEDIN_PASSWORD"],
            "dependency": {
                "name": "linkedin-api",
                "installed": linkedin_package_installed,
                "optional": True,
            },
        },
        "twitter": {
            "configured": env_status["X_BEARER_TOKEN"],
            "required_env": ["X_BEARER_TOKEN"],
            "optional_env": [
                "X_API_KEY",
                "X_API_SECRET",
                "X_ACCESS_TOKEN",
                "X_ACCESS_SECRET",
            ],
        },
    }

    missing_required = []
    if not env_status["PORTFOLIO_URL"]:
        missing_required.append("PORTFOLIO_URL")
    if not env_status["GITHUB_USERNAME"]:
        missing_required.append("GITHUB_USERNAME")
    if not env_status["RPC_URL"]:
        missing_required.append("RPC_URL")
    if not env_status["X_BEARER_TOKEN"]:
        missing_required.append("X_BEARER_TOKEN")

    return {
        "ok": True,
        "summary": {
            "core_ready": len(missing_required) == 0,
            "missing_required_env": missing_required,
        },
        "env": env_status,
        "integrations": integrations,
    }
