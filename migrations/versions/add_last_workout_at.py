"""Add last_workout_at column to User model

Revision ID: add_last_workout_at
Create Date: 2025-03-28

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_last_workout_at'
down_revision = None  # Set this to your previous migration ID if known
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('last_workout_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('user', 'last_workout_at') 