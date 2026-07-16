import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import SessionLocal
from app.models.task import Task
from app.schemas.task import Task as TaskSchema

async def main():
    async with SessionLocal() as db:
        try:
            result = await db.execute(
                select(Task)
                .options(selectinload(Task.assigned_to), selectinload(Task.assigned_by))
                .filter(Task.is_deleted == False)
                .offset(0)
                .limit(10)
            )
            tasks = result.scalars().all()
            print(f"Loaded {len(tasks)} tasks from db.")
            for t in tasks:
                data = TaskSchema.from_orm(t).dict()
                print("Task parsed:", data['id'])
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
