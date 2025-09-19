"""Vector store management for multi-tenant support."""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from llama_index.core.vector_stores.types import VectorStore
from src.core.config import settings, VectorStoreType

logger = logging.getLogger(__name__)


class BaseVectorStore(ABC):
    """Base class for vector store implementations."""

    @abstractmethod
    def get_store(self) -> VectorStore:
        """Get the LlamaIndex compatible vector store."""
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory from the vector store."""
        pass

    @abstractmethod
    def get_embedding(self, memory_id: str) -> Optional[List[float]]:
        """Get embedding for a specific memory."""
        pass

    @abstractmethod
    def search_by_vector(
        self,
        vector: List[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search using a vector directly."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        pass


class PineconeVectorStore(BaseVectorStore):
    """Pinecone vector store implementation."""

    def __init__(self, tenant_id: str):
        """Initialize Pinecone vector store for a tenant."""
        self.tenant_id = tenant_id
        self.namespace = f"tenant-{tenant_id}"

        # Import here to avoid dependency if not using Pinecone
        try:
            from pinecone import Pinecone
            from llama_index.vector_stores.pinecone import PineconeVectorStore as LlamaPinecone
        except ImportError:
            raise ImportError(
                "Pinecone dependencies not installed. "
                "Install with: pip install pinecone-client llama-index-vector-stores-pinecone"
            )

        # Initialize Pinecone client
        self.client = Pinecone(api_key=settings.pinecone_api_key)

        # Get or create index
        self.index = self.client.Index(settings.pinecone_index_name)

        # Create LlamaIndex compatible store
        self.store = LlamaPinecone(
            pinecone_index=self.index,
            namespace=self.namespace,
        )

        logger.info(f"Initialized Pinecone store for tenant {tenant_id} with namespace {self.namespace}")

    def get_store(self) -> VectorStore:
        """Get the LlamaIndex compatible vector store."""
        return self.store

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory from Pinecone."""
        try:
            self.index.delete(
                ids=[memory_id],
                namespace=self.namespace,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id} from Pinecone: {e}")
            return False

    def get_embedding(self, memory_id: str) -> Optional[List[float]]:
        """Get embedding for a specific memory from Pinecone."""
        try:
            result = self.index.fetch(
                ids=[memory_id],
                namespace=self.namespace,
            )

            if memory_id in result.vectors:
                return result.vectors[memory_id].values

            return None
        except Exception as e:
            logger.error(f"Failed to get embedding for {memory_id}: {e}")
            return None

    def search_by_vector(
        self,
        vector: List[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search Pinecone using a vector directly."""
        try:
            results = self.index.query(
                namespace=self.namespace,
                vector=vector,
                top_k=limit,
                include_metadata=True,
            )

            formatted_results = []
            for match in results.matches:
                if match.score >= min_score:
                    formatted_results.append({
                        "memory_id": match.id,
                        "score": match.score,
                        "metadata": match.metadata,
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search by vector in Pinecone: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index."""
        try:
            stats = self.index.describe_index_stats()
            namespace_stats = stats.namespaces.get(self.namespace, {})

            return {
                "type": "pinecone",
                "namespace": self.namespace,
                "vector_count": namespace_stats.get("vector_count", 0),
                "dimension": stats.dimension,
                "total_vector_count": stats.total_vector_count,
            }
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            return {"type": "pinecone", "error": str(e)}


class QdrantVectorStore(BaseVectorStore):
    """Qdrant vector store implementation."""

    def __init__(self, tenant_id: str):
        """Initialize Qdrant vector store for a tenant."""
        self.tenant_id = tenant_id
        self.collection_name = f"{settings.qdrant_collection_name}_{tenant_id}"

        # Import here to avoid dependency if not using Qdrant
        try:
            from qdrant_client import QdrantClient
            from llama_index.vector_stores.qdrant import QdrantVectorStore as LlamaQdrant
        except ImportError:
            raise ImportError(
                "Qdrant dependencies not installed. "
                "Install with: pip install qdrant-client llama-index-vector-stores-qdrant"
            )

        # Initialize Qdrant client
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
        )

        # Ensure collection exists
        self._ensure_collection_exists()

        # Create LlamaIndex compatible store
        self.store = LlamaQdrant(
            client=self.client,
            collection_name=self.collection_name,
        )

        logger.info(f"Initialized Qdrant store for tenant {tenant_id} with collection {self.collection_name}")

    def _ensure_collection_exists(self):
        """Ensure the collection exists in Qdrant."""
        from qdrant_client.models import Distance, VectorParams

        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")

    def get_store(self) -> VectorStore:
        """Get the LlamaIndex compatible vector store."""
        return self.store

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory from Qdrant."""
        try:
            from qdrant_client.models import PointIdsList

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=[memory_id]),
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id} from Qdrant: {e}")
            return False

    def get_embedding(self, memory_id: str) -> Optional[List[float]]:
        """Get embedding for a specific memory from Qdrant."""
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[memory_id],
                with_vectors=True,
            )

            if result:
                return result[0].vector

            return None
        except Exception as e:
            logger.error(f"Failed to get embedding for {memory_id}: {e}")
            return None

    def search_by_vector(
        self,
        vector: List[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search Qdrant using a vector directly."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=limit,
                score_threshold=min_score,
                with_payload=True,
            )

            formatted_results = []
            for hit in results:
                formatted_results.append({
                    "memory_id": hit.id,
                    "score": hit.score,
                    "metadata": hit.payload,
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search by vector in Qdrant: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the Qdrant collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)

            return {
                "type": "qdrant",
                "collection": self.collection_name,
                "vector_count": collection_info.points_count,
                "dimension": collection_info.config.params.vectors.size,
                "segments": collection_info.segments_count,
            }
        except Exception as e:
            logger.error(f"Failed to get Qdrant stats: {e}")
            return {"type": "qdrant", "error": str(e)}


class VectorStoreManager:
    """Manager for vector store operations."""

    def __init__(self, tenant_id: str):
        """Initialize vector store manager for a tenant."""
        self.tenant_id = tenant_id
        self.store_impl = self._create_store_implementation()

    def _create_store_implementation(self) -> BaseVectorStore:
        """Create the appropriate vector store implementation."""
        if settings.vector_store_type == VectorStoreType.PINECONE:
            return PineconeVectorStore(self.tenant_id)
        elif settings.vector_store_type == VectorStoreType.QDRANT:
            return QdrantVectorStore(self.tenant_id)
        else:
            raise ValueError(f"Unsupported vector store type: {settings.vector_store_type}")

    def get_store(self) -> VectorStore:
        """Get the LlamaIndex compatible vector store."""
        return self.store_impl.get_store()

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory from the vector store."""
        return self.store_impl.delete_memory(memory_id)

    def get_embedding(self, memory_id: str) -> Optional[List[float]]:
        """Get embedding for a specific memory."""
        return self.store_impl.get_embedding(memory_id)

    def search_by_vector(
        self,
        vector: List[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search using a vector directly."""
        return self.store_impl.search_by_vector(vector, limit, min_score)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return self.store_impl.get_stats()