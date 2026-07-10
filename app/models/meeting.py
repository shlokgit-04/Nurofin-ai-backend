from sqlalchemy import Column, Integer, String, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class MeetingStatusEnum(str, enum.Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class MeetingTypeEnum(str, enum.Enum):
    meeting = "meeting"
    reminder = "reminder"
    event = "event"

meeting_participants = Table(
    'meeting_participants', Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meeting.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True)
)

class Meeting(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String) # replacing agenda/notes with description for generic events
    date = Column(String) # 'YYYY-MM-DD'
    start_time = Column(String) # 'HH:MM'
    end_time = Column(String) # 'HH:MM'
    type = Column(Enum(MeetingTypeEnum), default=MeetingTypeEnum.meeting)
    status = Column(Enum(MeetingStatusEnum), default=MeetingStatusEnum.scheduled)
    
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    owner = relationship("User", foreign_keys=[owner_id])
    
    participants = relationship("User", secondary=meeting_participants, backref="meetings")
