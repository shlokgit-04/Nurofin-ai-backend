import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from app.db.base_class import Base


class QuarterStatusEnum(str, enum.Enum):
    planning = "planning"
    active = "active"
    closed = "closed"
    archived = "archived"


class Quarter(Base):
    __tablename__ = "quarter"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    label = Column(String)
    fiscal_year = Column(Integer, nullable=False)
    quarter_number = Column(Integer, nullable=False)
    start_date = Column(String)
    end_date = Column(String)
    status = Column(Enum(QuarterStatusEnum), default=QuarterStatusEnum.planning)
    goals = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
