"""Merge multiple heads

Revision ID: 104b8f0b1a70
Revises: b3c4d5e6f7a8, c1d2e3f4a5b6
Create Date: 2026-07-23 19:37:15.892908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '104b8f0b1a70'
down_revision: Union[str, None] = ('b3c4d5e6f7a8', 'c1d2e3f4a5b6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
