from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.responses import APIResponse, success_response, error_response

router = APIRouter()


def _fmt_date(d) -> Optional[str]:
    """Return ISO string for datetime or pass through a string as-is."""
    if d is None:
        return None
    if hasattr(d, 'isoformat'):
        return d.isoformat()
    return str(d)


def _serialize_project(p: Project) -> dict:
    """Safely serialize a project with its eagerly loaded relationships."""
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "status": p.status.value if hasattr(p.status, 'value') else p.status,
        "priority": p.priority.value if hasattr(p.priority, 'value') else p.priority,
        "progress": p.progress,
        "start_date": _fmt_date(p.start_date),
        "end_date":   _fmt_date(p.end_date),
        "git_url": p.git_url,
        "budget": p.budget,
        "spending": p.spending,
        "owner_id": p.owner_id,
        "owner": {
            "id": p.owner.id,
            "name": p.owner.full_name,
            "avatar": p.owner.profile_picture,
        } if p.owner else None,
        "members": [
            {
                "id": m.id,
                "name": m.full_name,
                "avatar": m.profile_picture,
                "role": m.role,
            }
            for m in (p.members or [])
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status.value if hasattr(t.status, 'value') else t.status,
                "priority": t.priority.value if hasattr(t.priority, 'value') else t.priority,
                "deadline": _fmt_date(t.deadline),
                "progress": t.progress,
                "assigned_to_id": t.assigned_to_id,
            }
            for t in (p.tasks or [])
            if not t.is_deleted
        ],
    }


@router.get("", response_model=APIResponse)
async def read_projects(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.members),
            selectinload(Project.owner),
            selectinload(Project.tasks)
        )
        .filter(Project.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()
    data = [_serialize_project(p) for p in projects]
    return success_response(data=data, message="Projects fetched successfully")


@router.post("", response_model=APIResponse)
async def create_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project_data = project_in.dict(exclude_unset=True)
    db_project = Project(**project_data, owner_id=current_user.id)
    db.add(db_project)
    await db.commit()

    # Reload with relationships for serialization
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.members),
            selectinload(Project.owner),
            selectinload(Project.tasks)
        )
        .filter(Project.id == db_project.id)
    )
    db_project_loaded = result.scalars().first()
    return success_response(
        data=_serialize_project(db_project_loaded),
        message="Project created successfully"
    )


@router.put("/{id}", response_model=APIResponse)
async def update_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Project).filter(Project.id == id, Project.is_deleted == False))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    await db.commit()

    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.members),
            selectinload(Project.owner),
            selectinload(Project.tasks)
        )
        .filter(Project.id == id)
    )
    project_loaded = result.scalars().first()
    return success_response(data=_serialize_project(project_loaded), message="Project updated")


@router.delete("/{id}", response_model=APIResponse)
async def delete_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Project).filter(Project.id == id))
    project = result.scalars().first()
    if not project:
        return error_response(message="Project not found")

    project.is_deleted = True
    await db.commit()
    return success_response(message="Project deleted")


@router.post("/{id}/members/{user_id}", response_model=APIResponse)
async def add_member(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    user_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    proj_result = await db.execute(
        select(Project).options(selectinload(Project.members)).filter(Project.id == id)
    )
    project = proj_result.scalars().first()
    if not project:
        return error_response(message="Project not found")

    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        return error_response(message="User not found")

    if user not in project.members:
        project.members.append(user)
        await db.commit()
        return success_response(message="Member added successfully")
    return success_response(message="User is already a member")


@router.delete("/{id}/members/{user_id}", response_model=APIResponse)
async def remove_member(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    user_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    proj_result = await db.execute(
        select(Project).options(selectinload(Project.members)).filter(Project.id == id)
    )
    project = proj_result.scalars().first()
    if not project:
        return error_response(message="Project not found")

    project.members = [m for m in project.members if m.id != user_id]
    await db.commit()
    return success_response(message="Member removed successfully")
