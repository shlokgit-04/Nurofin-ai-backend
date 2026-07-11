from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Role(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    is_custom = Column(Boolean, default=False)
    permissions = Column(JSON, nullable=True)  # Store permission keys list: e.g. ["read_finance", "edit_tasks"]
    
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    department = relationship("Department", back_populates="roles")
