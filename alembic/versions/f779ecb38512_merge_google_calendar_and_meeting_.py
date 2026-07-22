"""merge_google_calendar_and_meeting_intelligence

Revision ID: f779ecb38512
Revises: 994c0fce80e1, b1c2d3e4f5a6
Create Date: 2026-07-22 10:48:56.046471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f779ecb38512'
down_revision: Union[str, None] = ('994c0fce80e1', 'b1c2d3e4f5a6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
