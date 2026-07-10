from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, Project as ProjectSchema
from app.core.responses import APIResponse, success_response, error_response

router = APIRouter()

@router.get("", response_model=APIResponse)
async def read_projects(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Get projects where user is owner or member
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.members), selectinload(Project.owner))
        .filter(Project.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()
    # Pydantic will auto-serialize relationships due to from_attributes=True in schema
    data = [ProjectSchema.from_orm(p).dict() for p in projects]
    return success_response(data=data, message="Projects fetched successfully")

@router.post("", response_model=APIResponse)
async def create_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Create project
    project_data = project_in.dict(exclude_unset=True)
    db_project = Project(**project_data, owner_id=current_user.id)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    return success_response(
        data=ProjectSchema.from_orm(db_project).dict(),
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
    await db.refresh(project)
    return success_response(data=ProjectSchema.from_orm(project).dict(), message="Project updated")

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
        return error_response(message="Project not found", status_code=404)
        
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
    # 1. Get project
    proj_result = await db.execute(select(Project).options(selectinload(Project.members)).filter(Project.id == id))
    project = proj_result.scalars().first()
    if not project:
        return error_response(message="Project not found", status_code=404)
    
    # 2. Get user
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        return error_response(message="User not found", status_code=404)
        
    # 3. Add member
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
    proj_result = await db.execute(select(Project).options(selectinload(Project.members)).filter(Project.id == id))
    project = proj_result.scalars().first()
    if not project:
        return error_response(message="Project not found", status_code=404)
        
    project.members = [m for m in project.members if m.id != user_id]
    await db.commit()
    return success_response(message="Member removed successfully")
