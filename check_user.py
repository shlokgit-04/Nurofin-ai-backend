import asyncio
from sqlalchemy import text
from app.db.session import engine

async def main():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT * FROM \"user\" WHERE email = 'vincent@nurofin.com'"))
        row = res.first()
        if row:
            d = dict(row._mapping)
            print("User found:", d["email"], "Role:", d["role"])
            print("Hashed password:", d["hashed_password"])
        else:
            print("User NOT found!")

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
