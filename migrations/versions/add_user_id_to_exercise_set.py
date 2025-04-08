"""add user_id to exercise_set

Revision ID: add_user_id_to_exercise_set
Revises: add_set_number_to_exercise_set
Create Date: 2024-04-08 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_user_id_to_exercise_set'
down_revision = 'add_set_number_to_exercise_set'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('exercise_set')]
    
    if 'user_id' not in columns:
        # Add the column if it doesn't exist
        op.add_column('exercise_set', sa.Column('user_id', sa.Integer(), nullable=False))
        # Add foreign key constraint
        op.create_foreign_key(
            'fk_exercise_set_user_id',
            'exercise_set', 'user',
            ['user_id'], ['id']
        )


def downgrade():
    # Remove the foreign key constraint first
    op.drop_constraint('fk_exercise_set_user_id', 'exercise_set', type_='foreignkey')
    # Then remove the column
    op.drop_column('exercise_set', 'user_id') 