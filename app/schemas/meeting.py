from typing import Optional, List, Union
from datetime import date as dt_date, time as dt_time, datetime
from pydantic import BaseModel
from app.models.meeting import MeetingStatusEnum, MeetingTypeEnum, ParticipantStatusEnum


class MeetingBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    agenda: Optional[str] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    date: Optional[Union[dt_date, datetime, str]] = None
    start_time: Optional[Union[dt_time, str]] = None
    end_time: Optional[Union[dt_time, str]] = None
    timezone: Optional[str] = None
    type: Optional[MeetingTypeEnum] = MeetingTypeEnum.meeting
    status: Optional[MeetingStatusEnum] = MeetingStatusEnum.scheduled
    owner_id: Optional[int] = None


class MeetingCreate(MeetingBase):
    title: str
    participant_ids: Optional[List[int]] = []


class MeetingUpdate(MeetingBase):
    pass


class MeetingParticipantOut(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    status: ParticipantStatusEnum = ParticipantStatusEnum.pending

    class Config:
        orm_mode = True


class MOMUpload(BaseModel):
    summary: str


class MeetingTimelineOut(BaseModel):
    id: int
    action: str
    description: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class MeetingExtractedTaskOut(BaseModel):
    id: int
    meeting_id: int
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    suggested_owner: Optional[str] = None
    deadline: Optional[str] = None
    dependencies: Optional[str] = None
    confidence: int = 80
    status: str = "pending"
    real_task_id: Optional[int] = None

    class Config:
        orm_mode = True


class ExtractedTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    suggested_owner: Optional[str] = None
    deadline: Optional[str] = None


class BulkApproveRequest(BaseModel):
    task_ids: List[int]


class MeetingInDBBase(MeetingBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class Meeting(MeetingInDBBase):
    owner_name: Optional[str] = None
    owner_avatar: Optional[str] = None
    participants: List[MeetingParticipantOut] = []
    participants_count: int = 0
    mom_summary: Optional[str] = None
    mom_file_path: Optional[str] = None
    agenda: Optional[str] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    is_recurring: Optional[bool] = False
    created_at: Optional[str] = None
    mom_executive_summary: Optional[str] = None
    mom_decisions: Optional[str] = None
    mom_action_items: Optional[str] = None
    mom_risks: Optional[str] = None
    mom_blockers: Optional[str] = None
    mom_followups: Optional[str] = None
    mom_deadlines: Optional[str] = None
    mom_important_dates: Optional[str] = None
    created_by_id: Optional[int] = None

    class Config:
        orm_mode = True
