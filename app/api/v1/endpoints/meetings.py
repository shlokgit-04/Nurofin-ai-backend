from typing import Any, Optional
from datetime import datetime, timedelta
import json
import time as _time
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.meeting import (
    Meeting, MeetingParticipant, ParticipantStatusEnum,
    MeetingTimeline, MeetingExtractedTask,
)
from app.models.user import User
from app.models.task import Task, TaskStatusEnum, TaskPriorityEnum
from app.models.notification import Notification, NotificationTypeEnum
from app.schemas.meeting import (
    MeetingCreate, MeetingUpdate, Meeting as MeetingSchema,
    MeetingParticipantOut, MOMUpload, MeetingTimelineOut,
    MeetingExtractedTaskOut, ExtractedTaskUpdate, BulkApproveRequest,
)
from app.core.responses import APIResponse, success_response, error_response

router = APIRouter()


async def _add_timeline(db: AsyncSession, meeting_id: int, action: str, description: str = None, user_id: int = None, metadata: dict = None):
    entry = MeetingTimeline(
        meeting_id=meeting_id,
        action=action,
        description=description,
        user_id=user_id,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(entry)


async def _create_notification(db: AsyncSession, user_id: int, title: str, message: str, notif_type: NotificationTypeEnum, link: str = None):
    notif = Notification(
        title=title,
        message=message,
        type=notif_type,
        user_id=user_id,
        link=link,
    )
    db.add(notif)


def _serialize_meeting(m: Meeting) -> dict:
    owner_name = None
    owner_avatar = None
    if m.owner:
        owner_name = m.owner.full_name
        owner_avatar = m.owner.profile_picture

    participants = []
    for pe in (m.participant_entries or []):
        if pe.user:
            participants.append({
                "id": pe.id,
                "user_id": pe.user_id,
                "user_name": pe.user.full_name,
                "user_avatar": pe.user.profile_picture,
                "status": pe.status.value if pe.status else "pending",
            })

    return {
        "id": m.id,
        "title": m.title,
        "description": m.description,
        "agenda": m.agenda,
        "meeting_link": m.meeting_link,
        "location": m.location,
        "date": m.date,
        "start_time": m.start_time,
        "end_time": m.end_time,
        "timezone": m.timezone,
        "type": m.type.value if m.type else "meeting",
        "status": m.status.value if m.status else "scheduled",
        "is_recurring": m.is_recurring,
        "owner_id": m.owner_id,
        "owner_name": owner_name,
        "owner_avatar": owner_avatar,
        "created_by_id": m.created_by_id,
        "participants": participants,
        "participants_count": len(participants),
        "mom_summary": m.mom_summary,
        "mom_file_path": m.mom_file_path,
        "mom_executive_summary": m.mom_executive_summary,
        "mom_decisions": m.mom_decisions,
        "mom_action_items": m.mom_action_items,
        "mom_risks": m.mom_risks,
        "mom_blockers": m.mom_blockers,
        "mom_followups": m.mom_followups,
        "mom_deadlines": m.mom_deadlines,
        "mom_important_dates": m.mom_important_dates,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


def _serialize_timeline(entry: MeetingTimeline) -> dict:
    return {
        "id": entry.id,
        "action": entry.action,
        "description": entry.description,
        "user_id": entry.user_id,
        "user_name": entry.user.full_name if entry.user else None,
        "metadata_json": entry.metadata_json,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


def _serialize_extracted_task(t: MeetingExtractedTask) -> dict:
    return {
        "id": t.id,
        "meeting_id": t.meeting_id,
        "title": t.title,
        "description": t.description,
        "priority": t.priority,
        "suggested_owner": t.suggested_owner,
        "deadline": t.deadline,
        "dependencies": t.dependencies,
        "confidence": t.confidence,
        "status": t.status,
        "real_task_id": t.real_task_id,
    }


@router.get("", response_model=APIResponse)
async def read_meetings(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    filter: Optional[str] = Query(None, description="Filter by: today, weekly, monthly"),
    search: Optional[str] = Query(None, description="Search by title"),
    sort: Optional[str] = Query(None, description="Sort by: date, title, status"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    stmt = (
        select(Meeting)
        .options(
            selectinload(Meeting.participant_entries).selectinload(MeetingParticipant.user),
            selectinload(Meeting.owner),
        )
        .filter(Meeting.is_deleted == False)
    )

    if filter:
        today_date = datetime.now()
        if filter == "today":
            today_str = today_date.strftime("%Y-%m-%d")
            stmt = stmt.filter(Meeting.date == today_str)
        elif filter == "weekly":
            end_date = today_date + timedelta(days=7)
            stmt = stmt.filter(
                Meeting.date >= today_date.strftime("%Y-%m-%d"),
                Meeting.date <= end_date.strftime("%Y-%m-%d"),
            )
        elif filter == "monthly":
            month_prefix = today_date.strftime("%Y-%m")
            stmt = stmt.filter(Meeting.date.startswith(month_prefix))

    if search:
        stmt = stmt.filter(Meeting.title.ilike(f"%{search}%"))

    if sort == "date":
        stmt = stmt.order_by(Meeting.date.desc())
    elif sort == "title":
        stmt = stmt.order_by(Meeting.title)
    elif sort == "status":
        stmt = stmt.order_by(Meeting.status)
    else:
        stmt = stmt.order_by(Meeting.date.desc())

    result = await db.execute(stmt.offset(skip).limit(limit))
    meetings = result.scalars().unique().all()

    data = [_serialize_meeting(m) for m in meetings]
    return success_response(data=data, message="Events fetched successfully")


@router.get("/{id}", response_model=APIResponse)
async def read_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.participant_entries).selectinload(MeetingParticipant.user),
            selectinload(Meeting.owner),
            selectinload(Meeting.mom_uploaded_by),
            selectinload(Meeting.created_by),
            selectinload(Meeting.timeline_entries),
            selectinload(Meeting.extracted_tasks),
        )
        .filter(Meeting.id == id, Meeting.is_deleted == False)
    )
    meeting = result.scalars().first()
    if not meeting:
        return error_response(message="Event not found")

    data = _serialize_meeting(meeting)
    data["timeline"] = [_serialize_timeline(t) for t in (meeting.timeline_entries or [])]
    data["extracted_tasks"] = [_serialize_extracted_task(t) for t in (meeting.extracted_tasks or [])]

    return success_response(data=data, message="Event fetched successfully")


@router.post("", response_model=APIResponse)
async def create_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    meeting_in: MeetingCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    meeting_data = meeting_in.dict(exclude_unset=True, exclude={"participant_ids"})
    participant_ids = meeting_in.participant_ids or []
    db_meeting = Meeting(**meeting_data, owner_id=current_user.id, created_by_id=current_user.id)
    db.add(db_meeting)
    await db.flush()

    for uid in participant_ids:
        entry = MeetingParticipant(
            meeting_id=db_meeting.id,
            user_id=uid,
            status=ParticipantStatusEnum.pending,
            invited_at=int(_time.time()),
        )
        db.add(entry)
        await _create_notification(
            db, uid,
            title=f"Meeting invitation: {meeting_in.title}",
            message=f"You have been invited to '{meeting_in.title}'",
            notif_type=NotificationTypeEnum.meeting_invitation,
            link=f"/meetings?id={db_meeting.id}",
        )

    await _add_timeline(db, db_meeting.id, "meeting_created", f"Meeting '{meeting_in.title}' created", current_user.id)

    await db.commit()

    res = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.participant_entries).selectinload(MeetingParticipant.user),
            selectinload(Meeting.owner),
        )
        .filter(Meeting.id == db_meeting.id)
    )
    db_meeting_loaded = res.scalars().first()

    return success_response(
        data=_serialize_meeting(db_meeting_loaded),
        message="Event created successfully",
    )


