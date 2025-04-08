from app import create_app, db
from app.models.exercise_set import ExerciseSet

app = create_app()
with app.app_context():
    try:
        # Check if the column exists
        result = db.session.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'exercise_set' 
            AND column_name = 'set_number'
        """).fetchone()
        
        if not result:
            # Add the column if it doesn't exist
            db.session.execute("""
                ALTER TABLE exercise_set 
                ADD COLUMN set_number INTEGER NOT NULL DEFAULT 1
            """)
            db.session.commit()
            print("Successfully added set_number column to exercise_set table")
        else:
            print("set_number column already exists in exercise_set table")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error adding set_number column: {e}") 