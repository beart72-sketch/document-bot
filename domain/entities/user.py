from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    profile_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
