"""Add meeting intelligence: timeline, extracted tasks, MOM analysis, task links, notification types

Revision ID: e2f3a4b5c6d7
Revises: d1a2b3c4d5e6
Create Date: 2026-07-12 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, None] = 'd1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extend meeting table with new fields
    op.add_column('meeting', sa.Column('agenda', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('meeting_link', sa.String(), nullable=True))
    op.add_column('meeting', sa.Column('location', sa.String(), nullable=True))
    op.add_column('meeting', sa.Column('timezone', sa.String(), nullable=True))
    op.add_column('meeting', sa.Column('is_recurring', sa.Boolean(), nullable=True))
    op.add_column('meeting', sa.Column('recurrence_rule', sa.String(), nullable=True))
    op.add_column('meeting', sa.Column('created_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_meeting_created_by', 'meeting', 'user', ['created_by_id'], ['id'])

    # 2. Structured MOM analysis fields
    op.add_column('meeting', sa.Column('mom_executive_summary', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('mom_decisions', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('mom_action_items', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('mom_risks', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('mom_blockers', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('mom_followups', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('mom_deadlines', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('mom_important_dates', sa.Text(), nullable=True))

    # 3. Add 'maybe' to participant status enum
    op.execute("ALTER TYPE participantstatusenum ADD VALUE IF NOT EXISTS 'maybe'")

    # 4. Add invited_at to meeting_participants
    op.add_column('meeting_participants', sa.Column('invited_at', sa.Integer(), nullable=True))

    # 5. Create meeting_timeline table
    op.create_table(
        'meeting_timeline',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('meeting_id', sa.Integer(), sa.ForeignKey('meeting.id'), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
    )

    # 6. Create meeting_extracted_tasks table
    op.create_table(
        'meeting_extracted_tasks',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('meeting_id', sa.Integer(), sa.ForeignKey('meeting.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('suggested_owner', sa.String(), nullable=True),
        sa.Column('deadline', sa.String(), nullable=True),
        sa.Column('dependencies', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('real_task_id', sa.Integer(), sa.ForeignKey('task.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
    )

    # 7. Add meeting_id and mom_id to task table
    op.add_column('task', sa.Column('meeting_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_task_meeting', 'task', 'meeting', ['meeting_id'], ['id'])
    op.add_column('task', sa.Column('mom_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_task_mom', 'task', 'meeting_extracted_tasks', ['mom_id'], ['id'])

    # 8. Add link to notification table
    op.add_column('notification', sa.Column('link', sa.String(), nullable=True))

    # 9. Add new notification type values
    new_types = [
        'meeting_invitation', 'meeting_update', 'meeting_cancellation',
        'meeting_acceptance', 'meeting_decline', 'meeting_mom_uploaded',
        'meeting_tasks_extracted', 'meeting_task_assigned',
    ]
    for nt in new_types:
        op.execute(f"ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS '{nt}'")


def downgrade() -> None:
    op.drop_constraint('fk_task_mom', 'task', type_='foreignkey')
    op.drop_column('task', 'mom_id')
    op.drop_constraint('fk_task_meeting', 'task', type_='foreignkey')
    op.drop_column('task', 'meeting_id')

    op.drop_table('meeting_extracted_tasks')
    op.drop_table('meeting_timeline')

    op.drop_column('meeting_participants', 'invited_at')
    op.drop_column('notification', 'link')

    op.drop_column('meeting', 'mom_important_dates')
    op.drop_column('meeting', 'mom_deadlines')
    op.drop_column('meeting', 'mom_followups')
    op.drop_column('meeting', 'mom_blockers')
    op.drop_column('meeting', 'mom_risks')
    op.drop_column('meeting', 'mom_action_items')
    op.drop_column('meeting', 'mom_decisions')
    op.drop_column('meeting', 'mom_executive_summary')
    op.drop_constraint('fk_meeting_created_by', 'meeting', type_='foreignkey')
    op.drop_column('meeting', 'created_by_id')
    op.drop_column('meeting', 'recurrence_rule')
    op.drop_column('meeting', 'is_recurring')
    op.drop_column('meeting', 'timezone')
    op.drop_column('meeting', 'location')
    op.drop_column('meeting', 'meeting_link')
    op.drop_column('meeting', 'agenda')
