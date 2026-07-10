import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db.session import SessionLocal
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash

async def create_super_admin():
    async with SessionLocal() as db:
        admin_email = "vincent@nurofin.com"
        # Check if exists
        from sqlalchemy.future import select
        result = await db.execute(select(User).filter(User.email == admin_email))
        user = result.scalars().first()
        
        if not user:
            print("Creating super admin user...")
            admin_user = User(
                email=admin_email,
                full_name="Vincent CEO",
                username="vincent_ceo",
                role=RoleEnum.ceo,
                hashed_password=get_password_hash("qwerty")
            )
            db.add(admin_user)
            await db.commit()
            print(f"User created: {admin_email} / qwerty")
        else:
            print(f"User already exists: {admin_email}")

if __name__ == "__main__":
    asyncio.run(create_super_admin())
