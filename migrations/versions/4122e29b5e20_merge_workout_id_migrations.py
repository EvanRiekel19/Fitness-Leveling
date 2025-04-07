"""merge workout_id migrations

Revision ID: 4122e29b5e20
Revises: a2dbf47f8cc1, add_workout_id_column
Create Date: 2025-04-07 18:12:41.970098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4122e29b5e20'
down_revision = ('a2dbf47f8cc1', 'add_workout_id_column')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
