import enum
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Enum
from app.db.base_class import Base


class TransferStatusEnum(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class TaskTransfer(Base):
    __tablename__ = "tasktransfer"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    from_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    reason = Column(Text, nullable=False)
    current_progress = Column(Float, nullable=True)
    remaining_work = Column(Text, nullable=True)
    new_deadline = Column(String, nullable=True)
    transfer_notes = Column(Text, nullable=True)
    status = Column(Enum(TransferStatusEnum), default=TransferStatusEnum.pending)
    transferred_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