@router.put("/{id}", response_model=APIResponse)
async def update_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    meeting_in: MeetingUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.participant_entries).selectinload(MeetingParticipant.user),
            selectinload(Meeting.owner),
        )
        .filter(Meeting.id == id, Meeting.is_deleted == False)
    )
    meeting = result.scalars().first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = meeting_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meeting, field, value)

    await _add_timeline(db, id, "meeting_updated", f"Meeting '{meeting.title}' updated", current_user.id)

    for pe in (meeting.participant_entries or []):
        if pe.user_id != current_user.id:
            await _create_notification(
                db, pe.user_id,
                title=f"Meeting updated: {meeting.title}",
                message=f"The meeting '{meeting.title}' has been updated.",
                notif_type=NotificationTypeEnum.meeting_update,
                link=f"/meetings?id={id}",
            )

    await db.commit()

    res = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.participant_entries).selectinload(MeetingParticipant.user),
            selectinload(Meeting.owner),
        )
        .filter(Meeting.id == id)
    )
    meeting_loaded = res.scalars().first()

    return success_response(data=_serialize_meeting(meeting_loaded), message="Event updated")


@router.delete("/{id}", response_model=APIResponse)
async def delete_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participant_entries))
        .filter(Meeting.id == id)
    )
    meeting = result.scalars().first()
    if not meeting:
        return error_response(message="Event not found")

    for pe in (meeting.participant_entries or []):
        if pe.user_id != current_user.id:
            await _create_notification(
                db, pe.user_id,
                title=f"Meeting cancelled: {meeting.title}",
                message=f"The meeting '{meeting.title}' has been cancelled.",
                notif_type=NotificationTypeEnum.meeting_cancellation,
                link=f"/meetings?id={id}",
            )

    meeting.is_deleted = True
    await db.commit()
    return success_response(message="Event deleted")


