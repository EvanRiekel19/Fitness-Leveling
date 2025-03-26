from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.workout import Workout
from app import db

bp = Blueprint('workout', __name__)

@bp.route('/workouts')
@login_required
def index():
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.created_at.desc()).all()
    return render_template('workout/index.html', workouts=workouts)

@bp.route('/workouts/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        # Helper function to safely convert form values to integers
        def safe_int(value, default=0):
            try:
                return int(value) if value else default
            except (ValueError, TypeError):
                return default

        # Helper function to safely convert form values to floats
        def safe_float(value, default=0.0):
            try:
                return float(value) if value else default
            except (ValueError, TypeError):
                return default

        workout = Workout(
            user_id=current_user.id,
            type=request.form.get('type', 'cardio'),
            name=request.form.get('name', ''),
            duration=safe_int(request.form.get('duration')),
            intensity=safe_int(request.form.get('intensity'), 5),
            sets=safe_int(request.form.get('sets')),
            reps=safe_int(request.form.get('reps')),
            distance=safe_float(request.form.get('distance')),
            notes=request.form.get('notes', '')
        )
        
        # Validate required fields
        if not workout.name:
            flash('Workout name is required', 'error')
            return render_template('workout/new.html')
        
        if workout.duration <= 0:
            flash('Duration must be greater than 0', 'error')
            return render_template('workout/new.html')
        
        xp_earned = workout.calculate_xp()
        current_user.add_xp(xp_earned)
        
        db.session.add(workout)
        db.session.commit()
        
        flash(f'Workout logged! Earned {xp_earned} XP', 'success')
        return redirect(url_for('workout.index'))
    
    return render_template('workout/new.html') 