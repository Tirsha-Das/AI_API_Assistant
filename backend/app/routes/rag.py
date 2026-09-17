# backend/app/routes/rag.py
import logging
from fastapi import APIRouter, Depends, Query
from qdrant_client.models import Filter, FieldCondition, MatchValue
from rag.engine import embed_text, qdrant_client
from config import settings
from core.dependencies import get_current_user
from models.all_models import User

logger = logging.getLogger("app.rag")
router = APIRouter(prefix="/rag", tags=["RAG AI Context Retrieval"])

@router.get("/search")
def semantic_similarity_search(
    q: str = Query(..., description="The query string (e.g., 'how to create a customer')"),
    current_user: User = Depends(get_current_user)
):
    """Encapsulates vector queries. Restricts matching frames to the user's data boundary limits."""
    logger.info(f"🔍 Executing semantic RAG search for query: '{q}' (User ID: {current_user.id})")
    
    query_vector = embed_text(q)
    
    # Enforce data boundary isolation: Only look up chunks matching the current user's uploaded assets
    user_filter = Filter(
        must=[
            FieldCondition(key="user_id", match=MatchValue(value=current_user.id))
        ]
    )
    
    # 🔄 UPDATED: Use query_points instead of search to guarantee 100% in-memory compatibility
    search_results = qdrant_client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        query_filter=user_filter,
        limit=3,
        with_payload=True
    )
    
    formatted_results = []
    # query_points returns an object where hits sit inside the '.points' attribute array
    for hit in search_results.points:
        formatted_results.append({
            "score": hit.score,
            "method": hit.payload.get("endpoint_method"),
            "path": hit.payload.get("endpoint_path"),
            "context_chunk": hit.payload.get("chunk_text")
        })
        
    logger.info(f"🎯 Search complete! Found {len(formatted_results)} highly relevant schema chunks.")
    return {"query": q, "matches": formatted_results}
