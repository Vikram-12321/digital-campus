"""
home_algorithm.py

Scoring utilities for home/feed ranking in Digital Campus.
Includes recency scoring via exponential decay and basic
term-matching relevance scoring.

Used for ordering posts and events in home feeds or search results.

Author: Your Name or Team
Last updated: 2025-05-02
"""

import math
from datetime import datetime, timezone
from typing import Any

# ——— Weighting Constants ———
RECENCY_HALF_LIFE_HOURS = 24.0  # Recency score halves every 24 hours
ALPHA = 0.7                     # Weight on recency
BETA = 0.3                      # Weight on relevance


def recency_score(timestamp: datetime) -> float:
    """
    Computes an exponential decay score based on time since `timestamp`.
    1.0 = now, 0.5 = half-life, 0.25 = 2 half-lives, etc.

    Args:
        timestamp (datetime): The original creation time (UTC).

    Returns:
        float: A value in (0, 1] representing freshness.
    """
    age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600.0
    decay = math.exp(-math.log(2) * age_hours / RECENCY_HALF_LIFE_HOURS)
    return decay


def relevance_score(item: Any, query: str) -> float:
    """
    Computes basic relevance score by checking how many query words
    are found in the item's text fields (title, body, and tags).

    Args:
        item: Any object with .title, .body, and optionally .requirements (tags).
        query (str): The user's search input.

    Returns:
        float: A fraction [0.0, 1.0] of matched words.
    """
    if not query:
        return 0.0

    # Combine content from title, body, and tags
    text_fields = [
        getattr(item, "title", ""),
        getattr(item, "body", ""),
    ]

    # Support both list and TaggableManager cases
    tags = getattr(item, "requirements", [])
    if hasattr(tags, "names"):
        tags = tags.names()  # for TaggableManager

    text_fields.append(" ".join(tags))

    full_text = " ".join(filter(None, text_fields)).lower()
    words = [w for w in query.lower().split() if w]
    if not words:
        return 0.0

    matches = sum(1 for w in words if w in full_text)
    return matches / len(words)
