from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base_class import Base

class NotificationTypeEnum(str, enum.Enum):
    task_assigned = "task_assigned"
    deadline = "deadline"
    meeting_reminder = "meeting_reminder"
    project_update = "project_update"
    finance_reminder = "finance_reminder"

class Notification(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(String)
    type = Column(Enum(NotificationTypeEnum))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="notifications")
