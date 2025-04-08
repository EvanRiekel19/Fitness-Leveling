"""fix workout_id column

Revision ID: fix_workout_id_column
Revises: 9acac6a0f763
Create Date: 2024-04-08 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_workout_id_column'
down_revision = '9acac6a0f763'
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
        
        # Update existing records if needed
        op.execute("""
            UPDATE exercise e
            SET workout_id = (
                SELECT w.id
                FROM workout w
                WHERE w.id = e.workout_id
                LIMIT 1
            )
            WHERE e.workout_id IS NOT NULL
        """)
        
        # Make the column non-nullable after updating existing records
        op.alter_column('exercise', 'workout_id',
                       existing_type=sa.Integer(),
                       nullable=False)


def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_exercise_workout_id', 'exercise', type_='foreignkey')
    
    # Remove the column
    op.drop_column('exercise', 'workout_id') 