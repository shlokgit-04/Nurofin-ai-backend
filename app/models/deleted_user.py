from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db.base_class import Base

class DeletedUser(Base):
    __tablename__ = "deleted_user"

    id               = Column(Integer, primary_key=True, index=True)
    original_user_id = Column(Integer, index=True, nullable=False)
    full_name        = Column(String)
    username         = Column(String)
    email            = Column(String, nullable=False, index=True)
    hashed_password  = Column(String, nullable=True)
    role             = Column(String)
    department       = Column(String)
    github           = Column(String)
    linkedin         = Column(String)
    phone            = Column(String)
    profile_picture  = Column(String)
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime)
    updated_at       = Column(DateTime)
    deleted_at       = Column(DateTime, default=datetime.utcnow)
