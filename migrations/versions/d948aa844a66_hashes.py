"""hashes

Revision ID: d948aa844a66
Revises: d83228929a2a
Create Date: 2023-08-06 15:56:22.422124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd948aa844a66'
down_revision: Union[str, None] = 'd83228929a2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('image_hashes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dt_added', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute("ALTER TABLE image_hashes ADD COLUMN hash ARRAY NOT NULL")
    op.execute("CREATE UNIQUE INDEX unique_image_hashes_hash ON image_hashes(hash)")


def downgrade() -> None:
    op.drop_table('image_hashes')
