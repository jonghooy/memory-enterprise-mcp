"""Memory service for CRUD operations."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from src.models.memory import (
    Memory,
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemorySearch,
    MemoryFilter,
)
from src.core.rag_engine import RAGEngine
from src.services.wiki_link_service import WikiLinkService

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing memories."""

    def __init__(
        self,
        db_session: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
    ):
        """Initialize memory service."""
        self.db = db_session
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.rag_engine = RAGEngine(str(tenant_id))
        self.wiki_service = WikiLinkService()

    async def create_memory(self, memory_data: MemoryCreate) -> MemoryResponse:
        """Create a new memory."""
        try:
            # Extract wiki links from content
            wiki_links = self.wiki_service.extract_wiki_links(memory_data.content)

            # Extract entities from wiki links and tags
            entities = list(set(wiki_links + memory_data.entities))

            # Create memory object
            memory = Memory(
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                title=memory_data.title,
                content=memory_data.content,
                type=memory_data.type,
                source_id=memory_data.source_id,
                tags=memory_data.tags,
                metadata=memory_data.metadata,
                entities=entities,
                wiki_links=wiki_links,
                external_url=memory_data.external_url,
                external_id=memory_data.external_id,
            )

            # Save to database
            self.db.add(memory)
            await self.db.commit()
            await self.db.refresh(memory)

            # Index in vector store (async task)
            success = await self._index_memory_async(memory)

            if success:
                memory.is_indexed = True
                memory.indexed_at = datetime.utcnow()
            else:
                memory.index_error = "Failed to index in vector store"

            await self.db.commit()

            # Create response
            response = await self._memory_to_response(memory)

            logger.info(f"Created memory {memory.id} for user {self.user_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            await self.db.rollback()
            raise

    async def get_memory(self, memory_id: UUID) -> Optional[MemoryResponse]:
        """Get a memory by ID."""
        try:
            # Query with access control
            query = select(Memory).where(
                and_(
                    Memory.id == memory_id,
                    Memory.tenant_id == self.tenant_id,
                    or_(
                        Memory.user_id == self.user_id,
                        # Add shared memory logic here if needed
                    ),
                )
            )

            result = await self.db.execute(query)
            memory = result.scalar_one_or_none()

            if not memory:
                return None

            # Update access timestamp
            memory.accessed_at = datetime.utcnow()
            await self.db.commit()

            return await self._memory_to_response(memory)

        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            raise

    async def update_memory(
        self,
        memory_id: UUID,
        memory_update: MemoryUpdate,
    ) -> Optional[MemoryResponse]:
        """Update an existing memory."""
        try:
            # Get memory with write access check
            query = select(Memory).where(
                and_(
                    Memory.id == memory_id,
                    Memory.tenant_id == self.tenant_id,
                    Memory.user_id == self.user_id,  # Only owner can update
                )
            )

            result = await self.db.execute(query)
            memory = result.scalar_one_or_none()

            if not memory:
                return None

            # Update fields
            update_data = memory_update.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(memory, field, value)

            # Re-extract wiki links if content changed
            if memory_update.content:
                wiki_links = self.wiki_service.extract_wiki_links(memory_update.content)
                memory.wiki_links = wiki_links
                memory.entities = list(set(wiki_links + (memory_update.entities or [])))

            memory.updated_at = datetime.utcnow()

            await self.db.commit()

            # Re-index if content changed
            if memory_update.content or memory_update.title:
                await self._reindex_memory_async(memory)

            return await self._memory_to_response(memory)

        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            await self.db.rollback()
            raise

    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory."""
        try:
            # Get memory with delete access check
            query = select(Memory).where(
                and_(
                    Memory.id == memory_id,
                    Memory.tenant_id == self.tenant_id,
                    Memory.user_id == self.user_id,  # Only owner can delete
                )
            )

            result = await self.db.execute(query)
            memory = result.scalar_one_or_none()

            if not memory:
                return False

            # Remove from vector store
            self.rag_engine.delete_memory(memory.id)

            # Delete from database
            await self.db.delete(memory)
            await self.db.commit()

            logger.info(f"Deleted memory {memory_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            await self.db.rollback()
            raise

    async def search_memories(
        self,
        search_params: MemorySearch,
    ) -> List[MemoryResponse]:
        """Search memories using vector search and filters."""
        try:
            # Perform vector search
            vector_results = self.rag_engine.search(
                search_params,
                user_id=self.user_id,
            )

            if not vector_results:
                return []

            # Get memory IDs from vector results
            memory_ids = [
                UUID(result["memory_id"])
                for result in vector_results
                if result["memory_id"]
            ]

            # Fetch full memory objects with filters
            query = select(Memory).where(
                and_(
                    Memory.id.in_(memory_ids),
                    Memory.tenant_id == self.tenant_id,
                )
            )

            # Apply additional filters
            query = self._apply_filters(query, search_params.filters)

            result = await self.db.execute(query)
            memories = result.scalars().all()

            # Create response with relevance scores
            responses = []
            for memory in memories:
                response = await self._memory_to_response(memory)

                # Add relevance score from vector search
                for vector_result in vector_results:
                    if str(memory.id) == vector_result["memory_id"]:
                        response.relevance_score = vector_result["score"]
                        break

                responses.append(response)

            # Sort by relevance score
            responses.sort(key=lambda x: x.relevance_score or 0, reverse=True)

            return responses[:search_params.limit]

        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            raise

    async def list_memories(
        self,
        filters: Optional[MemoryFilter] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[MemoryResponse]:
        """List memories with optional filters."""
        try:
            # Base query
            query = select(Memory).where(
                and_(
                    Memory.tenant_id == self.tenant_id,
                    or_(
                        Memory.user_id == self.user_id,
                        # Add shared memory logic here
                    ),
                )
            )

            # Apply filters
            if filters:
                query = self._apply_filters(query, filters)

            # Order by updated_at desc
            query = query.order_by(desc(Memory.updated_at))

            # Apply pagination
            query = query.limit(limit).offset(offset)

            result = await self.db.execute(query)
            memories = result.scalars().all()

            # Convert to responses
            responses = []
            for memory in memories:
                response = await self._memory_to_response(memory)
                responses.append(response)

            return responses

        except Exception as e:
            logger.error(f"Failed to list memories: {e}")
            raise

    async def get_similar_memories(
        self,
        memory_id: UUID,
        limit: int = 5,
    ) -> List[MemoryResponse]:
        """Get memories similar to a given memory."""
        try:
            # Get similar memory IDs from RAG engine
            similar_results = self.rag_engine.get_similar_memories(
                memory_id,
                limit=limit,
            )

            if not similar_results:
                return []

            # Get memory IDs
            memory_ids = [
                UUID(result["memory_id"])
                for result in similar_results
            ]

            # Fetch full memory objects
            query = select(Memory).where(
                and_(
                    Memory.id.in_(memory_ids),
                    Memory.tenant_id == self.tenant_id,
                )
            )

            result = await self.db.execute(query)
            memories = result.scalars().all()

            # Convert to responses with similarity scores
            responses = []
            for memory in memories:
                response = await self._memory_to_response(memory)

                # Add similarity score
                for similar_result in similar_results:
                    if str(memory.id) == similar_result["memory_id"]:
                        response.relevance_score = similar_result["score"]
                        break

                responses.append(response)

            # Sort by similarity score
            responses.sort(key=lambda x: x.relevance_score or 0, reverse=True)

            return responses

        except Exception as e:
            logger.error(f"Failed to get similar memories: {e}")
            raise

    async def get_memories_by_entity(
        self,
        entity_name: str,
        limit: int = 20,
    ) -> List[MemoryResponse]:
        """Get memories that reference a specific entity."""
        try:
            # Normalize entity name
            normalized = entity_name.lower().strip()

            # Query for memories containing the entity
            query = select(Memory).where(
                and_(
                    Memory.tenant_id == self.tenant_id,
                    Memory.entities.contains([normalized]),
                )
            )

            query = query.limit(limit)

            result = await self.db.execute(query)
            memories = result.scalars().all()

            # Convert to responses
            responses = []
            for memory in memories:
                response = await self._memory_to_response(memory)
                responses.append(response)

            return responses

        except Exception as e:
            logger.error(f"Failed to get memories by entity: {e}")
            raise

    def _apply_filters(self, query, filters: Optional[MemoryFilter]):
        """Apply filters to a query."""
        if not filters:
            return query

        if filters.type:
            query = query.where(Memory.type == filters.type)

        if filters.tags:
            # Match any of the provided tags
            query = query.where(Memory.tags.overlap(filters.tags))

        if filters.source_id:
            query = query.where(Memory.source_id == filters.source_id)

        if filters.entities:
            # Match any of the provided entities
            query = query.where(Memory.entities.overlap(filters.entities))

        if filters.created_after:
            query = query.where(Memory.created_at >= filters.created_after)

        if filters.created_before:
            query = query.where(Memory.created_at <= filters.created_before)

        if filters.updated_after:
            query = query.where(Memory.updated_at >= filters.updated_after)

        if filters.updated_before:
            query = query.where(Memory.updated_at <= filters.updated_before)

        if filters.has_wiki_links is not None:
            if filters.has_wiki_links:
                query = query.where(Memory.wiki_links != [])
            else:
                query = query.where(Memory.wiki_links == [])

        if filters.is_indexed is not None:
            query = query.where(Memory.is_indexed == filters.is_indexed)

        return query

    async def _memory_to_response(self, memory: Memory) -> MemoryResponse:
        """Convert memory model to response."""
        # Get backlinks count
        backlinks_count = await self._get_backlinks_count(memory)

        return MemoryResponse(
            id=memory.id,
            title=memory.title,
            content=memory.content,
            type=memory.type,
            source_id=memory.source_id,
            tags=memory.tags,
            metadata=memory.metadata,
            entities=memory.entities,
            wiki_links=memory.wiki_links,
            external_url=memory.external_url,
            external_id=memory.external_id,
            created_at=memory.created_at,
            updated_at=memory.updated_at,
            accessed_at=memory.accessed_at,
            backlinks_count=backlinks_count,
            related_memories=[],  # TODO: Implement related memories
        )

    async def _get_backlinks_count(self, memory: Memory) -> int:
        """Get count of memories that link to this memory."""
        if not memory.entities:
            return 0

        # Count memories that have this memory's title as an entity
        title_normalized = memory.title.lower().strip()

        query = select(Memory).where(
            and_(
                Memory.tenant_id == self.tenant_id,
                Memory.id != memory.id,
                Memory.entities.contains([title_normalized]),
            )
        )

        result = await self.db.execute(query.count())
        return result.scalar() or 0

    async def _index_memory_async(self, memory: Memory) -> bool:
        """Index memory in vector store (can be made async with Celery)."""
        try:
            return self.rag_engine.index_memory(memory)
        except Exception as e:
            logger.error(f"Failed to index memory {memory.id}: {e}")
            return False

    async def _reindex_memory_async(self, memory: Memory) -> bool:
        """Re-index memory in vector store."""
        try:
            return self.rag_engine.update_memory_embedding(memory)
        except Exception as e:
            logger.error(f"Failed to reindex memory {memory.id}: {e}")
            return False