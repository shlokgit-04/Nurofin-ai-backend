from sqlalchemy import Column, Integer, String, Table, ForeignKey
from app.db.base_class import Base

task_labels = Table(
    "task_labels",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("task.id"), primary_key=True),
    Column("label_id", Integer, ForeignKey("label.id"), primary_key=True),
)


class Label(Base):
    __tablename__ = "label"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    color = Column(String, nullable=True)
