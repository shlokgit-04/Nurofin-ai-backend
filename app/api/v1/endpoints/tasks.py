from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema
from app.core.responses import APIResponse, success_response, error_response

router = APIRouter()

@router.get("", response_model=APIResponse)
async def read_tasks(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assigned_to), selectinload(Task.assigned_by))
        .filter(Task.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()
    data = [TaskSchema.from_orm(t).dict() for t in tasks]
    return success_response(data=data, message="Tasks retrieved successfully")

@router.post("", response_model=APIResponse)
async def create_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    try:
        task_data = task_in.dict(exclude_unset=True)
        db_task = Task(**task_data, assigned_by_id=current_user.id)
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        
        # Reload with relationships
        res = await db.execute(select(Task).options(selectinload(Task.assigned_to), selectinload(Task.assigned_by)).filter(Task.id == db_task.id))
        db_task_loaded = res.scalars().first()
        
        return success_response(
            data=TaskSchema.from_orm(db_task_loaded).dict(),
            message="Task created successfully"
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=400, content={"message": str(e), "traceback": error_details})

@router.put("/{id}", response_model=APIResponse)
async def update_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Task).options(selectinload(Task.assigned_to), selectinload(Task.assigned_by)).filter(Task.id == id, Task.is_deleted == False))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
        
    await db.commit()
    await db.refresh(task)
    return success_response(data=TaskSchema.from_orm(task).dict(), message="Task updated")

@router.delete("/{id}", response_model=APIResponse)
async def delete_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Task).filter(Task.id == id))
    task = result.scalars().first()
    if not task:
        return error_response(message="Task not found", status_code=404)
        
    task.is_deleted = True
    await db.commit()
    return success_response(message="Task deleted")
