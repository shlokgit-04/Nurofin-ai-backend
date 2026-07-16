import asyncio
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db.session import SessionLocal
from sqlalchemy import text

async def main():
    async with SessionLocal() as db:
        queries = [
            # Create extracted tasks if not exists
            """
            CREATE TABLE IF NOT EXISTS meeting_extracted_tasks (
                id SERIAL PRIMARY KEY,
                meeting_id INTEGER NOT NULL REFERENCES meeting(id),
                title VARCHAR NOT NULL,
                description TEXT,
                priority VARCHAR,
                suggested_owner VARCHAR,
                deadline VARCHAR,
                dependencies TEXT,
                confidence INTEGER,
                status VARCHAR,
                real_task_id INTEGER REFERENCES task(id),
                created_at TIMESTAMP WITHOUT TIME ZONE,
                updated_at TIMESTAMP WITHOUT TIME ZONE,
                is_deleted BOOLEAN
            );
            """,
            # Add missing columns
            "ALTER TABLE task ADD COLUMN IF NOT EXISTS meeting_id INTEGER;",
            "ALTER TABLE task ADD COLUMN IF NOT EXISTS mom_id INTEGER;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS agenda TEXT;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS meeting_link VARCHAR;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS location VARCHAR;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS timezone VARCHAR;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS recurrence_rule VARCHAR;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS created_by_id INTEGER;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS mom_executive_summary TEXT;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS mom_decisions TEXT;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS mom_action_items TEXT;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS mom_risks TEXT;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS mom_blockers TEXT;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS mom_followups TEXT;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS mom_deadlines TEXT;",
            "ALTER TABLE meeting ADD COLUMN IF NOT EXISTS mom_important_dates TEXT;",
            "ALTER TABLE meeting_participants ADD COLUMN IF NOT EXISTS invited_at INTEGER;",
            "ALTER TABLE notification ADD COLUMN IF NOT EXISTS link VARCHAR;"
        ]
        
        # Enums can't use IF NOT EXISTS inside ALTER TYPE natively without a plpgsql block in old postgres,
        # but let's try to add the enums in a safe way
        enums = [
            "ALTER TYPE participantstatusenum ADD VALUE IF NOT EXISTS 'maybe';",
            "ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'meeting_invitation';",
            "ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'meeting_update';",
            "ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'meeting_cancellation';",
            "ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'meeting_acceptance';",
            "ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'meeting_decline';",
            "ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'meeting_mom_uploaded';",
            "ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'meeting_tasks_extracted';",
            "ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'meeting_task_assigned';"
        ]
        
        try:
            for q in queries:
                await db.execute(text(q))
            
            # Enums need to run outside of standard transaction blocks or individually sometimes,
            # but since we're using asyncpg/psycopg, let's just run them and ignore duplicates if the IF NOT EXISTS works.
            for e in enums:
                try:
                    await db.execute(text(e))
                except Exception as enum_err:
                    print(f"Skipping enum error (likely already exists): {enum_err}")
                    
            await db.commit()
            print("Successfully added missing database schema components.")
        except Exception as e:
            print("Error:")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
