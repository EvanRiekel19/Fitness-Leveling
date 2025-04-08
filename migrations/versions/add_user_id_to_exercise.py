"""add user_id to exercise

Revision ID: add_user_id_to_exercise
Revises: add_type_to_exercise
Create Date: 2024-04-08 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_user_id_to_exercise'
down_revision = 'add_type_to_exercise'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('exercise')]
    
    if 'user_id' not in columns:
        # Add the column if it doesn't exist
        op.add_column('exercise', sa.Column('user_id', sa.Integer(), nullable=False))
        # Add foreign key constraint
        op.create_foreign_key(
            'fk_exercise_user_id',
            'exercise', 'user',
            ['user_id'], ['id']
        )


def downgrade():
    # Remove the foreign key constraint first
    op.drop_constraint('fk_exercise_user_id', 'exercise', type_='foreignkey')
    # Then remove the column
    op.drop_column('exercise', 'user_id') 