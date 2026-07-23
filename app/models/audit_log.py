from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db.base_class import Base


class AuditLog(Base):
    __tablename__ = "auditlog"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
