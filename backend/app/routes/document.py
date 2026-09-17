# backend/app/routes/documents.py
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.orm import Session
from database import get_db
from models.all_models import Document, User
from schemas.document import DocumentMetadataResponse
from core.dependencies import get_current_user

logger = logging.getLogger("app.documents")
router = APIRouter(prefix="/documents", tags=["Document Knowledge Management"])

# Configuration Safeguards
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # Strict 2MB ceiling cap protection
ALLOWED_CONTENT_TYPES = {
    "application/json",
    "application/x-yaml",
    "application/pdf",
    "text/yaml",
    "text/markdown",
    "text/plain" # Included for flexible local dev testing (.json files sometimes fall back to plain text)
}

@router.post("/upload", response_model=DocumentMetadataResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Ingests API schemas/markdown strings via multipart form arrays, applies limits, 
    and saves the raw textual content directly into the database.
    """
    logger.info(f"📥 File upload request received from user '{current_user.email}': filename='{file.filename}'")
    
    # 1. Enforce validation constraint guards
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be blank.")
        
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning(f"❌ Upload rejected: Unsupported layout content type '{file.content_type}' passed.")
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported format. Type must align explicitly with JSON, YAML, or Markdown."
        )
        
    # 2. Process file size stream metrics securely
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty payload files cannot be processed.")
    if file_size > MAX_FILE_SIZE_BYTES:
        logger.warning(f"❌ Upload rejected: File size ({file_size} bytes) breaches safety limits.")
        raise HTTPException(status_code=413, detail="File size limit exceeded. Max supported volume: 2MB.")
        
    try:
        # 3. Transform byte streams to legal UTF-8 Python strings
        raw_text_content = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        logger.error("💥 Decoding crash: Uploaded stream string format failed UTF-8 compatibility checks.")
        raise HTTPException(status_code=400, detail="File encoding must align to readable text structures (UTF-8).")
        
    # 4. Commit metadata entity maps to PostgreSQL storage blocks
    new_doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        raw_content=raw_text_content
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    logger.info(f"✅ Success! Ingested Document ID {new_doc.id} securely for tracking layout maps.")
    return new_doc


@router.get("", response_model=List[DocumentMetadataResponse])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieves an aggregated index list of all asset items registered directly to the active session user profile."""
    logger.info(f"📋 Listing active knowledge base items registered to user: {current_user.email}")
    return db.query(Document).filter(Document.user_id == current_user.id).all()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Wipes an asset inventory record out of your structural systems layout layer cleanly."""
    logger.info(f"🗑️ Deletion execution triggered against Knowledge Asset ID {id} by '{current_user.email}'")
    
    doc = db.query(Document).filter(Document.id == id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target document asset not found.")
        
    db.delete(doc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
