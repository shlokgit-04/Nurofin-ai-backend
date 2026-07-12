from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Department(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    is_custom = Column(Boolean, default=False)
    
    roles = relationship("Role", back_populates="department", cascade="all, delete-orphan")
