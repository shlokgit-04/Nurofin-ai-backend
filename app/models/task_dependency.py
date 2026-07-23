from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base_class import Base


class TaskDependency(Base):
    __tablename__ = "taskdependency"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=True)
    depends_on_id = Column(Integer, ForeignKey("task.id"), nullable=True)
    dependency_type = Column(String, nullable=True)
