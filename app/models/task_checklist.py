from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db.base_class import Base


class TaskChecklist(Base):
    __tablename__ = "taskchecklist"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    title = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    completed_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    completed_at = Column(String, nullable=True)
