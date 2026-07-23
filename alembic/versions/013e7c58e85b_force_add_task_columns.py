"""force_add_task_columns

Revision ID: 013e7c58e85b
Revises: 3065874192dd
Create Date: 2026-07-23 19:56:22.461581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '013e7c58e85b'
down_revision: Union[str, None] = '3065874192dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text('''
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='task' AND column_name='start_date') THEN
                ALTER TABLE task ADD COLUMN start_date VARCHAR;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='task' AND column_name='estimated_hours') THEN
                ALTER TABLE task ADD COLUMN estimated_hours DOUBLE PRECISION;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='task' AND column_name='reviewer_id') THEN
                ALTER TABLE task ADD COLUMN reviewer_id INTEGER;
                ALTER TABLE task ADD CONSTRAINT task_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES "user" (id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='task' AND column_name='parent_id') THEN
                ALTER TABLE task ADD COLUMN parent_id INTEGER;
                ALTER TABLE task ADD CONSTRAINT task_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES task (id);
            END IF;
        END $$;
    '''))


def downgrade() -> None:
    pass
