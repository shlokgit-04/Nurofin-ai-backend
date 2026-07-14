"""Add MeetingParticipant status, MOM fields, and meeting_participants id column

Revision ID: d1a2b3c4d5e6
Revises: c452d867cfe0
Create Date: 2026-07-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1a2b3c4d5e6'
down_revision: Union[str, None] = 'c452d867cfe0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add id column and status to meeting_participants
    # First drop the old composite PK constraint
    op.execute("ALTER TABLE meeting_participants DROP CONSTRAINT IF EXISTS meeting_participants_pkey")

    # Add auto-increment id column as new primary key
    op.add_column('meeting_participants', sa.Column('id', sa.Integer(), nullable=False))
    op.execute("ALTER TABLE meeting_participants ADD PRIMARY KEY (id)")

    # Add status column with default
    participantstatusenum = sa.Enum('pending', 'accepted', 'declined', name='participantstatusenum')
    participantstatusenum.create(op.get_bind(), checkfirst=True)
    op.add_column('meeting_participants', sa.Column('status', participantstatusenum, nullable=True))

    # Set existing rows to 'pending'
    op.execute("UPDATE meeting_participants SET status = 'pending' WHERE status IS NULL")

    # 2. Add MOM fields to meeting table
    op.add_column('meeting', sa.Column('mom_file_path', sa.String(), nullable=True))
    op.add_column('meeting', sa.Column('mom_summary', sa.String(), nullable=True))
    op.add_column('meeting', sa.Column('mom_uploaded_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_meeting_mom_uploaded_by', 'meeting', 'user', ['mom_uploaded_by_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_meeting_mom_uploaded_by', 'meeting', type_='foreignkey')
    op.drop_column('meeting', 'mom_uploaded_by_id')
    op.drop_column('meeting', 'mom_summary')
    op.drop_column('meeting', 'mom_file_path')

    op.drop_column('meeting_participants', 'status')
    op.drop_column('meeting_participants', 'id')

    op.execute("ALTER TABLE meeting_participants ADD PRIMARY KEY (meeting_id, user_id)")

    op.execute("DROP TYPE IF EXISTS participantstatusenum")
