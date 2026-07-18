import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.core.security import verify_password

async def main():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT * FROM \"user\" WHERE email = 'vincent@nurofin.com'"))
        row = res.first()
        if row:
            d = dict(row._mapping)
            print("Found user!")
            print("Password matches 'qwerty'?", verify_password("qwerty", d["hashed_password"]))
        else:
            print("User not found!")

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
