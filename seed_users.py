import sys, asyncio, selectors
sys.path.insert(0, r'C:\Users\Muneesha\Desktop\Nurofin Executive AI\Nurofin-ai-backend')
from app.db.session import SessionLocal
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash

async def seed():
    async with SessionLocal() as db:
        v = User(
            email='vincent@nurofin.com',
            full_name='Vincent CEO',
            username='vincent_ceo',
            role=RoleEnum.ceo,
            department='Executive',
            hashed_password=get_password_hash('qwerty')
        )
        db.add(v)
        m = User(
            email='muneesha09@gmail.com',
            full_name='Muneesha',
            username='muneesha',
            role=RoleEnum.manager,
            department='Engineering',
            hashed_password=get_password_hash('qwerty')
        )
        db.add(m)
        await db.commit()
        print('Done: vincent@nurofin.com (ceo) + muneesha09@gmail.com (manager) | password: qwerty')

if __name__ == '__main__':
    asyncio.run(seed(), loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()))
