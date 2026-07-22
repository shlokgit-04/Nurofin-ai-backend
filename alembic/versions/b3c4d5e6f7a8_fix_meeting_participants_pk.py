"""fix_meeting_participants_pk_and_constraints

Revision ID: b3c4d5e6f7a8
Revises: f779ecb38512
Create Date: 2026-07-22 11:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = 'f779ecb38512'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE meeting_participants DROP CONSTRAINT IF EXISTS meeting_participants_pkey")
    op.execute("ALTER TABLE meeting_participants ALTER COLUMN id SET NOT NULL")
    op.execute("CREATE SEQUENCE IF NOT EXISTS meeting_participants_id_seq OWNED BY meeting_participants.id")
    op.execute("ALTER TABLE meeting_participants ALTER COLUMN id SET DEFAULT nextval('meeting_participants_id_seq')")
    op.execute("SELECT setval('meeting_participants_id_seq', COALESCE((SELECT MAX(id) FROM meeting_participants), 0) + 1, false)")
    op.execute("ALTER TABLE meeting_participants ADD CONSTRAINT meeting_participants_pkey PRIMARY KEY (id)")
    op.execute("ALTER TABLE meeting_participants ADD CONSTRAINT uq_meeting_participant UNIQUE (meeting_id, user_id)")


def downgrade() -> None:
    op.execute("ALTER TABLE meeting_participants DROP CONSTRAINT IF EXISTS uq_meeting_participant")
    op.execute("ALTER TABLE meeting_participants DROP CONSTRAINT IF EXISTS meeting_participants_pkey")
    op.execute("ALTER TABLE meeting_participants ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS meeting_participants_id_seq")
    op.execute("ALTER TABLE meeting_participants ALTER COLUMN id DROP NOT NULL")
    op.execute("ALTER TABLE meeting_participants ADD CONSTRAINT meeting_participants_pkey PRIMARY KEY (meeting_id, user_id)")
