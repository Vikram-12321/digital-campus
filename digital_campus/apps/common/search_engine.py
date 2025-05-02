"""
search_engine.py  –  pluggable search model for Digital Campus
--------------------------------------------------------------

A simple TF-IDF + cosine-similarity engine with hooks for
• spell-correction  • embeddings  • re-ranking with ML
Copy into your backend, wire it in views.py instead of the handmade scorer.

Install deps:
    pip install scikit-learn rapidfuzz numpy
"""

from dataclasses import dataclass
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process
import numpy as np
import re
from typing import List, Tuple
from typing import Optional 


@dataclass
class Document:
    id: int
    text: str
    meta: dict   # e.g. {"type":"post", "title": ..., "author": ...}


class SearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = None          # TF-IDF matrix
        self.documents: List[Document] = []

    # ---------- indexing ---------- #
    def build_index(self, all_posts, all_users):
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

    # ---------- optional spell-correction ---------- #
    def correct_query(self, query: str, threshold: int = 80) -> str:
        vocab = list(self.vectorizer.vocabulary_.keys())
        tokens = re.findall(r"\w+", query.lower())
        corrected = [
            process.extractOne(t, vocab)[0] if process.extractOne(t, vocab)[1] >= threshold else t
            for t in tokens
        ]
        return " ".join(corrected)

    # ---------- search ---------- #
    def search(self, query: str, top_k: int = 20) -> List[Tuple[Document, float]]:
        if not self.doc_matrix.shape[0]:
            return []

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.doc_matrix).flatten()
        best_idx = sims.argsort()[::-1][:top_k]
        return [(self.documents[i], float(sims[i])) for i in best_idx if sims[i] > 0]

    # ---------- future hooks ---------- #
    # def embed_and_rerank(self, query): ...
    # def learn_to_rank(self, feature_matrix, labels): ...


# ----------- example usage (shell / unit test) -------------
if __name__ == "__main__":
    from django.contrib.auth import get_user_model
    from apps.posts.models import Post
    se = SearchEngine()
    se.build_index(Post.objects.all(), get_user_model().objects.all())
    q = "matrix calculus"
    print("Did you mean:", se.correct_query(q))
    for doc, score in se.search(q):
        print(score, doc.meta["type"], doc.meta["obj"])


_engine_singleton: Optional[SearchEngine] = None

def engine() -> SearchEngine:
    global _engine_singleton
    if _engine_singleton is None:
        raise RuntimeError("SearchEngine not initialised (CommonConfig.ready())")
    return _engine_singleton

def search(q: str, k: int = 20) -> List[Tuple[Document, float]]:
    return engine().search(q, top_k=k)

def correct(q: str) -> str:
    return engine().correct_query(q)