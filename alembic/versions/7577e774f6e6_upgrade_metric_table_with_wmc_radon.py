"""upgrade metric table with wmc radon

Revision ID: 7577e774f6e6
Revises: c0d7844477a1
Create Date: 2023-04-20 10:36:17.631240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7577e774f6e6'
down_revision = 'c0d7844477a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('metric', sa.Column('radon_wmc_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_wmc_avg', sa.Float))


def downgrade() -> None:
    pass
