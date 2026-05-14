import numpy as np
from config import Config


class KnowledgeRetriever:
    """RAG 知识检索：本地 embedding + 余弦相似度"""

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
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        return self.model.encode(text, normalize_embeddings=True)

    def retrieve(self, query: str, top_k: int = 3, category: str | None = None,
                 min_score: float = 0.0) -> list[dict]:
        embedding = self.encode(query)
        return self._search(embedding, top_k, category, min_score)

    def _search(self, query_vec: np.ndarray, top_k: int, category: str | None,
                min_score: float) -> list[dict]:
        from db.models import Knowledge

        query = Knowledge.select().where(Knowledge.embedding.is_null(False))
        if category:
            query = query.where(Knowledge.category == category)

        results = []
        for k in query:
            stored = np.frombuffer(k.embedding, dtype=np.float32)
            score = float(np.dot(query_vec, stored) / (
                np.linalg.norm(query_vec) * np.linalg.norm(stored) + 1e-8
            ))
            if score >= min_score:
                results.append({
                    "id": k.id,
                    "title": k.title,
                    "content": k.content,
                    "category": k.category,
                    "score": score,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
