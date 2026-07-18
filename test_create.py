import asyncio
from sqlalchemy import text
from app.db.session import engine

async def main():
    async with engine.begin() as conn:
        try:
            # Try to insert a user with an invalid role
            await conn.execute(text("""
                INSERT INTO "user" (email, hashed_password, role, is_active)
                VALUES ('test_enum@example.com', 'pwd', 'CustomRole', true)
            """))
            print("Success")
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
