"""merge workout_id migrations

Revision ID: a2dbf47f8cc1
Revises: add_workout_id_to_exercise, fix_exercise_table
Create Date: 2025-04-07 18:02:41.236830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2dbf47f8cc1'
down_revision = ('add_workout_id_to_exercise', 'fix_exercise_table')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
