from typing import Optional, List, Union
from datetime import date as dt_date, time as dt_time, datetime
from pydantic import BaseModel
from app.models.meeting import MeetingStatusEnum, MeetingTypeEnum
from app.schemas.user import UserBasic

class MeetingBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[Union[dt_date, datetime, str]] = None
    start_time: Optional[Union[dt_time, str]] = None
    end_time: Optional[Union[dt_time, str]] = None
    type: Optional[MeetingTypeEnum] = MeetingTypeEnum.meeting
    status: Optional[MeetingStatusEnum] = MeetingStatusEnum.scheduled
    owner_id: Optional[int] = None

class MeetingCreate(MeetingBase):
    title: str

class MeetingUpdate(MeetingBase):
    pass

class MeetingInDBBase(MeetingBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

class Meeting(MeetingInDBBase):
    owner: Optional[UserBasic] = None
    participants: List[UserBasic] = []

    class Config:
        orm_mode = True