@router.post("/{id}/accept", response_model=APIResponse)
async def accept_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == id,
            MeetingParticipant.user_id == current_user.id,
        )
    )
    entry = result.scalars().first()
    if not entry:
        return error_response(message="You are not invited to this meeting")

    entry.status = ParticipantStatusEnum.accepted

    meeting_result = await db.execute(select(Meeting).filter(Meeting.id == id))
    meeting = meeting_result.scalars().first()
    if meeting and meeting.owner_id and meeting.owner_id != current_user.id:
        await _create_notification(
            db, meeting.owner_id,
            title=f"Invitation accepted: {meeting.title}",
            message=f"{current_user.full_name} accepted the invitation to '{meeting.title}'.",
            notif_type=NotificationTypeEnum.meeting_acceptance,
            link=f"/meetings?id={id}",
        )

    await _add_timeline(db, id, "participant_accepted", f"{current_user.full_name} accepted", current_user.id)
    await db.commit()
    return success_response(message="Meeting invitation accepted")


@router.post("/{id}/decline", response_model=APIResponse)
async def decline_meeting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == id,
            MeetingParticipant.user_id == current_user.id,
        )
    )
    entry = result.scalars().first()
    if not entry:
        return error_response(message="You are not invited to this meeting")

    entry.status = ParticipantStatusEnum.declined

    meeting_result = await db.execute(select(Meeting).filter(Meeting.id == id))
    meeting = meeting_result.scalars().first()
    if meeting and meeting.owner_id and meeting.owner_id != current_user.id:
        await _create_notification(
            db, meeting.owner_id,
            title=f"Invitation declined: {meeting.title}",
            message=f"{current_user.full_name} declined the invitation to '{meeting.title}'.",
            notif_type=NotificationTypeEnum.meeting_decline,
            link=f"/meetings?id={id}",
        )

    await _add_timeline(db, id, "participant_declined", f"{current_user.full_name} declined", current_user.id)
    await db.commit()
    return success_response(message="Meeting invitation declined")


@router.post("/{id}/participants", response_model=APIResponse)
async def add_participant(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    user_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(select(Meeting).filter(Meeting.id == id, Meeting.is_deleted == False))
    meeting = result.scalars().first()
    if not meeting:
        return error_response(message="Meeting not found")

    existing = await db.execute(
        select(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == id,
            MeetingParticipant.user_id == user_id,
        )
    )
    if existing.scalars().first():
        return error_response(message="User is already a participant")

    entry = MeetingParticipant(
        meeting_id=id,
        user_id=user_id,
        status=ParticipantStatusEnum.pending,
        invited_at=int(_time.time()),
    )
    db.add(entry)

    await _create_notification(
        db, user_id,
        title=f"Meeting invitation: {meeting.title}",
        message=f"You have been invited to '{meeting.title}'",
        notif_type=NotificationTypeEnum.meeting_invitation,
        link=f"/meetings?id={id}",
    )

    await _add_timeline(db, id, "participant_added", f"New participant added", current_user.id)
    await db.commit()
    return success_response(message="Participant added")


@router.post("/{id}/participants/remove", response_model=APIResponse)
async def remove_participant(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    user_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(select(Meeting).filter(Meeting.id == id, Meeting.is_deleted == False))
    meeting = result.scalars().first()
    if not meeting:
        return error_response(message="Meeting not found")

    existing = await db.execute(
        select(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == id,
            MeetingParticipant.user_id == user_id,
        )
    )
    entry = existing.scalars().first()
    if not entry:
        return error_response(message="User is not a participant")

    await db.delete(entry)
    await _add_timeline(db, id, "participant_removed", f"Participant removed", current_user.id)
    await db.commit()
    return success_response(message="Participant removed")


@router.post("/{id}/mom", response_model=APIResponse)
async def upload_mom(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    mom_in: MOMUpload,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participant_entries))
        .filter(Meeting.id == id, Meeting.is_deleted == False)
    )
    meeting = result.scalars().first()
    if not meeting:
        return error_response(message="Meeting not found")

    meeting.mom_summary = mom_in.summary
    meeting.mom_uploaded_by_id = current_user.id

    await _add_timeline(db, id, "mom_uploaded", f"MOM uploaded by {current_user.full_name}", current_user.id)

    for pe in (meeting.participant_entries or []):
        if pe.user_id != current_user.id:
            await _create_notification(
                db, pe.user_id,
                title=f"MOM uploaded: {meeting.title}",
                message=f"Minutes of Meeting have been uploaded for '{meeting.title}'.",
                notif_type=NotificationTypeEnum.meeting_mom_uploaded,
                link=f"/meetings?id={id}",
            )

    await db.commit()

    res = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.participant_entries).selectinload(MeetingParticipant.user),
            selectinload(Meeting.owner),
        )
        .filter(Meeting.id == id)
    )
    meeting_loaded = res.scalars().first()

    return success_response(
        data=_serialize_meeting(meeting_loaded),
        message="Minutes of Meeting uploaded successfully",
    )


