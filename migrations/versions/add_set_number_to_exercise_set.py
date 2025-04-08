"""add set_number to exercise_set

Revision ID: add_set_number_to_exercise_set
Revises: add_user_id_to_exercise
Create Date: 2024-04-08 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_set_number_to_exercise_set'
down_revision = 'add_user_id_to_exercise'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('exercise_set')]
    
    if 'set_number' not in columns:
        # Add the column if it doesn't exist
        op.add_column('exercise_set', sa.Column('set_number', sa.Integer(), nullable=False, server_default='1'))


def downgrade():
    # Remove the column
    op.drop_column('exercise_set', 'set_number') 