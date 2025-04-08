"""add workout_id final

Revision ID: add_workout_id_final
Revises: recreate_tables
Create Date: 2024-04-08 02:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_workout_id_final'
down_revision = 'recreate_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('exercise')]
    
    if 'workout_id' not in columns:
        # Add the column if it doesn't exist
        op.add_column('exercise', sa.Column('workout_id', sa.Integer(), nullable=True))
        
        # Add foreign key constraint
        op.create_foreign_key(
            'fk_exercise_workout_id',
            'exercise', 'workout',
            ['workout_id'], ['id']
        )
        
        # Make the column non-nullable
        op.alter_column('exercise', 'workout_id',
                       existing_type=sa.Integer(),
                       nullable=False)


def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_exercise_workout_id', 'exercise', type_='foreignkey')
    
    # Remove the column
    op.drop_column('exercise', 'workout_id') 