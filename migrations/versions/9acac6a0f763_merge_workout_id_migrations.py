"""merge workout_id migrations

Revision ID: 9acac6a0f763
Revises: 4122e29b5e20, add_workout_id_to_exercise_safely
Create Date: 2025-04-07 22:19:32.947492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9acac6a0f763'
down_revision = ('4122e29b5e20', 'add_workout_id_to_exercise_safely')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
