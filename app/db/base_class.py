from typing import Any
from sqlalchemy.orm import as_declarative, declared_attr

from sqlalchemy import Column, DateTime, Boolean
import datetime

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
