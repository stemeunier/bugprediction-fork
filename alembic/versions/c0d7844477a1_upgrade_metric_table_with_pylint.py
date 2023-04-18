"""upgrade metric table with pylint

Revision ID: c0d7844477a1
Revises: a3139821d248
Create Date: 2023-04-12 14:14:24.327117

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0d7844477a1'
down_revision = 'a3139821d248'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # pylint raw metrics
    op.add_column('metric', sa.Column('pylint_cbo', sa.Float))
    op.add_column('metric', sa.Column('pylint_fan_out', sa.Float))
    op.add_column('metric', sa.Column('pylint_dit', sa.Integer))
    op.add_column('metric', sa.Column('pylint_noc', sa.Integer))
    op.add_column('metric', sa.Column('pylint_nom', sa.Integer))
    op.add_column('metric', sa.Column('pylint_nof', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_field', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_returns', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_loops', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_comparisons', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_try_except', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_str_literals', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_numbers', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_math_op', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_variable', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_inner_cls_and_lambda', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_docstring', sa.Integer))
    op.add_column('metric', sa.Column('pylint_num_import', sa.Integer))
    op.add_column('metric', sa.Column('pylint_lcc', sa.Float))

def downgrade() -> None:
    pass
