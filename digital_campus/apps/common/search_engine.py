"""
search_engine.py — Pluggable TF-IDF Search Engine for Digital Campus
─────────────────────────────────────────────────────────────────────

Implements a basic search engine over posts and users using:
- TF-IDF vectorization
- Cosine similarity
- Optional fuzzy spell-correction

Designed to be lightweight and easily extensible:
- Hooks for ML re-ranking, embedding-based search
- Pluggable as a backend service for views

Dependencies:
    pip install scikit-learn rapidfuzz numpy
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
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
    meta: dict   # e.g. {"type": "post", "obj": post}


class SearchEngine:
    """
    Core search engine using TF-IDF and cosine similarity.
    Supports indexing, searching, and spell-correction.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = None
        self.documents: List[Document] = []

    # ————— Indexing ————— #
    def build_index(self, all_posts, all_users) -> None:
        """
        Builds the TF-IDF index from all posts and users.
        """
        self.documents = []

        for p in all_posts:
            txt = f"{p.title} {p.content}"
            self.documents.append(Document(
                id=p.pk,
                text=txt,
                meta={"type": "post", "obj": p}
            ))

        for u in all_users:
            txt = f"{u.username} {u.first_name} {u.last_name}"
            self.documents.append(Document(
                id=u.pk,
                text=txt,
                meta={"type": "user", "obj": u}
            ))

        corpus = [d.text for d in self.documents]
        self.doc_matrix = self.vectorizer.fit_transform(corpus)

    # ————— Spell-Correction ————— #
    def correct_query(self, query: str, threshold: int = 80) -> str:
        """
        Attempts to correct query tokens using fuzzy matching
        against the TF-IDF vocabulary.
        """
        vocab = list(self.vectorizer.vocabulary_.keys())
        tokens = re.findall(r"\w+", query.lower())
        corrected = [
            process.extractOne(t, vocab)[0] if process.extractOne(t, vocab)[1] >= threshold else t
            for t in tokens
        ]
        return " ".join(corrected)

    # ————— Search ————— #
    def search(self, query: str, top_k: int = 20) -> List[Tuple[Document, float]]:
        """
        Returns the top-k most similar documents to the query.
        """
        if self.doc_matrix is None or not self.doc_matrix.shape[0]:
            return []

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.doc_matrix).flatten()
        best_idx = sims.argsort()[::-1][:top_k]
        return [
            (self.documents[i], float(sims[i]))
            for i in best_idx if sims[i] > 0
        ]

    # ————— Future Enhancements ————— #
    # def embed_and_rerank(self, query): ...
    # def learn_to_rank(self, feature_matrix, labels): ...


# ————— Example Usage ————— #
if __name__ == "__main__":
    from django.contrib.auth import get_user_model
    from apps.posts.models import Post

    se = SearchEngine()
    se.build_index(Post.objects.all(), get_user_model().objects.all())
    q = "matrix calculus"
    print("Did you mean:", se.correct_query(q))
    for doc, score in se.search(q):
        print(score, doc.meta["type"], doc.meta["obj"])


# ————— Singleton Instantiation ————— #
_engine_singleton: Optional[SearchEngine] = None

def engine() -> SearchEngine:
    """
    Returns the global singleton SearchEngine instance.
    Raises if not initialized (should be done in AppConfig.ready).
    """
    global _engine_singleton
    if _engine_singleton is None:
        raise RuntimeError("SearchEngine not initialized. Call from AppConfig.ready().")
    return _engine_singleton

def search(q: str, k: int = 20) -> List[Tuple[Document, float]]:
    """Wrapper for global search engine search method."""
    return engine().search(q, top_k=k)

def correct(q: str) -> str:
    """Wrapper for global search engine correction method."""
    return engine().correct_query(q)
