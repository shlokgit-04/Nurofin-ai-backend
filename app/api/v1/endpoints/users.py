from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.user import User
from app.models.department import Department
from app.models.role import Role
from app.schemas.user import (
    UserCreate, 
    UserUpdate, 
    DepartmentCreate, 
    RoleCreate
)
from app.core.security import get_password_hash
from app.core.responses import APIResponse, success_response, error_response

router = APIRouter()

# ----------------- User Management Endpoints -----------------

@router.get("/", response_model=APIResponse)
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    role: Optional[str] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    query = select(User).filter(User.is_deleted == False)
    if role:
        query = query.filter(User.role == role)
    if department:
        query = query.filter(User.department == department)
    
    result = await db.execute(query.offset(skip).limit(limit))
    users = result.scalars().all()
    
    # Serialize with all employee details
    data = [
        {
            "id": u.id, 
            "email": u.email, 
            "username": u.username,
            "full_name": u.full_name, 
            "role": u.role, 
            "department": u.department,
            "phone": u.phone,
            "github": u.github,
            "linkedin": u.linkedin,
            "profile_picture": u.profile_picture,
            "is_active": u.is_active
        } 
        for u in users
    ]
    return success_response(data=data, message="Users fetched successfully")

@router.post("/", response_model=APIResponse)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "CEO":
        raise HTTPException(
            status_code=403,
            detail="Operation restricted to the CEO only."
        )
    # Check if user exists
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
        
    result_username = await db.execute(select(User).filter(User.username == user_in.username))
    if result_username.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
        
    user_data = user_in.dict(exclude={"password"})
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(**user_data, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return success_response(
        data={"id": db_user.id, "email": db_user.email, "role": db_user.role, "department": db_user.department},
        message="User created successfully"
    )

@router.put("/{user_id}", response_model=APIResponse)
async def update_user(
    user_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "CEO":
        raise HTTPException(
            status_code=403,
            detail="Operation restricted to the CEO only."
        )
    result = await db.execute(select(User).filter(User.id == user_id, User.is_deleted == False))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        db_user.hashed_password = hashed_password
        del update_data["password"]
        
    for field, val in update_data.items():
        setattr(db_user, field, val)
        
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return success_response(
        data={"id": db_user.id, "email": db_user.email, "role": db_user.role, "is_active": db_user.is_active},
        message="User updated successfully"
    )

@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "CEO":
        raise HTTPException(
            status_code=403,
            detail="Operation restricted to the CEO only."
        )
    result = await db.execute(select(User).filter(User.id == user_id, User.is_deleted == False))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db_user.is_deleted = True
    db.add(db_user)
    await db.commit()
    return success_response(message="User soft-deleted successfully")


# ----------------- Departments & Roles Endpoints -----------------

@router.get("/departments", response_model=APIResponse)
async def list_departments_and_roles(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(
        select(Department).options(selectinload(Department.roles)).filter(Department.is_deleted == False)
    )
    departments = result.scalars().all()
    
    data = []
    for dept in departments:
        roles_data = []
        for role in dept.roles:
            if not role.is_deleted:
                roles_data.append({
                    "id": role.id,
                    "name": role.name,
                    "is_custom": role.is_custom,
                    "permissions": role.permissions or []
                })
        data.append({
            "id": dept.id,
            "name": dept.name,
            "is_custom": dept.is_custom,
            "roles": roles_data
        })
        
    return success_response(data=data, message="Departments and roles fetched successfully")

@router.post("/departments", response_model=APIResponse)
async def create_department(
    *,
    db: AsyncSession = Depends(deps.get_db),
    dept_in: DepartmentCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "CEO":
        raise HTTPException(
            status_code=403,
            detail="Operation restricted to the CEO only."
        )
    # Check if department exists
    result = await db.execute(select(Department).filter(Department.name == dept_in.name, Department.is_deleted == False))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Department already exists")
        
    db_dept = Department(name=dept_in.name, is_custom=True)
    db.add(db_dept)
    await db.commit()
    await db.refresh(db_dept)
    
    return success_response(
        data={"id": db_dept.id, "name": db_dept.name, "is_custom": db_dept.is_custom},
        message="Department created successfully"
    )

@router.post("/departments/{dept_id}/roles", response_model=APIResponse)
async def create_role_under_department(
    dept_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    role_in: RoleCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "CEO":
        raise HTTPException(
            status_code=403,
            detail="Operation restricted to the CEO only."
        )
    # Check if department exists
    result = await db.execute(select(Department).filter(Department.id == dept_id, Department.is_deleted == False))
    dept = result.scalars().first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    # Check if role exists in this department
    role_res = await db.execute(
        select(Role).filter(Role.name == role_in.name, Role.department_id == dept_id, Role.is_deleted == False)
    )
    if role_res.scalars().first():
        raise HTTPException(status_code=400, detail="Role already exists in this department")
        
    db_role = Role(
        name=role_in.name,
        permissions=role_in.permissions,
        is_custom=True,
        department_id=dept_id
    )
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    
    return success_response(
        data={
            "id": db_role.id,
            "name": db_role.name,
            "is_custom": db_role.is_custom,
            "permissions": db_role.permissions,
            "department_id": db_role.department_id
        },
        message="Role created successfully"
    )

@router.put("/departments/{dept_id}/roles/{role_id}", response_model=APIResponse)
async def update_role_permissions(
    dept_id: int,
    role_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    permissions: list[str],
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "CEO":
        raise HTTPException(
            status_code=403,
            detail="Operation restricted to the CEO only."
        )
    result = await db.execute(
        select(Role).filter(Role.id == role_id, Role.department_id == dept_id, Role.is_deleted == False)
    )
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found or doesn't belong to this department")
        
    role.permissions = permissions
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return success_response(
        data={
            "id": role.id,
            "name": role.name,
            "permissions": role.permissions,
            "department_id": role.department_id
        },
        message="Role permissions updated successfully"
    )

@router.delete("/departments/{dept_id}", response_model=APIResponse)
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "CEO":
        raise HTTPException(
            status_code=403,
            detail="Operation restricted to the CEO only."
        )
    result = await db.execute(select(Department).filter(Department.id == dept_id, Department.is_deleted == False))
    dept = result.scalars().first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    dept.is_deleted = True
    db.add(dept)
    
    # Soft delete all roles under this department
    roles_res = await db.execute(select(Role).filter(Role.department_id == dept_id, Role.is_deleted == False))
    for r in roles_res.scalars().all():
        r.is_deleted = True
        db.add(r)
        
    await db.commit()
    return success_response(message="Department and all its roles soft-deleted successfully")

@router.delete("/departments/{dept_id}/roles/{role_id}", response_model=APIResponse)
async def delete_role(
    dept_id: int,
    role_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "CEO":
        raise HTTPException(
            status_code=403,
            detail="Operation restricted to the CEO only."
        )
    result = await db.execute(
        select(Role).filter(Role.id == role_id, Role.department_id == dept_id, Role.is_deleted == False)
    )
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found or doesn't belong to this department")
        
    role.is_deleted = True
    db.add(role)
    await db.commit()
    return success_response(message="Role soft-deleted successfully")
