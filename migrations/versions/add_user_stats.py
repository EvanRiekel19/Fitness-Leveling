"""add user stats

Revision ID: add_user_stats
Revises: recreate_tables
Create Date: 2024-04-03 04:44:27.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_stats'
down_revision = 'recreate_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns if they don't exist
    op.add_column('user', sa.Column('total_workouts', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('total_distance', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('total_duration', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('total_calories', sa.Integer(), nullable=True))
    
    # Set default values for new columns
    op.execute('UPDATE "user" SET total_workouts = 0 WHERE total_workouts IS NULL')
    op.execute('UPDATE "user" SET total_distance = 0 WHERE total_distance IS NULL')
    op.execute('UPDATE "user" SET total_duration = 0 WHERE total_duration IS NULL')
    op.execute('UPDATE "user" SET total_calories = 0 WHERE total_calories IS NULL')
    
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