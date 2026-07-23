from typing import Optional, List
from pydantic import BaseModel
from app.models.issue import IssueStatusEnum, IssuePriorityEnum

class IssueBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[IssuePriorityEnum] = None
    status: Optional[IssueStatusEnum] = None
    attachments: Optional[List[str]] = None
    project_id: Optional[int] = None
    assigned_user_id: Optional[int] = None

class IssueCreate(IssueBase):
    title: str

class IssueUpdate(IssueBase):
    pass

class IssueInDBBase(IssueBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True

class Issue(IssueInDBBase):
    pass
