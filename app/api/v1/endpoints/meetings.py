from typing import Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.meeting import Meeting
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingUpdate, Meeting as MeetingSchema
from app.core.responses import APIResponse, success_response, error_response

router = APIRouter()

@router.get("", response_model=APIResponse)
async def read_meetings(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    filter: Optional[str] = Query(None, description="Filter by: today, weekly, monthly"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    stmt = select(Meeting).options(selectinload(Meeting.participants), selectinload(Meeting.owner)).filter(Meeting.is_deleted == False)
    
    # Apply date filters
    if filter:
        today_date = datetime.now()
        if filter == 'today':
            today_str = today_date.strftime('%Y-%m-%d')
            stmt = stmt.filter(Meeting.date == today_str)
        elif filter == 'weekly':
            # This week (from today to +7 days for simple planner view)
            end_date = today_date + timedelta(days=7)
            stmt = stmt.filter(Meeting.date >= today_date.strftime('%Y-%m-%d'), Meeting.date <= end_date.strftime('%Y-%m-%d'))
        elif filter == 'monthly':
            # This month (current YYYY-MM)
            month_prefix = today_date.strftime('%Y-%m')
            stmt = stmt.filter(Meeting.date.startswith(month_prefix))

    result = await db.execute(stmt.offset(skip).limit(limit))
    meetings = result.scalars().all()
    
    data = [MeetingSchema.from_orm(m).dict() for m in meetings]
    return success_response(data=data, message="Events fetched successfully")

@router.post("", response_model=APIResponse)
async def create_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    meeting_in: MeetingCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    meeting_data = meeting_in.dict(exclude_unset=True)
    db_meeting = Meeting(**meeting_data, owner_id=current_user.id)
    db.add(db_meeting)
    await db.commit()
    await db.refresh(db_meeting)
    
    res = await db.execute(select(Meeting).options(selectinload(Meeting.owner), selectinload(Meeting.participants)).filter(Meeting.id == db_meeting.id))
    db_meeting_loaded = res.scalars().first()
    
    return success_response(
        data=MeetingSchema.from_orm(db_meeting_loaded).dict(),
        message="Event created successfully"
    )

@router.put("/{id}", response_model=APIResponse)
async def update_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    meeting_in: MeetingUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Meeting).options(selectinload(Meeting.participants), selectinload(Meeting.owner)).filter(Meeting.id == id, Meeting.is_deleted == False))
    meeting = result.scalars().first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Event not found")
        
    update_data = meeting_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meeting, field, value)
        
    await db.commit()
    await db.refresh(meeting)
    return success_response(data=MeetingSchema.from_orm(meeting).dict(), message="Event updated")

@router.delete("/{id}", response_model=APIResponse)
async def delete_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Meeting).filter(Meeting.id == id))
    meeting = result.scalars().first()
    if not meeting:
        return error_response(message="Event not found", status_code=404)
        
    meeting.is_deleted = True
    await db.commit()
    return success_response(message="Event deleted")
