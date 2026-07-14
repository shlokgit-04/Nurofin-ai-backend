from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import RoleEnum

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    role: Optional[RoleEnum] = None
    department: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    is_active: Optional[bool] = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True

# Additional properties to return via API
class User(UserInDBBase):
    class Config:
        from_attributes = True

class UserBasic(BaseModel):
    id: int
    name: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

    class Config:
        from_attributes = True
