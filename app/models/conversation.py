from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class Conversation(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, default="New Conversation")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    user = relationship("User", backref="conversations")
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        order_by="ConversationMessage.created_at",
        cascade="all, delete-orphan",
    )


class ConversationMessage(Base):
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    files_json = Column(Text, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
