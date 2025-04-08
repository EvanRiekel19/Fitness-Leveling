from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Check if column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'exercise' 
            AND column_name = 'workout_id'
        """))
        
        if not result.fetchone():
            # Add the column if it doesn't exist
            db.session.execute(text("""
                ALTER TABLE exercise 
                ADD COLUMN workout_id INTEGER,
                ADD CONSTRAINT fk_exercise_workout_id 
                FOREIGN KEY (workout_id) 
                REFERENCES workout (id)
            """))
            db.session.commit()
            print("Successfully added workout_id column to exercise table")
        else:
            print("workout_id column already exists")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback() 