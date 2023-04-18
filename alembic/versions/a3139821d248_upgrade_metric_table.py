"""upgrade metric table

Revision ID: a3139821d248
Revises: 
Create Date: 2023-04-08 10:52:29.701997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3139821d248'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PDepend metrics
    op.add_column('metric', sa.Column('pdepend_cbo', sa.Float))
    op.add_column('metric', sa.Column('pdepend_fan_out', sa.Float))
    op.add_column('metric', sa.Column('pdepend_dit', sa.Float))
    op.add_column('metric', sa.Column('pdepend_nof', sa.Float))
    op.add_column('metric', sa.Column('pdepend_noc', sa.Float))
    op.add_column('metric', sa.Column('pdepend_nom', sa.Float))
    op.add_column('metric', sa.Column('pdepend_nopm', sa.Float))
    op.add_column('metric', sa.Column('pdepend_vars', sa.Float))
    op.add_column('metric', sa.Column('pdepend_wmc', sa.Float))
    op.add_column('metric', sa.Column('pdepend_calls', sa.Float))
    op.add_column('metric', sa.Column('pdepend_nocc', sa.Float))
    op.add_column('metric', sa.Column('pdepend_noom', sa.Float))
    op.add_column('metric', sa.Column('pdepend_noi', sa.Float))
    op.add_column('metric', sa.Column('pdepend_nop', sa.Float))

    # radon raw metrics
    op.add_column('metric', sa.Column('radon_cc_total', sa.Float))
    op.add_column('metric', sa.Column('radon_cc_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_loc_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_loc_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_lloc_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_lloc_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_sloc_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_sloc_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_comments_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_comments_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_docstring_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_docstring_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_blank_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_blank_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_single_comments_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_single_comments_avg', sa.Float))

    # radon calculated metrics
    op.add_column('metric', sa.Column('radon_noc_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_noc_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_nom_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_nom_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_nof_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_nof_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_class_loc_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_class_loc_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_method_loc_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_method_loc_avg', sa.Float))
    op.add_column('metric', sa.Column('radon_func_loc_total', sa.Integer))
    op.add_column('metric', sa.Column('radon_func_loc_avg', sa.Float))

def downgrade() -> None:
    pass
