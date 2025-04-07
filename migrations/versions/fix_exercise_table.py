"""fix exercise table

Revision ID: fix_exercise_table
Revises: add_all_missing_columns
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_exercise_table'
down_revision = 'add_all_missing_columns'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the existing exercise table
    op.drop_table('exercise')
    
    # Create the exercise table with the correct columns
    op.create_table('exercise',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workout_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['workout_id'], ['workout.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop the exercise table
    op.drop_table('exercise')
    
    # Recreate the original exercise table (if needed)
    op.create_table('exercise',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    ) 