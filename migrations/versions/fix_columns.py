"""fix columns

Revision ID: fix_columns
Revises: 3215aff09b97
Create Date: 2024-04-07 21:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_columns'
down_revision = '3215aff09b97'
branch_labels = None
depends_on = None


def upgrade():
    # Create the columns if they don't exist
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('user')]
    
    if 'total_workouts' not in columns:
        op.add_column('user', sa.Column('total_workouts', sa.Integer(), server_default='0', nullable=False))
    if 'total_distance' not in columns:
        op.add_column('user', sa.Column('total_distance', sa.Float(), server_default='0', nullable=False))
    if 'total_duration' not in columns:
        op.add_column('user', sa.Column('total_duration', sa.Integer(), server_default='0', nullable=False))
    if 'total_calories' not in columns:
        op.add_column('user', sa.Column('total_calories', sa.Integer(), server_default='0', nullable=False))


def downgrade():
    # Remove the columns
    op.drop_column('user', 'total_workouts')
    op.drop_column('user', 'total_distance')
    op.drop_column('user', 'total_duration')
    op.drop_column('user', 'total_calories') 