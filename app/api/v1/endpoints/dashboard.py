from typing import Any
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api import deps
from app.models.project import Project, ProjectStatusEnum
from app.models.task import Task, TaskPriorityEnum
from app.models.meeting import Meeting
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.core.responses import APIResponse, success_response

router = APIRouter()

@router.get("/summary", response_model=APIResponse)
async def get_dashboard_summary(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Active Projects
    res = await db.execute(select(func.count(Project.id)).filter(Project.status == ProjectStatusEnum.active, Project.is_deleted == False))
    active_projects = res.scalar() or 0
    
    # Completed Projects
    res = await db.execute(select(func.count(Project.id)).filter(Project.status == ProjectStatusEnum.completed, Project.is_deleted == False))
    completed_projects = res.scalar() or 0
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # Today's Tasks (deadline is today)
    res = await db.execute(select(func.count(Task.id)).filter(Task.deadline == today_str, Task.is_deleted == False))
    today_tasks = res.scalar() or 0
    
    # Overdue Tasks (deadline < today and status != completed)
    res = await db.execute(select(func.count(Task.id)).filter(Task.deadline < today_str, Task.status != 'completed', Task.is_deleted == False))
    overdue_tasks = res.scalar() or 0
    
    # Today's Meetings
    res = await db.execute(select(func.count(Meeting.id)).filter(Meeting.date == today_str, Meeting.is_deleted == False))
    today_meetings = res.scalar() or 0
    
    # High Priority Tasks
    res = await db.execute(select(func.count(Task.id)).filter(Task.priority.in_([TaskPriorityEnum.high, TaskPriorityEnum.critical]), Task.is_deleted == False))
    high_priority_tasks = res.scalar() or 0

    data = {
        "activeProjects": active_projects,
        "completedProjects": completed_projects,
        "todayTasks": today_tasks,
        "overdueTasks": overdue_tasks,
        "todayMeetings": today_meetings,
        "highPriorityTasks": high_priority_tasks
    }
    
    return success_response(data=data, message="Dashboard summary fetched successfully")
