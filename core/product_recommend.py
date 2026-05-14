import json
import numpy as np
from config import Config


class ProductRecommender:
    """商品推荐：基于 embedding 的语义匹配"""

    def __init__(self, model_name: str = "", load_model: bool = True):
        self._model = None
        self._model_name = model_name or Config.EMBEDDING_MODEL
        if load_model:
            self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        except Exception:
            pass

    @property
    def model(self):
        if self._model is None:
            self._load_model()
        return self._model

    def encode(self, text: str) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("Embedding model not loaded")
        return self._model.encode(text, normalize_embeddings=True)

    def recommend(self, query: str, top_k: int = 3, category: str | None = None,
                  max_price: float | None = None) -> list[dict]:
        embedding = self.encode(query)
        return self._search(embedding, top_k, category, max_price)

    def _search(self, query_vec: np.ndarray, top_k: int, category: str | None,
                max_price: float | None) -> list[dict]:
        from db.models import Product

        q = Product.select().where(Product.embedding.is_null(False))
        if category:
            q = q.where(Product.category == category)

        results = []
        for p in q:
            if max_price is not None and p.price > max_price:
                continue
            stored = np.frombuffer(p.embedding, dtype=np.float32)
            score = float(np.dot(query_vec, stored) / (
                np.linalg.norm(query_vec) * np.linalg.norm(stored) + 1e-8
            ))
            results.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "category": p.category,
                "tags": json.loads(p.tags),
                "score": score,
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
