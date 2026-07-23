from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db.base_class import Base


class TaskHistory(Base):
    __tablename__ = "taskhistory"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    action = Column(String, nullable=False)
    description = Column(String, nullable=True)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    performed_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
