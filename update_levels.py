from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    for user in users:
        old_level = user.level
        user.update_level()
        print(f"Updated {user.username}: Level {old_level} -> {user.level} (XP: {user.xp})")
    
    db.session.commit()
    print("All user levels have been updated!") 