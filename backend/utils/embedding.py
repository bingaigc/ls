from __future__ import annotations

import hashlib
import logging
from functools import lru_cache
from typing import List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.utils.config import load_config

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        cfg = load_config()["embedding"]
        self.mode = cfg.get("mode", "local")
        self.local_model_name = cfg.get("local_model", "sentence-transformers/all-MiniLM-L6-v2")
        self.openai_model = cfg.get("openai_model", "text-embedding-3-small")
        self.openai_api_key = cfg.get("openai_api_key", "")

    @lru_cache(maxsize=1)
    def _local_model(self):
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(self.local_model_name)

    @lru_cache(maxsize=1)
    def _openai_client(self):
        from openai import OpenAI

        return OpenAI(api_key=self.openai_api_key)

    @staticmethod
    def _hash_embedding(text: str, dim: int = 384) -> np.ndarray:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        ints = np.frombuffer(digest * ((dim // len(digest)) + 1), dtype=np.uint8)[:dim]
        vec = ints.astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([])

        if self.mode == "openai" and self.openai_api_key:
            try:
                client = self._openai_client()
                resp = client.embeddings.create(model=self.openai_model, input=texts)
                arr = np.array([d.embedding for d in resp.data], dtype=np.float32)
                return arr
            except Exception as exc:
                logger.warning("OpenAI embedding failed, fallback to local/hash mode: %s", exc)

        try:
            model = self._local_model()
            return np.array(model.encode(texts, normalize_embeddings=True), dtype=np.float32)
        except Exception as exc:
            logger.warning("Local embedding failed, fallback to hash mode: %s", exc)
            logger.warning("Using hash-based fallback embeddings; similarity quality may be reduced.")
            return np.array([self._hash_embedding(t) for t in texts], dtype=np.float32)


embedding_service = EmbeddingService()


def cosine_similarity_pairwise(a: np.ndarray, b: np.ndarray) -> List[float]:
    if len(a) == 0 or len(b) == 0:
        return []
    sims = [float(cosine_similarity([x], [y])[0][0]) for x, y in zip(a, b)]
    return sims
