"""create comment table

Revision ID: b50a065f412c
Revises: 7577e774f6e6
Create Date: 2023-05-10 15:12:38.657597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b50a065f412c'
down_revision = '7577e774f6e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'comment',
        sa.Column('comment_id', sa.Integer, primary_key=True),
        sa.Column('project_name', sa.String(50), sa.ForeignKey('project.name'), nullable=False),
        sa.Column('user_id', sa.String),
        sa.Column('timestamp', sa.String),
        sa.Column('feature_url', sa.String),
        sa.Column('rating', sa.Integer),
        sa.Column('comment', sa.String),
    )

def downgrade() -> None:
    op.drop_table('comment')
