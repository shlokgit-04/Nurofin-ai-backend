from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Knowledge(Base):
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False, index=True)
    file_type = Column(String)
    category = Column(String)
    
    uploaded_by_id = Column(Integer, ForeignKey("user.id"))
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    
    uploaded_by = relationship("User")
    project = relationship("Project", back_populates="knowledge_docs")
