"""fix column types

Revision ID: fix_column_types
Revises: fix_columns
Create Date: 2024-04-07 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_column_types'
down_revision = 'fix_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Drop and recreate columns with correct types and defaults
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS total_workouts')
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS total_distance')
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS total_duration')
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS total_calories')
    
    op.execute('ALTER TABLE "user" ADD COLUMN total_workouts INTEGER NOT NULL DEFAULT 0')
    op.execute('ALTER TABLE "user" ADD COLUMN total_distance FLOAT NOT NULL DEFAULT 0')
    op.execute('ALTER TABLE "user" ADD COLUMN total_duration INTEGER NOT NULL DEFAULT 0')
    op.execute('ALTER TABLE "user" ADD COLUMN total_calories INTEGER NOT NULL DEFAULT 0')


def downgrade():
    # Remove the columns
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS total_workouts')
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS total_distance')
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS total_duration')
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS total_calories') 