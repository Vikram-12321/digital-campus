"""
apps/search/scoring.py

Scoring utilities for home/feed ranking in Digital Campus.

Includes:
- Exponential recency decay scoring
- Keyword-based relevance scoring

Used for ordering posts and events in feeds or search results.

Author: Vikram Bhojanala  
Last updated: 2025-05-09
"""

import math
from datetime import datetime, timezone
from typing import Any, List


# ——— Scoring Weights ———
RECENCY_HALF_LIFE_HOURS = 24.0  # Recency halves every 24h
ALPHA = 0.7                     # Recency weight
BETA = 0.3                      # Relevance weight


def recency_score(timestamp: datetime) -> float:
    """
    Returns a score in (0, 1] using exponential decay based on age.

    Args:
        timestamp (datetime): A timezone-aware datetime (UTC).

    Returns:
        float: A freshness score (1 = now, 0.5 = 24h ago, etc.).
    """
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600.0
    decay = math.exp(-math.log(2) * age_hours / RECENCY_HALF_LIFE_HOURS)
    return max(decay, 0.0)  # Just in case


def relevance_score(item: Any, query: str) -> float:
    """
    Computes keyword match fraction from a query string.

    Args:
        item (Any): Object with .title, .body, and optionally .requirements (tags/skills).
        query (str): The search string entered by the user.

    Returns:
        float: Fraction [0.0, 1.0] of query words matched in item fields.
    """
    if not query:
        return 0.0

    title = getattr(item, "title", "") or ""
    body = getattr(item, "body", "") or ""

    # Handle TaggableManager, list, or None
    raw_tags = getattr(item, "requirements", [])
    tags: List[str] = raw_tags.names() if hasattr(raw_tags, "names") else list(raw_tags or [])

    full_text = " ".join([title, body, " ".join(tags)]).lower()
    query_words = [word for word in query.lower().split() if word]

    if not query_words:
        return 0.0

    matches = sum(1 for word in query_words if word in full_text)
    return matches / len(query_words)

def final_score(item: Any, query: str) -> float:
    return ALPHA * recency_score(item.timestamp) + BETA * relevance_score(item, query)
