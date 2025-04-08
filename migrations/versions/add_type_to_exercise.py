"""add type to exercise

Revision ID: add_type_to_exercise
Revises: add_workout_id_final
Create Date: 2024-04-08 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_type_to_exercise'
down_revision = 'add_workout_id_final'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('exercise')]
    
    if 'type' not in columns:
        # Add the column if it doesn't exist
        op.add_column('exercise', sa.Column('type', sa.String(50), nullable=False, server_default='strength'))


def downgrade():
    # Remove the column
    op.drop_column('exercise', 'type') 