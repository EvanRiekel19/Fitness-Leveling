from app import create_app, db
from app.models.workout import Workout
from app.models.user import User

app = create_app()
with app.app_context():
    # Clear all workouts
    Workout.query.delete()
    # Reset user XP
    for user in User.query.all():
        user.xp = 0
        user.level = 1
    db.session.commit()
    print("All workouts cleared and user XP reset") 