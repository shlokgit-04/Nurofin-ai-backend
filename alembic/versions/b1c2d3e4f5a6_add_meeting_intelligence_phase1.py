"""add meeting intelligence phase 1 fields

Revision ID: b1c2d3e4f5a6
Revises: 9a249f678469
Create Date: 2026-07-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = '9a249f678469'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('meeting', sa.Column('transcript', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('ai_summary', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('minutes_of_meeting', sa.Text(), nullable=True))
    op.add_column('meeting', sa.Column('analysis_status', sa.String(), nullable=True))
    op.add_column('meeting', sa.Column('metadata_json', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('meeting', 'metadata_json')
    op.drop_column('meeting', 'analysis_status')
    op.drop_column('meeting', 'minutes_of_meeting')
    op.drop_column('meeting', 'ai_summary')
    op.drop_column('meeting', 'transcript')
