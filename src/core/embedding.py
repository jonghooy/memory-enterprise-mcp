"""Embedding service for text vectorization."""

import logging
from typing import List, Optional
import numpy as np

from sentence_transformers import SentenceTransformer
from src.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    _instance = None
    _model = None

    def __new__(cls):
        """Singleton pattern for embedding model."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize embedding service."""
        if self._model is None:
            self._initialize_model()

    def _initialize_model(self):
        """Initialize the embedding model."""
        try:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self._model = SentenceTransformer(
                settings.embedding_model,
                device="cuda" if self._check_cuda() else "cpu",
            )
            logger.info(f"Embedding model loaded successfully")

            # Verify dimension
            test_embedding = self._model.encode("test")
            actual_dim = len(test_embedding)

            if actual_dim != settings.embedding_dimension:
                logger.warning(
                    f"Embedding dimension mismatch: "
                    f"expected {settings.embedding_dimension}, got {actual_dim}"
                )
                # Update settings to match actual dimension
                settings.embedding_dimension = actual_dim

        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise

    def _check_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self._model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def embed_texts(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            if not texts:
                return []

            batch_size = batch_size or settings.embedding_batch_size

            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=len(texts) > 100,
            )

            return embeddings.tolist()

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float],
    ) -> float:
        """Compute cosine similarity between two embeddings."""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Compute cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

            return float(similarity)

        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.0

    def find_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 5,
        min_similarity: float = 0.0,
    ) -> List[tuple[int, float]]:
        """Find most similar embeddings from candidates."""
        try:
            if not candidate_embeddings:
                return []

            # Compute similarities
            similarities = []
            query_vec = np.array(query_embedding)

            for i, candidate in enumerate(candidate_embeddings):
                candidate_vec = np.array(candidate)
                similarity = np.dot(query_vec, candidate_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(candidate_vec)
                )

                if similarity >= min_similarity:
                    similarities.append((i, float(similarity)))

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Failed to find similar embeddings: {e}")
            return []

    def get_model_info(self) -> dict:
        """Get information about the embedding model."""
        if self._model is None:
            return {"error": "Model not initialized"}

        return {
            "model_name": settings.embedding_model,
            "dimension": settings.embedding_dimension,
            "device": str(self._model.device),
            "max_sequence_length": getattr(self._model, "max_seq_length", "unknown"),
        }


# Global embedding service instance
embedding_service = EmbeddingService()