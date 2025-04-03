"""Add workout stats columns

Revision ID: add_workout_stats
Revises: recreate_tables
Create Date: 2024-04-03 04:53:09.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_workout_stats'
down_revision = 'recreate_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to user table
    op.add_column('user', sa.Column('total_workouts', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('total_distance', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('total_duration', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('total_calories', sa.Float(), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE \"user\" SET total_workouts = 0 WHERE total_workouts IS NULL")
    op.execute("UPDATE \"user\" SET total_distance = 0.0 WHERE total_distance IS NULL")
    op.execute("UPDATE \"user\" SET total_duration = 0.0 WHERE total_duration IS NULL")
    op.execute("UPDATE \"user\" SET total_calories = 0.0 WHERE total_calories IS NULL")
    
    # Make columns non-nullable after setting defaults
    op.alter_column('user', 'total_workouts', nullable=False)
    op.alter_column('user', 'total_distance', nullable=False)
    op.alter_column('user', 'total_duration', nullable=False)
    op.alter_column('user', 'total_calories', nullable=False)


def downgrade():
    # Remove the columns
    op.drop_column('user', 'total_workouts')
    op.drop_column('user', 'total_distance')
    op.drop_column('user', 'total_duration')
    op.drop_column('user', 'total_calories') 