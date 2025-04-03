"""merge add_last_workout_at and add_user_stats

Revision ID: 20672be512d4
Revises: add_last_workout_at, add_user_stats
Create Date: 2025-04-03 00:54:52.287928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20672be512d4'
down_revision = ('add_last_workout_at', 'add_user_stats')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
