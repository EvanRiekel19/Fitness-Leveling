from app import db
from app.models.user import User
from datetime import datetime
import logging

def apply_xp_decay_to_all_users():
    """Apply XP decay to all users who haven't worked out recently."""
    try:
        users = User.query.all()
        for user in users:
            xp_lost = user.apply_xp_decay()
            if xp_lost > 0:
                logging.info(f"User {user.username} lost {xp_lost} XP due to inactivity")
    except Exception as e:
        logging.error(f"Error applying XP decay: {str(e)}")
        db.session.rollback()
    finally:
        db.session.commit() 