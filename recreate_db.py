from app import create_app, db
from app.models.user import User
from app.models.workout import Workout
from app.models.friendship import Friendship

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Database recreated successfully!") 