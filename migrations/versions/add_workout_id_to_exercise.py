"""add workout_id to exercise

Revision ID: add_workout_id_to_exercise
Revises: recreate_tables
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_workout_id_to_exercise'
down_revision = 'recreate_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Add workout_id column to exercise table
    op.add_column('exercise', sa.Column('workout_id', sa.Integer(), nullable=False))
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_exercise_workout_id',
        'exercise', 'workout',
        ['workout_id'], ['id']
    )

def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_exercise_workout_id', 'exercise', type_='foreignkey')
    # Remove workout_id column
    op.drop_column('exercise', 'workout_id') 