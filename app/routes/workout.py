from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.workout import Workout
from app.models.exercise import Exercise, ExerciseSet
from app import db
import json

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

# New route for detailed strength workout entry
@bp.route('/workouts/new/strength', methods=['GET', 'POST'])
@login_required
def new_strength():
    if request.method == 'POST':
        # Helper functions
        def safe_int(value, default=0):
            try:
                return int(value) if value else default
            except (ValueError, TypeError):
                return default

        def safe_float(value, default=0.0):
            try:
                return float(value) if value else default
            except (ValueError, TypeError):
                return default

        # Create workout
        workout = Workout(
            user_id=current_user.id,
            type='strength',
            name=request.form.get('name', ''),
            duration=safe_int(request.form.get('duration')),
            intensity=safe_int(request.form.get('intensity'), 5),
            notes=request.form.get('notes', '')
        )
        
        # Validate required fields
        if not workout.name:
            flash('Workout name is required', 'error')
            return render_template('workout/new_strength.html')
        
        if workout.duration <= 0:
            flash('Duration must be greater than 0', 'error')
            return render_template('workout/new_strength.html')
        
        # Process exercises data from form
        exercises_data = request.form.get('exercises_data', '[]')
        try:
            exercises_data = json.loads(exercises_data)
        except json.JSONDecodeError:
            exercises_data = []
        
        # Save workout to get an ID
        db.session.add(workout)
        db.session.flush()
        
        # Process and add exercises
        for exercise_data in exercises_data:
            exercise_name = exercise_data.get('name', '').strip()
            if not exercise_name:
                continue
                
            exercise = Exercise(
                workout_id=workout.id,
                name=exercise_name
            )
            db.session.add(exercise)
            db.session.flush()
            
            # Add sets for this exercise
            sets_data = exercise_data.get('sets', [])
            for set_idx, set_data in enumerate(sets_data, 1):
                exercise_set = ExerciseSet(
                    exercise_id=exercise.id,
                    set_number=set_idx,
                    reps=safe_int(set_data.get('reps')),
                    weight=safe_float(set_data.get('weight')),
                    notes=set_data.get('notes', '')
                )
                db.session.add(exercise_set)
        
        # Calculate XP and update user
        xp_earned = workout.calculate_xp()
        current_user.add_xp(xp_earned)
        
        db.session.commit()
        
        flash(f'Strength workout logged! Earned {xp_earned} XP', 'success')
        return redirect(url_for('workout.index'))
    
    # Define a list of common exercise names
    exercise_options = [
        # Chest
        "Bench Press", "Incline Bench Press", "Decline Bench Press", "Dumbbell Press", 
        "Incline Dumbbell Press", "Chest Fly", "Cable Fly", "Push-up", "Dips",
        
        # Back
        "Pull-up", "Lat Pulldown", "Seated Row", "Bent Over Row", "T-Bar Row", 
        "Face Pull", "Deadlift", "Back Extension", "Good Morning",
        
        # Shoulders
        "Overhead Press", "Military Press", "Dumbbell Shoulder Press", "Lateral Raise", 
        "Front Raise", "Rear Delt Fly", "Shrug", "Upright Row",
        
        # Arms
        "Bicep Curl", "Hammer Curl", "Preacher Curl", "Concentration Curl", 
        "Tricep Extension", "Tricep Pushdown", "Skull Crusher", "Close-Grip Bench Press",
        
        # Legs
        "Squat", "Leg Press", "Leg Extension", "Leg Curl", "Lunge", "Romanian Deadlift", 
        "Calf Raise", "Hip Thrust", "Glute Bridge", "Hack Squat",
        
        # Core
        "Crunch", "Sit-up", "Plank", "Russian Twist", "Leg Raise", "Ab Rollout",
        "Hanging Leg Raise", "Cable Crunch", "Side Plank"
    ]
    
    return render_template('workout/new_strength.html', exercise_options=exercise_options)

# Get workout details for a specific workout
@bp.route('/workouts/<int:workout_id>')
@login_required
def view(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    
    # Ensure the user owns this workout
    if workout.user_id != current_user.id:
        flash('You do not have permission to view this workout', 'error')
        return redirect(url_for('workout.index'))
    
    return render_template('workout/view.html', workout=workout) 