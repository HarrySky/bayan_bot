"""initial

Revision ID: d83228929a2a
Revises:
Create Date: 2023-08-06 12:35:28.578757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd83228929a2a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'state',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dt_added', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('offset', sa.BigInteger(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute("INSERT INTO state (id) VALUES (1)")


def downgrade() -> None:
    op.drop_table('state')
