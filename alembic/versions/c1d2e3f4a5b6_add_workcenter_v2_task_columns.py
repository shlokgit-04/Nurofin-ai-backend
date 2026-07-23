"""add_workcenter_v2_task_columns

Revision ID: c1d2e3f4a5b6
Revises: b1c2d3e4f5a6
Create Date: 2026-07-23 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table, column):
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT column_name FROM information_schema.columns WHERE table_name=:t AND column_name=:c"),
        {"t": table, "c": column}
    )
    return result.fetchone() is not None


def upgrade() -> None:
    if not column_exists('task', 'start_date'):
        op.add_column('task', sa.Column('start_date', sa.String(), nullable=True))
    if not column_exists('task', 'estimated_hours'):
        op.add_column('task', sa.Column('estimated_hours', sa.Float(), nullable=True))
    if not column_exists('task', 'reviewer_id'):
        op.add_column('task', sa.Column('reviewer_id', sa.Integer(), nullable=True))
        op.create_foreign_key('task_reviewer_id_fkey', 'task', 'user', ['reviewer_id'], ['id'])
    if not column_exists('task', 'parent_id'):
        op.add_column('task', sa.Column('parent_id', sa.Integer(), nullable=True))
        op.create_foreign_key('task_parent_id_fkey', 'task', 'task', ['parent_id'], ['id'])
    if not column_exists('task', 'quarter_id'):
        op.add_column('task', sa.Column('quarter_id', sa.Integer(), nullable=True))
        # op.create_foreign_key('task_quarter_id_fkey', 'task', 'quarter', ['quarter_id'], ['id'])


def downgrade() -> None:
    if column_exists('task', 'quarter_id'):
        # op.drop_constraint('task_quarter_id_fkey', 'task', type_='foreignkey')
        op.drop_column('task', 'quarter_id')
    if column_exists('task', 'parent_id'):
        op.drop_constraint('task_parent_id_fkey', 'task', type_='foreignkey')
        op.drop_column('task', 'parent_id')
    if column_exists('task', 'reviewer_id'):
        op.drop_constraint('task_reviewer_id_fkey', 'task', type_='foreignkey')
        op.drop_column('task', 'reviewer_id')
    if column_exists('task', 'estimated_hours'):
        op.drop_column('task', 'estimated_hours')
    if column_exists('task', 'start_date'):
        op.drop_column('task', 'start_date')
