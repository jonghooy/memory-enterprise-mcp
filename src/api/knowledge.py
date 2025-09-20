"""Knowledge API endpoints for RAG integration."""

import logging
from typing import List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.rag_engine import RAGEngine
from src.models.memory import Memory, MemoryCreate, MemoryResponse
from src.services.memory_service import MemoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class KnowledgeItem(BaseModel):
    """Knowledge item model for frontend integration."""
    id: str
    title: str
    content: str
    tags: List[str]
    created: str
    updated: str
    type: str
    fileName: str = None
    fileSize: int = None


class KnowledgeCreate(BaseModel):
    """Knowledge create model."""
    title: str
    content: str
    tags: List[str]
    type: str


class KnowledgeUpdate(BaseModel):
    """Knowledge update model."""
    title: str
    content: str
    tags: List[str]
    type: str


# Mock tenant and user IDs for now - in production, get from auth
MOCK_TENANT_ID = UUID("00000000-0000-0000-0000-000000000000")
MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.get("/", response_model=List[KnowledgeItem])
async def get_knowledge_items(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all knowledge items."""
    try:
        # Use memory service to fetch items
        memory_service = MemoryService(db, MOCK_TENANT_ID, MOCK_USER_ID)

        # Search with empty query to get all items
        search_params = {
            "query": "",
            "limit": limit,
            "offset": skip,
        }

        memories = await memory_service.search_memories(search_params)

        # Convert to knowledge items
        items = []
        for memory in memories:
            item = KnowledgeItem(
                id=str(memory.id),
                title=memory.title,
                content=memory.content,
                tags=memory.tags or [],
                created=memory.created_at.isoformat() if memory.created_at else datetime.utcnow().isoformat(),
                updated=memory.updated_at.isoformat() if memory.updated_at else datetime.utcnow().isoformat(),
                type=memory.type or "document",
            )
            items.append(item)

        return items

    except Exception as e:
        logger.error(f"Error fetching knowledge items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=KnowledgeItem)
async def create_knowledge_item(
    knowledge: KnowledgeCreate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Create a new knowledge item and index it."""
    try:
        # Create memory service
        memory_service = MemoryService(db, MOCK_TENANT_ID, MOCK_USER_ID)

        # Create memory object
        memory_data = MemoryCreate(
            title=knowledge.title,
            content=knowledge.content,
            type=knowledge.type,
            tags=knowledge.tags,
            entities=[],  # Will be extracted automatically
            metadata={},
        )

        # Create and index memory
        memory = await memory_service.create_memory(memory_data)

        # Convert to knowledge item
        item = KnowledgeItem(
            id=str(memory.id),
            title=memory.title,
            content=memory.content,
            tags=memory.tags or [],
            created=memory.created_at.isoformat() if memory.created_at else datetime.utcnow().isoformat(),
            updated=memory.updated_at.isoformat() if memory.updated_at else datetime.utcnow().isoformat(),
            type=memory.type or "document",
        )

        logger.info(f"Created and indexed knowledge item: {item.id}")
        return item

    except Exception as e:
        logger.error(f"Error creating knowledge item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=KnowledgeItem)
async def upload_knowledge_file(
    file: UploadFile = File(...),
    title: str = Form(None),
    tags: str = Form(""),
    type: str = Form("file"),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file and index its content."""
    try:
        # Read file content
        content = await file.read()
        content_text = content.decode("utf-8", errors="ignore")

        # Use filename as title if not provided
        if not title:
            title = file.filename

        # Parse tags
        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

        # Create memory service
        memory_service = MemoryService(db, MOCK_TENANT_ID, MOCK_USER_ID)

        # Create memory object
        memory_data = MemoryCreate(
            title=title,
            content=content_text,
            type=type,
            tags=tag_list,
            entities=[],
            metadata={
                "fileName": file.filename,
                "fileSize": len(content),
                "contentType": file.content_type,
            },
        )

        # Create and index memory
        memory = await memory_service.create_memory(memory_data)

        # Convert to knowledge item
        item = KnowledgeItem(
            id=str(memory.id),
            title=memory.title,
            content=memory.content,
            tags=memory.tags or [],
            created=memory.created_at.isoformat() if memory.created_at else datetime.utcnow().isoformat(),
            updated=memory.updated_at.isoformat() if memory.updated_at else datetime.utcnow().isoformat(),
            type=memory.type or "file",
            fileName=file.filename,
            fileSize=len(content),
        )

        logger.info(f"Uploaded and indexed file: {item.id}")
        return item

    except Exception as e:
        logger.error(f"Error uploading knowledge file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=KnowledgeItem)
async def get_knowledge_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific knowledge item."""
    try:
        # Create memory service
        memory_service = MemoryService(db, MOCK_TENANT_ID, MOCK_USER_ID)

        # Get memory
        memory = await memory_service.get_memory(UUID(item_id))

        if not memory:
            raise HTTPException(status_code=404, detail="Knowledge item not found")

        # Convert to knowledge item
        item = KnowledgeItem(
            id=str(memory.id),
            title=memory.title,
            content=memory.content,
            tags=memory.tags or [],
            created=memory.created_at.isoformat() if memory.created_at else datetime.utcnow().isoformat(),
            updated=memory.updated_at.isoformat() if memory.updated_at else datetime.utcnow().isoformat(),
            type=memory.type or "document",
        )

        return item

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching knowledge item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{item_id}", response_model=KnowledgeItem)
async def update_knowledge_item(
    item_id: str,
    knowledge: KnowledgeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a knowledge item and re-index it."""
    try:
        # Create memory service
        memory_service = MemoryService(db, MOCK_TENANT_ID, MOCK_USER_ID)

        # Update memory
        memory = await memory_service.update_memory(
            UUID(item_id),
            {
                "title": knowledge.title,
                "content": knowledge.content,
                "tags": knowledge.tags,
                "type": knowledge.type,
            }
        )

        if not memory:
            raise HTTPException(status_code=404, detail="Knowledge item not found")

        # Re-index the memory
        rag_engine = RAGEngine(str(MOCK_TENANT_ID))
        await rag_engine.update_memory(memory)

        # Convert to knowledge item
        item = KnowledgeItem(
            id=str(memory.id),
            title=memory.title,
            content=memory.content,
            tags=memory.tags or [],
            created=memory.created_at.isoformat() if memory.created_at else datetime.utcnow().isoformat(),
            updated=memory.updated_at.isoformat() if memory.updated_at else datetime.utcnow().isoformat(),
            type=memory.type or "document",
        )

        logger.info(f"Updated and re-indexed knowledge item: {item.id}")
        return item

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating knowledge item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}")
async def delete_knowledge_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a knowledge item and remove from index."""
    try:
        # Create memory service
        memory_service = MemoryService(db, MOCK_TENANT_ID, MOCK_USER_ID)

        # Delete memory
        success = await memory_service.delete_memory(UUID(item_id))

        if not success:
            raise HTTPException(status_code=404, detail="Knowledge item not found")

        # Remove from vector index
        rag_engine = RAGEngine(str(MOCK_TENANT_ID))
        await rag_engine.delete_memory(UUID(item_id))

        logger.info(f"Deleted knowledge item: {item_id}")
        return {"success": True, "message": "Knowledge item deleted"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_knowledge(
    query: str = Body(..., embed=True),
    limit: int = Body(10, embed=True),
    db: AsyncSession = Depends(get_db),
):
    """Search knowledge using RAG."""
    try:
        # Create RAG engine
        rag_engine = RAGEngine(str(MOCK_TENANT_ID))

        # Search using RAG
        results = await rag_engine.search(
            query=query,
            k=limit,
            filter_dict={"tenant_id": str(MOCK_TENANT_ID)},
        )

        # Convert results to knowledge items
        items = []
        for result in results:
            # Extract metadata
            metadata = result.metadata or {}

            item = KnowledgeItem(
                id=metadata.get("memory_id", ""),
                title=metadata.get("title", ""),
                content=result.text,
                tags=metadata.get("tags", []),
                created=metadata.get("created_at", datetime.utcnow().isoformat()),
                updated=metadata.get("updated_at", datetime.utcnow().isoformat()),
                type=metadata.get("type", "document"),
            )
            items.append(item)

        logger.info(f"RAG search for '{query}' returned {len(items)} results")
        return {"query": query, "results": items}

    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))