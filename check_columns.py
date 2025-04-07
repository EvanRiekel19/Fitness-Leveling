from app import create_app, db
from sqlalchemy import text

def check_columns():
    app = create_app()
    with app.app_context():
        # SQL command to list all columns in the user table
        sql_command = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'user'
        ORDER BY ordinal_position;
        """
        
        try:
            # Execute the SQL command
            result = db.session.execute(text(sql_command))
            print("\nColumns in the user table:")
            print("---------------------------")
            for row in result:
                print(f"Column: {row[0]}, Type: {row[1]}, Nullable: {row[2]}")
        except Exception as e:
            print(f"Error occurred: {str(e)}")

if __name__ == '__main__':
    check_columns() 