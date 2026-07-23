from typing import Optional
from pydantic import BaseModel

class KnowledgeBase(BaseModel):
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    category: Optional[str] = None
    uploaded_by_id: Optional[int] = None
    project_id: Optional[int] = None

class KnowledgeCreate(KnowledgeBase):
    file_name: str

class KnowledgeUpdate(KnowledgeBase):
    pass

class KnowledgeInDBBase(KnowledgeBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True

class Knowledge(KnowledgeInDBBase):
    pass
