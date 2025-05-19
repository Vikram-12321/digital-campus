"""
engine.py — Pluggable TF-IDF Search Engine for Digital Campus
─────────────────────────────────────────────────────────────────────

Implements a lightweight vector-based search engine over posts and users using:
- TF-IDF vectorization
- Cosine similarity
- Optional fuzzy spell-correction via RapidFuzz

Designed for easy extension:
- Hooks for re-ranking (ML, embeddings, etc.)
- Singleton-compatible for AppConfig initialization

Author: Vikram Bhojanala  
Last updated: 2025-05-09
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process
import numpy as np
import re


@dataclass
class Document:
    """
    Represents a searchable unit (user or post) with metadata.
    """
    id: int
    text: str
    meta: Dict[str, Any]  # e.g. {"type": "post", "obj": post}


class SearchEngine:
    """
    Core search engine using TF-IDF and cosine similarity.
    Supports indexing, searching, and spell correction.
    """

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = None
        self.documents: List[Document] = []

    # ————— Indexing ————— #
    def build_index(self, all_posts: List[Any], all_users: List[Any]) -> None:
        """
        Builds the TF-IDF index from all posts and users.
        """
        self.documents = []

        for post in all_posts:
            text = f"{post.title} {post.content}"
            self.documents.append(Document(
                id=post.pk,
                text=text,
                meta={"type": "post", "obj": post}
            ))

        for user in all_users:
            text = f"{user.username} {user.first_name} {user.last_name}"
            self.documents.append(Document(
                id=user.pk,
                text=text,
                meta={"type": "user", "obj": user}
            ))

        corpus = [doc.text for doc in self.documents]
        self.doc_matrix = self.vectorizer.fit_transform(corpus)

    # ————— Spell Correction ————— #
    def correct_query(self, query: str, threshold: int = 80) -> str:
        """
        Attempts to correct query tokens using fuzzy matching
        against the TF-IDF vocabulary.
        """
        if not hasattr(self.vectorizer, "vocabulary_"):
            return query  # Not yet indexed

        vocab = list(self.vectorizer.vocabulary_.keys())
        tokens = re.findall(r"\w+", query.lower())
        corrected = []

        for token in tokens:
            suggestion = process.extractOne(token, vocab)
            if suggestion and suggestion[1] >= threshold:
                corrected.append(suggestion[0])
            else:
                corrected.append(token)

        return " ".join(corrected)

    # ————— Search ————— #
    def search(self, query: str, top_k: int = 20) -> List[Tuple[Document, float]]:
        """
        Returns the top-k most relevant documents to the query.
        """
        if not self.doc_matrix or not self.documents:
            return []

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.doc_matrix).flatten()
        top_indices = sims.argsort()[::-1][:top_k]

        return [
            (self.documents[i], float(sims[i]))
            for i in top_indices if sims[i] > 0
        ]

    # ————— Future Enhancements ————— #
    # def embed_and_rerank(self, query: str): ...
    # def learn_to_rank(self, features, labels): ...


# ————— Singleton & Access Helpers ————— #

_engine_singleton: Optional[SearchEngine] = None

def engine() -> SearchEngine:
    """
    Returns the global SearchEngine singleton.
    Should be initialized in AppConfig.ready().
    """
    if _engine_singleton is None:
        raise RuntimeError("SearchEngine not initialized. Call in AppConfig.ready().")
    return _engine_singleton

def initialize_engine(posts: List[Any], users: List[Any]) -> SearchEngine:
    """
    Initializes and stores the global SearchEngine.
    Should be called only once (e.g., from AppConfig).
    """
    global _engine_singleton
    _engine_singleton = SearchEngine()
    _engine_singleton.build_index(posts, users)
    return _engine_singleton

def search(q: str, k: int = 20) -> List[Tuple[Document, float]]:
    """Wrapper for global search()."""
    return engine().search(q, top_k=k)

def correct(q: str) -> str:
    """Wrapper for global correct_query()."""
    return engine().correct_query(q)


# ————— Example Usage ————— #
if __name__ == "__main__":
    from django.contrib.auth import get_user_model
    from apps.posts.models import Post

    posts = Post.objects.all()
    users = get_user_model().objects.all()

    se = SearchEngine()
    se.build_index(posts, users)

    q = "matrix calculus"
    print("Did you mean:", se.correct_query(q))
    for doc, score in se.search(q):
        print(f"{score:.3f} — {doc.meta['type']} — {doc.meta['obj']}")
