import os
from typing import Any


class LinkedInDependencyError(RuntimeError):
    pass


def _client() -> Any:
    email = os.getenv("LINKEDIN_EMAIL", "").strip()
    password = os.getenv("LINKEDIN_PASSWORD", "").strip()
    if not email or not password:
        raise ValueError("Missing LINKEDIN_EMAIL or LINKEDIN_PASSWORD in environment.")
    try:
        from linkedin_api import Linkedin  # type: ignore
    except ModuleNotFoundError as exc:
        raise LinkedInDependencyError(
            "Optional dependency 'linkedin-api' is not installed. "
            "Install it in a compatible Python environment to enable LinkedIn tools."
        ) from exc
    return Linkedin(email, password)


def get_linkedin_profile(username: str) -> dict[str, Any]:
    username = username.strip()
    if not username:
        return {"ok": False, "error": "username is required."}

    try:
        client = _client()
        data = client.get_profile(username)
        return {
            "ok": True,
            "public_id": data.get("public_id"),
            "first_name": data.get("firstName"),
            "last_name": data.get("lastName"),
            "headline": data.get("headline"),
            "summary": data.get("summary"),
            "location": data.get("locationName"),
            "skills": data.get("skills", []),
            "experience": data.get("experience", []),
            "education": data.get("education", []),
        }
    except LinkedInDependencyError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "error": f"Failed to fetch LinkedIn profile: {exc}"}


def get_linkedin_recent_posts(username: str, count: int = 5) -> list[dict[str, Any]]:
    username = username.strip()
    if not username:
        return [{"ok": False, "error": "username is required."}]

    if count <= 0:
        count = 5

    try:
        client = _client()
        urn_id = client.get_profile(username).get("profile_urn")
        if not urn_id:
            return [{"ok": False, "error": "Could not resolve profile URN."}]

        posts = client.get_profile_posts(urn_id=urn_id, post_count=min(count, 20))
        formatted = []
        for post in posts:
            commentary = post.get("commentary", {}) or {}
            social_detail = post.get("socialDetail", {}) or {}
            total_social_activity_counts = social_detail.get(
                "totalSocialActivityCounts", {}
            ) or {}

            formatted.append(
                {
                    "text": commentary.get("text"),
                    "likes": total_social_activity_counts.get("numLikes"),
                    "comments": total_social_activity_counts.get("numComments"),
                    "shares": total_social_activity_counts.get("numShares"),
                    "posted_at": post.get("created", {}).get("time"),
                }
            )

        return formatted
    except LinkedInDependencyError as exc:
        return [{"ok": False, "error": str(exc)}]
    except Exception as exc:
        return [{"ok": False, "error": f"Failed to fetch LinkedIn posts: {exc}"}]
