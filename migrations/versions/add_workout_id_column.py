"""add workout_id column

Revision ID: add_workout_id_column
Revises: add_all_missing_columns
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_workout_id_column'
down_revision = 'add_all_missing_columns'
branch_labels = None
depends_on = None

def upgrade():
    # Check if the column exists first
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('exercise')]
    
    if 'workout_id' not in columns:
        op.add_column('exercise', sa.Column('workout_id', sa.Integer(), nullable=True))
        # Add foreign key constraint
        op.create_foreign_key(
            'fk_exercise_workout_id',
            'exercise', 'workout',
            ['workout_id'], ['id']
        )

def downgrade():
    # Remove foreign key constraint first
    op.drop_constraint('fk_exercise_workout_id', 'exercise', type_='foreignkey')
    # Then drop the column
    op.drop_column('exercise', 'workout_id') 