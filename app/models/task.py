from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class TaskStatusEnum(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    completed = "completed"
    blocked = "blocked"

class TaskPriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.todo)
    priority = Column(Enum(TaskPriorityEnum), default=TaskPriorityEnum.medium)
    deadline = Column(String) # Can be DateTime but specs say deadline, lets stick to string for simple parsing for now
    progress = Column(Float, default=0.0)
    source = Column(String) # Email, Voice, Manual
    
    assigned_to_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    assigned_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id], back_populates="created_tasks")
    project = relationship("Project", back_populates="tasks")
