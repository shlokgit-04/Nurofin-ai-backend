from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class RoleEnum(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    ceo = "ceo"
    manager = "manager"
    team_lead = "team_lead"
    employee = "employee"

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.employee)
    department = Column(String)
    github = Column(String)
    linkedin = Column(String)
    phone = Column(String)
    profile_picture = Column(String)
    is_active = Column(Boolean(), default=True)
    
    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assigned_to")
    created_tasks = relationship("Task", foreign_keys="Task.assigned_by_id", back_populates="assigned_by")

    @property
    def name(self):
        return self.full_name

    @property
    def avatar(self):
        return self.profile_picture
