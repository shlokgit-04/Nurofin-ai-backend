import asyncio
from sqlalchemy import select
from app.db.session import SessionLocal

# Import all models
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.models.meeting import Meeting, MeetingParticipant, MeetingExtractedTask, MeetingTimeline
from app.models.notification import Notification
# try to import any other models if they exist, but these are the main ones

async def main():
    async with SessionLocal() as db:
        models = [User, Task, Project, Meeting, MeetingParticipant, MeetingExtractedTask, MeetingTimeline, Notification]
        for model in models:
            try:
                await db.execute(select(model).limit(1))
                print(f"{model.__name__}: OK")
            except Exception as e:
                print(f"{model.__name__}: ERROR - {str(e)}")

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
