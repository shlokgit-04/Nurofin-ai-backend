from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db.base_class import Base


class TaskComment(Base):
    __tablename__ = "taskcomment"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("taskcomment.id"), nullable=True)
    attachments = Column(Text, nullable=True)
