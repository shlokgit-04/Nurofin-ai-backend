import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import SessionLocal
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash

async def create_users():
    async with SessionLocal() as db:
        users = [
            {
                "email": "muneesha@nurofin.ai",
                "username": "muneesha",
                "full_name": "Muneesha",
                "role": RoleEnum.admin,
                "password": "password123",
                "profile_picture": "https://ui-avatars.com/api/?name=Muneesha&background=0D8ABC&color=fff"
            },
            {
                "email": "aryan@nurofin.ai",
                "username": "aryan",
                "full_name": "Aryan",
                "role": RoleEnum.manager,
                "password": "password123",
                "profile_picture": "https://ui-avatars.com/api/?name=Aryan&background=ff5a5a&color=fff"
            },
            {
                "email": "shlok@nurofin.ai",
                "username": "shlok",
                "full_name": "Shlok",
                "role": RoleEnum.employee,
                "password": "password123",
                "profile_picture": "https://ui-avatars.com/api/?name=Shlok&background=5aff5a&color=fff"
            }
        ]
        
        for u in users:
            res = await db.execute(select(User).filter(User.username == u["username"]))
            if res.scalars().first():
                continue
            password = u.pop("password")
            db_user = User(**u, hashed_password=get_password_hash(password))
            db.add(db_user)
            
        await db.commit()
        print("Mock users created successfully!")

if __name__ == "__main__":
    asyncio.run(create_users())
