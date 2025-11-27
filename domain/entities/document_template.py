from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import datetime
from uuid import uuid4

@dataclass
class DocumentTemplate:
    """Доменная модель шаблона документа"""
    id: str
    name: str
    description: str
    content: str
    document_type: str
    variables_schema: Dict[str, Any] = None
    required_variables: List[str] = None
    category: str = "general"
    version: str = "1.0"
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())
        if self.variables_schema is None:
            self.variables_schema = {}
        if self.required_variables is None:
            self.required_variables = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def validate_variables(self, variables: Dict[str, Any]) -> bool:
        """Проверяет корректность переданных переменных"""
        return all(var in variables for var in self.required_variables)
    
    def __repr__(self) -> str:
        return f"DocumentTemplate(id={self.id}, name='{self.name}', type={self.document_type})"
