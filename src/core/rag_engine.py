"""RAG Engine implementation using LlamaIndex."""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from llama_index.core import (
    Document,
    VectorStoreIndex,
    Settings,
    StorageContext,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.core.config import settings
from src.core.vector_store import VectorStoreManager
from src.models.memory import Memory, MemorySearch

logger = logging.getLogger(__name__)


class RAGEngine:
    """Main RAG engine for memory management."""

    def __init__(
        self,
        tenant_id: str,
        vector_store_manager: Optional[VectorStoreManager] = None,
    ):
        """Initialize RAG engine for a specific tenant."""
        self.tenant_id = tenant_id
        self.vector_store_manager = vector_store_manager or VectorStoreManager(tenant_id)

        # Configure LlamaIndex settings
        self._configure_llama_index()

        # Initialize index
        self.index = None
        self._initialize_index()

    def _configure_llama_index(self):
        """Configure global LlamaIndex settings."""
        # Set embedding model
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=settings.embedding_model,
            trust_remote_code=True,
        )

        # Set chunk settings
        Settings.chunk_size = settings.chunk_size
        Settings.chunk_overlap = settings.chunk_overlap

        # Configure LLM if available
        if settings.openai_api_key:
            try:
                from llama_index.llms.openai import OpenAI
                Settings.llm = OpenAI(
                    model=settings.llm_model,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                    api_key=settings.openai_api_key,
                )
            except ImportError:
                logger.warning("OpenAI LLM not available, skipping LLM configuration")

    def _initialize_index(self):
        """Initialize or load the vector store index."""
        try:
            # Get vector store from manager
            vector_store = self.vector_store_manager.get_store()

            # Create storage context with vector store
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store
            )

            # Create or load index
            self.index = VectorStoreIndex.from_vector_store(
                vector_store,
                storage_context=storage_context,
            )

            logger.info(f"Initialized RAG index for tenant {self.tenant_id}")

        except Exception as e:
            logger.error(f"Failed to initialize RAG index: {e}")
            raise

    def index_memory(self, memory: Memory) -> bool:
        """Index a single memory into the vector store."""
        try:
            # Create document from memory
            document = self._memory_to_document(memory)

            # Parse into nodes
            parser = SentenceSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )
            nodes = parser.get_nodes_from_documents([document])

            # Add to index
            self.index.insert_nodes(nodes)

            logger.info(f"Indexed memory {memory.id} for tenant {self.tenant_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to index memory {memory.id}: {e}")
            return False

    def index_memories_batch(self, memories: List[Memory]) -> Dict[str, bool]:
        """Index multiple memories in batch."""
        results = {}

        try:
            # Convert memories to documents
            documents = [self._memory_to_document(memory) for memory in memories]

            # Parse all documents into nodes
            parser = SentenceSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )
            all_nodes = []
            for doc in documents:
                nodes = parser.get_nodes_from_documents([doc])
                all_nodes.extend(nodes)

            # Batch insert
            self.index.insert_nodes(all_nodes)

            # Mark all as successful
            for memory in memories:
                results[str(memory.id)] = True

            logger.info(f"Batch indexed {len(memories)} memories for tenant {self.tenant_id}")

        except Exception as e:
            logger.error(f"Failed to batch index memories: {e}")
            # Mark all as failed
            for memory in memories:
                results[str(memory.id)] = False

        return results

    def search(
        self,
        search_params: MemorySearch,
        user_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        """Search memories using semantic and/or keyword search."""
        try:
            # Create query engine
            query_engine = self.index.as_query_engine(
                similarity_top_k=search_params.limit,
                response_mode="no_text",  # We just want the nodes, not a synthesized response
            )

            # Add metadata filters if provided
            metadata_filters = self._build_metadata_filters(search_params.filters, user_id)

            # Execute search
            response = query_engine.query(
                search_params.query,
                metadata_filters=metadata_filters,
            )

            # Extract results
            results = []
            for node_with_score in response.source_nodes:
                result = self._format_search_result(node_with_score)
                if result["score"] >= search_params.min_score:
                    results.append(result)

            logger.info(
                f"Search completed for tenant {self.tenant_id}: "
                f"query='{search_params.query[:50]}...', results={len(results)}"
            )

            return results

        except Exception as e:
            logger.error(f"Search failed for tenant {self.tenant_id}: {e}")
            return []

    def get_similar_memories(
        self,
        memory_id: UUID,
        limit: int = 5,
        min_score: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Find memories similar to a given memory."""
        try:
            # Get the memory's embedding from vector store
            embedding = self.vector_store_manager.get_embedding(str(memory_id))

            if not embedding:
                logger.warning(f"No embedding found for memory {memory_id}")
                return []

            # Search using the embedding
            results = self.vector_store_manager.search_by_vector(
                vector=embedding,
                limit=limit + 1,  # +1 because the memory itself will be included
                min_score=min_score,
            )

            # Filter out the memory itself
            similar_memories = [
                r for r in results if r["memory_id"] != str(memory_id)
            ]

            return similar_memories[:limit]

        except Exception as e:
            logger.error(f"Failed to find similar memories for {memory_id}: {e}")
            return []

    def update_memory_embedding(self, memory: Memory) -> bool:
        """Update the embedding for an existing memory."""
        try:
            # Delete old embedding
            self.vector_store_manager.delete_memory(str(memory.id))

            # Re-index with new content
            return self.index_memory(memory)

        except Exception as e:
            logger.error(f"Failed to update memory embedding for {memory.id}: {e}")
            return False

    def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory from the vector store."""
        try:
            success = self.vector_store_manager.delete_memory(str(memory_id))

            if success:
                logger.info(f"Deleted memory {memory_id} from tenant {self.tenant_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    def _memory_to_document(self, memory: Memory) -> Document:
        """Convert a Memory object to a LlamaIndex Document."""
        # Combine title and content for better context
        text = f"{memory.title}\n\n{memory.content}"

        # Build metadata
        metadata = {
            "memory_id": str(memory.id),
            "tenant_id": str(memory.tenant_id),
            "user_id": str(memory.user_id),
            "type": memory.type.value,
            "created_at": memory.created_at.isoformat(),
            "updated_at": memory.updated_at.isoformat(),
        }

        # Add optional metadata
        if memory.tags:
            metadata["tags"] = ",".join(memory.tags)

        if memory.entities:
            metadata["entities"] = ",".join(memory.entities)

        if memory.source_id:
            metadata["source_id"] = str(memory.source_id)

        if memory.external_url:
            metadata["external_url"] = memory.external_url

        # Merge with custom metadata
        metadata.update(memory.metadata)

        return Document(
            text=text,
            metadata=metadata,
            id_=str(memory.id),
        )

    def _build_metadata_filters(
        self,
        filters: Optional[Any],
        user_id: Optional[UUID],
    ) -> Optional[Dict[str, Any]]:
        """Build metadata filters for search."""
        if not filters and not user_id:
            return None

        metadata_filters = {}

        # Add user filter if provided
        if user_id:
            metadata_filters["user_id"] = str(user_id)

        # Add filters from search params
        if filters:
            if filters.type:
                metadata_filters["type"] = filters.type.value

            if filters.source_id:
                metadata_filters["source_id"] = str(filters.source_id)

            # Add more filter mappings as needed

        return metadata_filters if metadata_filters else None

    def _format_search_result(self, node_with_score: NodeWithScore) -> Dict[str, Any]:
        """Format a search result from a node with score."""
        metadata = node_with_score.node.metadata

        return {
            "memory_id": metadata.get("memory_id"),
            "score": node_with_score.score,
            "text": node_with_score.node.text,
            "type": metadata.get("type"),
            "created_at": metadata.get("created_at"),
            "tags": metadata.get("tags", "").split(",") if metadata.get("tags") else [],
            "entities": metadata.get("entities", "").split(",") if metadata.get("entities") else [],
        }

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        try:
            stats = self.vector_store_manager.get_stats()
            stats["tenant_id"] = self.tenant_id
            stats["index_initialized"] = self.index is not None

            return stats

        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {
                "tenant_id": self.tenant_id,
                "error": str(e),
            }