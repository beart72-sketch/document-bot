from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(Enum):
    CLAIM = "claim"
    CONTRACT = "contract"
    COMPLAINT = "complaint"
    MOTION = "motion"

class DocumentStatus(Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

@dataclass
class Document:
    id: str
    title: str
    content: str
    document_type: str
    status: str
    user_id: str
    template_id: Optional[str] = None
    document_metadata: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
