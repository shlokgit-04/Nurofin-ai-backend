"""merge_google_calendar_and_meeting_fix

Revision ID: 994c0fce80e1
Revises: 684debe30ca6, ad68f4667c9c
Create Date: 2026-07-15 21:43:38.179832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '994c0fce80e1'
down_revision: Union[str, None] = ('684debe30ca6', 'ad68f4667c9c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
