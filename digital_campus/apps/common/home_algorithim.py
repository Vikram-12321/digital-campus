import math
from datetime import datetime, timezone

# how strongly recency matters
RECENCY_HALF_LIFE_HOURS = 24.0      # recency decays by half every 24 h
ALPHA = 0.7                        # weight on recency
BETA  = 0.3                        # weight on relevance

def recency_score(timestamp):
    """
    Exponential decay: 1.0 at now, 0.5 after half-life, etc.
    """
    age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600.0
    return math.exp(-math.log(2) * age_hours / RECENCY_HALF_LIFE_HOURS)

def relevance_score(item, query):
    """
    Very basic: fraction of query words found in title/body/tags.
    """
    if not query:
        return 0.0
    text = " ".join(filter(None, [
        getattr(item, "title", ""),
        getattr(item, "body", ""),
        # if you have taggit tags:
        " ".join(getattr(item, "requirements", []))  
    ])).lower()
    words = [w for w in query.lower().split() if w]
    matches = sum(1 for w in words if w in text)
    return matches / len(words)
