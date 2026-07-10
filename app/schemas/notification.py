from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.notification import NotificationTypeEnum

class NotificationBase(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[NotificationTypeEnum] = None
    is_read: Optional[bool] = False
    user_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    title: str
    user_id: int

class NotificationUpdate(NotificationBase):
    is_read: Optional[bool] = None

class NotificationInDBBase(NotificationBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Notification(NotificationInDBBase):
    class Config:
        orm_mode = True
