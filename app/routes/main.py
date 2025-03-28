from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from app.models.workout import Workout
from datetime import datetime, timedelta
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('main/landing.html')
    
    # Check and apply XP decay
    xp_to_lose, days_until_decay = current_user.calculate_xp_decay()
    if xp_to_lose > 0:
        xp_lost = current_user.apply_xp_decay()
        if xp_lost > 0:
            flash(f'You lost {xp_lost} XP due to inactivity! Work out to stop losing XP.', 'error')
            db.session.commit()
    
    # Get recent workouts
    recent_workouts = Workout.query.filter_by(user_id=current_user.id)\
        .order_by(Workout.created_at.desc())\
        .limit(5)\
        .all()
    
    # Get weekly stats
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.created_at >= week_ago
    ).all()
    
    total_xp_this_week = sum(workout.xp_earned for workout in weekly_workouts)
    workout_count_this_week = len(weekly_workouts)
    
    return render_template('main/dashboard.html',
                         recent_workouts=recent_workouts,
                         total_xp_this_week=total_xp_this_week,
                         workout_count_this_week=workout_count_this_week) 