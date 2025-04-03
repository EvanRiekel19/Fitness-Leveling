"""Add last_workout_at to User model

Revision ID: add_last_workout_at
Revises: initial_schema
Create Date: 2024-04-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_last_workout_at'
down_revision = 'initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('last_workout_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('user', 'last_workout_at') 