import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.base_class import Base
# Import all models to ensure they are registered with Base.metadata
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.meeting import Meeting
from app.models.issue import Issue
from app.models.knowledge import Knowledge
from app.models.notification import Notification

async def reset_db():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database reset successfully.")

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(reset_db())
