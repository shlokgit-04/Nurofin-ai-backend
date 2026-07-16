import asyncio
from app.db.session import SessionLocal
from app.models.task import Task
from sqlalchemy import select

async def main():
    async with SessionLocal() as db:
        try:
            res = await db.execute(select(Task).limit(1))
            tasks = res.scalars().all()
            print("Success:", tasks)
        except Exception as e:
            print("Error:")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
