from pydantic import BaseModel
from datetime import datetime

class DocumentMetadataResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True
