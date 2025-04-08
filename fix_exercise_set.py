from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Check if column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'exercise_set' 
            AND column_name = 'set_number'
        """)).fetchone()
        
        if not result:
            # Add the column if it doesn't exist
            db.session.execute(text("""
                ALTER TABLE exercise_set 
                ADD COLUMN set_number INTEGER NOT NULL DEFAULT 1
            """))
            db.session.commit()
            print("Successfully added set_number column to exercise_set table")
        else:
            print("set_number column already exists in exercise_set table")
            
        # Verify the column was added
        columns = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'exercise_set'
            ORDER BY ordinal_position
        """)).fetchall()
        
        print("\nCurrent table structure:")
        for col in columns:
            print(f"Column: {col[0]}, Type: {col[1]}, Nullable: {col[2]}, Default: {col[3]}")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}") 