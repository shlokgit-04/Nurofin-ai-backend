from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.responses import APIResponse, success_response, error_response

router = APIRouter()

@router.get("/", response_model=APIResponse)
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(User).filter(User.is_deleted == False).offset(skip).limit(limit))
    users = result.scalars().all()
    # Serialize to dicts
    data = [
        {"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role, "is_active": u.is_active} 
        for u in users
    ]
    return success_response(data=data, message="Users fetched successfully")

@router.post("/", response_model=APIResponse)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
    # current_user: User = Depends(deps.get_current_user) # Optionally require admin
) -> Any:
    # Check if user exists
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
        
    user_data = user_in.dict(exclude={"password"})
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(**user_data, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return success_response(
        data={"id": db_user.id, "email": db_user.email, "role": db_user.role},
        message="User created successfully"
    )
