"""Merge multiple heads

Revision ID: f49c8c168d4d
Revises: 684debe30ca6, ad68f4667c9c
Create Date: 2026-07-16 10:22:43.815716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f49c8c168d4d'
down_revision: Union[str, None] = ('684debe30ca6', 'ad68f4667c9c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
