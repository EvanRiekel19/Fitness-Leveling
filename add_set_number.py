from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Add the column
        db.session.execute(text("""
            ALTER TABLE exercise_set 
            ADD COLUMN IF NOT EXISTS set_number INTEGER NOT NULL DEFAULT 1
        """))
        db.session.commit()
        print("Successfully added set_number column to exercise_set table")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}") 