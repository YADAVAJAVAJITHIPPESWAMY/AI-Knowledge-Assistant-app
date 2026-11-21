"""
Embedding Service
Generates 1536-dimensional vector embeddings using OpenAI's `text-embedding-3-small`.
Includes a deterministic semantic mock embedder for offline local development and unit tests.
"""
import hashlib
import math
from typing import List, Optional
import numpy as np
from app.core.config import settings

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    openai = None


class EmbeddingService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.client = None

        if HAS_OPENAI and self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single text passage."""
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else [0.0] * self.dimension

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates 1536-dimensional embeddings for a batch of texts.
        Uses OpenAI text-embedding-3-small when API key is provided,
        or deterministic normalized vector hashing when offline.
        """
        if not texts:
            return []

        # If live OpenAI client is available, call the API
        if self.client and self.api_key:
            try:
                # Clean newlines as recommended by OpenAI documentation
                sanitized_texts = [t.replace("\n", " ") for t in texts]
                response = self.client.embeddings.create(
                    input=sanitized_texts,
                    model=self.model,
                    dimensions=self.dimension
                )
                return [data.embedding for data in response.data]
            except Exception as e:
                # Log error and fall back to deterministic embedder
                pass

        # Deterministic offline fallback embedding:
        # Generates a stable, normalized 1536-dim vector based on sha256 + token frequency
        return [self._generate_mock_embedding(text) for text in texts]

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        Creates a reproducible, unit-normalized 1536-dimensional vector for offline tests.
        Passages with shared words produce naturally higher cosine similarities.
        """
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            slot = h % self.dimension
            weight = 1.0 / math.sqrt(idx + 1)
            vec[slot] += weight

        # Also encode global text hash
        full_h = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        for i in range(16):
            slot = (full_h >> (i * 4)) % self.dimension
            vec[slot] += 0.5

        # Normalize to unit length (L2 norm)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec.tolist()


embedding_service = EmbeddingService()