ANALYSIS_PROMPT = """You are an expert meeting analyst. Analyze the following Minutes of Meeting and extract structured data.
Return ONLY a valid JSON object with exactly these fields (no markdown, no code fences):
{
  "executive_summary": "A 2-3 sentence summary of the meeting",
  "decisions": ["decision 1", "decision 2"],
  "action_items": [
    {"title": "task title", "description": "detailed description", "priority": "high|medium|low", "suggested_owner": "person name or null", "deadline": "date string or null"}
  ],
  "risks": ["risk 1"],
  "blockers": ["blocker 1"],
  "followups": ["followup 1"],
  "deadlines": ["deadline description 1"],
  "important_dates": ["date description 1"]
}

If a section has no items, use an empty array [].
If a field cannot be determined, use null for strings or [] for arrays.

Minutes of Meeting:
"""


@router.post("/{id}/mom/analyze", response_model=APIResponse)
async def analyze_mom(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participant_entries))
        .filter(Meeting.id == id, Meeting.is_deleted == False)
    )
    meeting = result.scalars().first()
    if not meeting:
        return error_response(message="Meeting not found")
    if not meeting.mom_summary:
        return error_response(message="No MOM uploaded yet")

    ai_engine_url = "http://localhost:8001/api/v1/chat/analyze"
    prompt = ANALYSIS_PROMPT + meeting.mom_summary

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                ai_engine_url,
                json={
                    "message": prompt,
                    "temperature": 0.1,
                    "max_tokens": 2048,
                    "system_prompt": "You are a meeting analysis AI. Return ONLY valid JSON. No markdown, no code fences, no explanation.",
                },
            )
            resp.raise_for_status()
            ai_data = resp.json()
    except Exception as e:
        return error_response(message=f"AI engine unavailable: {str(e)[:200]}")

    raw_response = ai_data.get("response", "") or ""

    analysis = None
    try:
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        if start != -1 and end > start:
            analysis = json.loads(raw_response[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    if not analysis:
        fallback = {
            "executive_summary": meeting.mom_summary[:500],
            "decisions": [], "action_items": [], "risks": [], "blockers": [],
            "followups": [], "deadlines": [], "important_dates": [],
        }
        analysis = fallback

    meeting.mom_executive_summary = json.dumps(analysis.get("executive_summary"))
    meeting.mom_decisions = json.dumps(analysis.get("decisions", []))
    meeting.mom_action_items = json.dumps(analysis.get("action_items", []))
    meeting.mom_risks = json.dumps(analysis.get("risks", []))
    meeting.mom_blockers = json.dumps(analysis.get("blockers", []))
    meeting.mom_followups = json.dumps(analysis.get("followups", []))
    meeting.mom_deadlines = json.dumps(analysis.get("deadlines", []))
    meeting.mom_important_dates = json.dumps(analysis.get("important_dates", []))

    extracted_tasks_data = analysis.get("action_items", [])
    created_tasks = []
    for item in extracted_tasks_data:
        if not isinstance(item, dict) or not item.get("title"):
            continue
        extracted = MeetingExtractedTask(
            meeting_id=id,
            title=item["title"],
            description=item.get("description"),
            priority=item.get("priority", "medium"),
            suggested_owner=item.get("suggested_owner"),
            deadline=item.get("deadline"),
            status="pending",
            confidence=80,
        )
        db.add(extracted)
        await db.flush()
        created_tasks.append({
            "id": extracted.id,
            "title": extracted.title,
            "priority": extracted.priority,
            "suggested_owner": extracted.suggested_owner,
        })

    await _add_timeline(
        db, id, "mom_analyzed",
        f"AI analyzed MOM - {len(created_tasks)} tasks extracted",
        current_user.id,
        metadata={"tasks_extracted": len(created_tasks)},
    )

    for pe in (meeting.participant_entries or []):
        if pe.user_id != current_user.id:
            await _create_notification(
                db, pe.user_id,
                title=f"MOM analyzed: {meeting.title}",
                message=f"AI analysis complete for '{meeting.title}'. {len(created_tasks)} tasks extracted.",
                notif_type=NotificationTypeEnum.meeting_tasks_extracted,
                link=f"/meetings?id={id}",
            )

    await db.commit()

    res = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.participant_entries).selectinload(MeetingParticipant.user),
            selectinload(Meeting.owner),
        )
        .filter(Meeting.id == id)
    )
    meeting_loaded = res.scalars().first()

    return success_response(
        data={
            **_serialize_meeting(meeting_loaded),
            "extracted_tasks": created_tasks,
            "analysis": analysis,
        },
        message="MOM analysis complete",
    )


