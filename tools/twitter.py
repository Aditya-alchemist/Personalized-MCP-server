import os
from typing import Any

import tweepy


def _first_non_empty(*keys: str) -> str:
    for key in keys:
        value = os.getenv(key, "").strip()
        if value:
            return value
    return ""


def _client() -> tweepy.Client:
    bearer = _first_non_empty("X_BEARER_TOKEN")
    api_key = _first_non_empty("X_API_KEY", "X_CONSUMER_KEY")
    api_secret = _first_non_empty("X_API_SECRET", "X_SECRET_KEY")
    access_token = os.getenv("X_ACCESS_TOKEN", "").strip()
    access_secret = os.getenv("X_ACCESS_SECRET", "").strip()

    if not bearer:
        raise ValueError("Missing X_BEARER_TOKEN in environment.")

    return tweepy.Client(
        bearer_token=bearer,
        consumer_key=api_key or None,
        consumer_secret=api_secret or None,
        access_token=access_token or None,
        access_token_secret=access_secret or None,
        wait_on_rate_limit=True,
    )


def get_twitter_profile(username: str) -> dict[str, Any]:
    username = username.strip().lstrip("@")
    if not username:
        return {"ok": False, "error": "username is required."}

    try:
        client = _client()
        user = client.get_user(
            username=username,
            user_fields=["public_metrics", "description", "created_at", "verified"],
        )
        if not user.data:
            return {"ok": False, "error": "User not found."}

        metrics = user.data.public_metrics or {}
        return {
            "ok": True,
            "id": user.data.id,
            "username": user.data.username,
            "name": user.data.name,
            "bio": user.data.description,
            "verified": user.data.verified,
            "followers": metrics.get("followers_count"),
            "following": metrics.get("following_count"),
            "tweets": metrics.get("tweet_count"),
            "listed": metrics.get("listed_count"),
            "created_at": user.data.created_at.isoformat() if user.data.created_at else None,
        }
    except Exception as exc:
        return {"ok": False, "error": f"Failed to fetch Twitter profile: {exc}"}


def get_recent_tweets(username: str, count: int = 10) -> list[dict[str, Any]]:
    username = username.strip().lstrip("@")
    if not username:
        return [{"ok": False, "error": "username is required."}]

    if count <= 0:
        count = 10

    try:
        client = _client()
        user_resp = client.get_user(username=username)
        if not user_resp.data:
            return [{"ok": False, "error": "User not found."}]

        tweets_resp = client.get_users_tweets(
            id=user_resp.data.id,
            max_results=min(max(count, 5), 100),
            tweet_fields=["created_at", "public_metrics", "lang"],
            exclude=["replies", "retweets"],
        )

        tweets = []
        for tw in tweets_resp.data or []:
            metrics = tw.public_metrics or {}
            tweets.append(
                {
                    "id": tw.id,
                    "text": tw.text,
                    "created_at": tw.created_at.isoformat() if tw.created_at else None,
                    "language": tw.lang,
                    "likes": metrics.get("like_count"),
                    "retweets": metrics.get("retweet_count"),
                    "replies": metrics.get("reply_count"),
                    "quotes": metrics.get("quote_count"),
                    # Organic impression metrics require elevated access and user context.
                    "impressions": None,
                }
            )

        return tweets
    except Exception as exc:
        return [{"ok": False, "error": f"Failed to fetch recent tweets: {exc}"}]
