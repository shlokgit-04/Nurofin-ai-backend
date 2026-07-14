import sys, asyncio
sys.path.insert(0, r'C:\Users\Muneesha\Desktop\Nurofin Executive AI\Nurofin-ai-backend')
from app.db.session import SessionLocal
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash
from sqlalchemy import text

async def recreate():
    async with SessionLocal() as db:
        await db.execute(text("DELETE FROM meeting_participants WHERE user_id = 1"))
        await db.execute(text("DELETE FROM project_members WHERE user_id = 1"))
        await db.execute(text("UPDATE task SET assigned_to_id = NULL WHERE assigned_to_id = 1"))
        await db.execute(text("UPDATE task SET assigned_by_id = NULL WHERE assigned_by_id = 1"))
        await db.execute(text("UPDATE project SET owner_id = NULL WHERE owner_id = 1"))
        await db.execute(text("UPDATE meeting SET owner_id = NULL WHERE owner_id = 1"))
        await db.execute(text("DELETE FROM public.user WHERE id = 1"))
        await db.commit()

        u = User(
            email='muneesha09@gmail.com',
            full_name='Muneesha',
            username='muneesha_new',
            role=RoleEnum.employee,
            department='Engineering',
            hashed_password=get_password_hash('qwerty')
        )
        db.add(u)
        await db.commit()
        print('OK: created successfully')

asyncio.run(recreate())
