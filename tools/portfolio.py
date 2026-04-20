import os
from typing import Any

import requests
from bs4 import BeautifulSoup


def _pick_first_text(soup: BeautifulSoup, selectors: list[str]) -> str:
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            text = " ".join(node.get_text(strip=True).split())
            if text:
                return text
    return ""


def get_portfolio_summary() -> dict[str, Any]:
    url = os.getenv("PORTFOLIO_URL", "").strip()
    if not url:
        return {
            "ok": False,
            "error": "Missing PORTFOLIO_URL in environment.",
            "title": None,
            "about": None,
            "projects": [],
        }

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        return {
            "ok": False,
            "error": f"Failed to fetch portfolio: {exc}",
            "title": None,
            "about": None,
            "projects": [],
        }

    soup = BeautifulSoup(response.text, "html.parser")
    title = _pick_first_text(soup, ["title", "h1", "header h1"])
    about = _pick_first_text(
        soup,
        [
            "#about",
            "section#about",
            "[data-section='about']",
            "section.about",
            "main p",
        ],
    )

    project_cards = soup.select(
        ".project-card, .project, .card, [data-project], article"
    )
    projects = []
    for card in project_cards[:12]:
        name = _pick_first_text(card, ["h2", "h3", "h4", "a", "strong"])
        description = _pick_first_text(card, ["p", ".description", ".summary"])
        if name or description:
            projects.append({"name": name or "Untitled Project", "description": description})

    if not projects:
        links = soup.select("a[href]")
        for a in links[:40]:
            href = (a.get("href") or "").strip()
            label = " ".join(a.get_text(strip=True).split())
            if href and label and "project" in (href + " " + label).lower():
                projects.append({"name": label, "description": ""})

    return {
        "ok": True,
        "source": url,
        "title": title or None,
        "about": about or None,
        "projects": projects,
    }
