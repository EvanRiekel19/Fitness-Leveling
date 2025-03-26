from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.workout import Workout
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('main/landing.html')
    
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