@router.get("/{id}/timeline", response_model=APIResponse)
async def get_timeline(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(MeetingTimeline)
        .filter(MeetingTimeline.meeting_id == id, MeetingTimeline.is_deleted == False)
        .order_by(MeetingTimeline.created_at.desc())
    )
    entries = result.scalars().all()

    data = []
    for e in entries:
        user_name = None
        if e.user_id:
            user_res = await db.execute(select(User).filter(User.id == e.user_id))
            user = user_res.scalars().first()
            user_name = user.full_name if user else None
        data.append({
            "id": e.id,
            "action": e.action,
            "description": e.description,
            "user_id": e.user_id,
            "user_name": user_name,
            "metadata_json": e.metadata_json,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        })

    return success_response(data=data, message="Timeline fetched successfully")


@router.get("/{id}/extracted-tasks", response_model=APIResponse)
async def get_extracted_tasks(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(MeetingExtractedTask)
        .filter(MeetingExtractedTask.meeting_id == id, MeetingExtractedTask.is_deleted == False)
    )
    tasks = result.scalars().all()
    data = [_serialize_extracted_task(t) for t in tasks]
    return success_response(data=data, message="Extracted tasks fetched")


@router.post("/{id}/extracted-tasks", response_model=APIResponse)
async def create_extracted_tasks(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    tasks_data: list[dict],
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    meeting_result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participant_entries))
        .filter(Meeting.id == id, Meeting.is_deleted == False)
    )
    meeting = meeting_result.scalars().first()
    if not meeting:
        return error_response(message="Meeting not found")

    created = []
    for td in tasks_data:
        t = MeetingExtractedTask(
            meeting_id=id,
            title=td.get("title", "Untitled"),
            description=td.get("description"),
            priority=td.get("priority", "medium"),
            suggested_owner=td.get("suggested_owner"),
            deadline=td.get("deadline"),
            dependencies=td.get("dependencies"),
            confidence=td.get("confidence", 80),
        )
        db.add(t)
        created.append(td.get("title", "Untitled"))

    await _add_timeline(
        db, id, "tasks_extracted",
        f"AI extracted {len(created)} task(s)",
        current_user.id,
        metadata={"count": len(created)},
    )

    for pe in (meeting.participant_entries or []):
        if pe.user_id != current_user.id:
            await _create_notification(
                db, pe.user_id,
                title=f"Tasks extracted: {meeting.title}",
                message=f"{len(created)} task(s) have been extracted from '{meeting.title}'.",
                notif_type=NotificationTypeEnum.meeting_tasks_extracted,
                link=f"/meetings?id={id}",
            )

    await db.commit()
    return success_response(data={"count": len(created)}, message=f"{len(created)} task(s) extracted")


