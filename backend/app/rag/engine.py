# backend/app/ai/rag/engine.py
import json
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import settings

logger = logging.getLogger("rag")

# 1. Initialize local computational frameworks
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔌 CHANGE THIS LINE: Run completely locally inside RAM without Docker!
qdrant_client = QdrantClient(location=":memory:")

def embed_text(text: str) -> List[float]:
    """Isolated encapsulation wrapper for embedding data pipelines."""
    return embedding_model.encode(text).tolist()

def init_qdrant_collection():
    """Wakes up collection layouts inside local storage parameters securely."""
    try:
        # Check and create collection inside memory instance context safely
        if not qdrant_client.collection_exists(settings.QDRANT_COLLECTION):
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            logger.info(f"📦 Created fresh in-memory Qdrant Collection: {settings.QDRANT_COLLECTION}")
    except Exception as e:
        logger.error(f"💥 Failed initializing Qdrant workspace arrays: {str(e)}")

def parse_and_chunk_document(raw_content: str, filename: str) -> List[Dict[str, Any]]:
    """
    Transforms raw API text configurations into semantic chunks.
    Converts structural JSON OpenAPI blocks into explicit descriptive layouts per endpoint.
    """
    chunks = []
    
    # Check if file content resembles an OpenAPI specification mapping
    if filename.endswith(".json") or '"openapi":' in raw_content or '"swagger":' in raw_content:
        try:
            spec = json.loads(raw_content)
            paths = spec.get("paths", {})
            
            for path_str, path_item in paths.items():
                for method, operation in path_item.items():
                    if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                        continue
                        
                    summary = operation.get("summary", "")
                    description = operation.get("description", "")
                    
                    # Synthesize structural parameters to natural descriptive language blocks
                    chunk_text = (
                        f"Endpoint: {method.upper()} {path_str}\n"
                        f"Summary: {summary}\n"
                        f"Description: {description}\n"
                        f"Context Domain: Exposes interactive operations targeting business sandbox vectors."
                    )
                    
                    chunks.append({
                        "text": chunk_text,
                        "method": method.upper(),
                        "path": path_str
                    })
            if chunks:
                return chunks
        except Exception:
            logger.warning("Parsing fell back to standard line blocks processing schemas.")
            
    # Fallback / Prose processing framework (Markdown/Text segment arrays)
    lines = raw_content.split("\n\n")
    for segment in lines:
        clean_segment = segment.strip()
        if len(clean_segment) > 10:
            chunks.append({
                "text": f"Document context segment from {filename}:\n{clean_segment}",
                "method": "PROSE",
                "path": "N/A"
            })
            
    return chunks
