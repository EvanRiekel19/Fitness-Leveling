"""merge multiple heads

Revision ID: 3215aff09b97
Revises: 20672be512d4, add_workout_stats
Create Date: 2025-04-03 01:00:46.959057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3215aff09b97'
down_revision = ('20672be512d4', 'add_workout_stats')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