@router.put("/{id}/extracted-tasks/{task_id}", response_model=APIResponse)
async def update_extracted_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    task_id: int,
    task_in: ExtractedTaskUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(MeetingExtractedTask).filter(
            MeetingExtractedTask.id == task_id,
            MeetingExtractedTask.meeting_id == id,
            MeetingExtractedTask.is_deleted == False,
        )
    )
    task = result.scalars().first()
    if not task:
        return error_response(message="Extracted task not found")

    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    return success_response(data=_serialize_extracted_task(task), message="Extracted task updated")


@router.post("/{id}/extracted-tasks/{task_id}/approve", response_model=APIResponse)
async def approve_extracted_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    task_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(MeetingExtractedTask).filter(
            MeetingExtractedTask.id == task_id,
            MeetingExtractedTask.meeting_id == id,
            MeetingExtractedTask.is_deleted == False,
        )
    )
    ext_task = result.scalars().first()
    if not ext_task:
        return error_response(message="Extracted task not found")

    real_task = Task(
        title=ext_task.title,
        description=ext_task.description,
        priority=TaskPriorityEnum(ext_task.priority) if ext_task.priority in [e.value for e in TaskPriorityEnum] else TaskPriorityEnum.medium,
        deadline=ext_task.deadline,
        source="meeting_mom",
        meeting_id=id,
        assigned_by_id=current_user.id,
    )
    db.add(real_task)
    await db.flush()

    ext_task.real_task_id = real_task.id
    ext_task.status = "approved"

    await _add_timeline(
        db, id, "task_approved",
        f"Task '{ext_task.title}' approved and created",
        current_user.id,
    )

    await db.commit()

    return success_response(
        data={"task_id": real_task.id, "title": real_task.title},
        message="Task approved and created",
    )


@router.post("/{id}/extracted-tasks/{task_id}/reject", response_model=APIResponse)
async def reject_extracted_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    task_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(
        select(MeetingExtractedTask).filter(
            MeetingExtractedTask.id == task_id,
            MeetingExtractedTask.meeting_id == id,
            MeetingExtractedTask.is_deleted == False,
        )
    )
    ext_task = result.scalars().first()
    if not ext_task:
        return error_response(message="Extracted task not found")

    ext_task.status = "rejected"
    await _add_timeline(db, id, "task_rejected", f"Task '{ext_task.title}' rejected", current_user.id)
    await db.commit()
    return success_response(message="Extracted task rejected")


@router.post("/{id}/extracted-tasks/bulk-approve", response_model=APIResponse)
async def bulk_approve_extracted_tasks(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    body: BulkApproveRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    created = []
    for task_id in body.task_ids:
        result = await db.execute(
            select(MeetingExtractedTask).filter(
                MeetingExtractedTask.id == task_id,
                MeetingExtractedTask.meeting_id == id,
                MeetingExtractedTask.is_deleted == False,
            )
        )
        ext_task = result.scalars().first()
        if not ext_task or ext_task.status != "pending":
            continue

        real_task = Task(
            title=ext_task.title,
            description=ext_task.description,
            priority=TaskPriorityEnum(ext_task.priority) if ext_task.priority in [e.value for e in TaskPriorityEnum] else TaskPriorityEnum.medium,
            deadline=ext_task.deadline,
            source="meeting_mom",
            meeting_id=id,
            assigned_by_id=current_user.id,
        )
        db.add(real_task)
        await db.flush()
        ext_task.real_task_id = real_task.id
        ext_task.status = "approved"
        created.append(ext_task.title)

    await _add_timeline(
        db, id, "bulk_approved",
        f"{len(created)} task(s) bulk approved",
        current_user.id,
        metadata={"count": len(created)},
    )

    await db.commit()
    return success_response(data={"count": len(created)}, message=f"{len(created)} task(s) approved")


@router.post("/{id}/extracted-tasks/bulk-reject", response_model=APIResponse)
async def bulk_reject_extracted_tasks(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    body: BulkApproveRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    count = 0
    for task_id in body.task_ids:
        result = await db.execute(
            select(MeetingExtractedTask).filter(
                MeetingExtractedTask.id == task_id,
                MeetingExtractedTask.meeting_id == id,
                MeetingExtractedTask.is_deleted == False,
            )
        )
        ext_task = result.scalars().first()
        if ext_task and ext_task.status == "pending":
            ext_task.status = "rejected"
            count += 1

    await _add_timeline(db, id, "bulk_rejected", f"{count} task(s) bulk rejected", current_user.id)
    await db.commit()
    return success_response(data={"count": count}, message=f"{count} task(s) rejected")
