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
    # Always redirect to the detailed strength form
    return redirect(url_for('workout.new_strength'))

def get_exercise_history(exercise_name, user_id):
    """Get previous workout data and PRs for a specific exercise."""
    try:
        # Get all exercises with this name for the user
        exercises = db.session.execute("""
            SELECT e.id, e.workout_id, e.name, w.date
            FROM exercise e
            JOIN workout w ON e.workout_id = w.id
            WHERE e.name = :exercise_name AND w.user_id = :user_id
            ORDER BY w.date DESC
            LIMIT 5
        """, {'exercise_name': exercise_name, 'user_id': user_id}).fetchall()
        
        if not exercises:
            return None
            
        # Get sets for each exercise
        history = []
        for ex in exercises:
            sets = db.session.execute("""
                SELECT set_number, reps, weight, notes
                FROM exercise_set
                WHERE exercise_id = :exercise_id
                ORDER BY set_number
            """, {'exercise_id': ex[0]}).fetchall()
            
            history.append({
                'date': ex[3],
                'sets': [{
                    'set_number': s[0],
                    'reps': s[1],
                    'weight': s[2],
                    'notes': s[3]
                } for s in sets]
            })
            
        # Calculate PRs
        prs = {
            'max_weight': 0,
            'max_reps': 0,
            'max_volume': 0  # weight * reps
        }
        
        for workout in history:
            for set_data in workout['sets']:
                if set_data['weight'] and set_data['reps']:
                    # Update max weight
                    if set_data['weight'] > prs['max_weight']:
                        prs['max_weight'] = set_data['weight']
                    
                    # Update max reps
                    if set_data['reps'] > prs['max_reps']:
                        prs['max_reps'] = set_data['reps']
                    
                    # Update max volume
                    volume = set_data['weight'] * set_data['reps']
                    if volume > prs['max_volume']:
                        prs['max_volume'] = volume
        
        return {
            'history': history,
            'prs': prs,
            'last_workout': history[0]['date'] if history else None
        }
    except Exception as e:
        print(f"Error getting exercise history: {e}")
        return None

@bp.route('/workouts/new/strength', methods=['GET', 'POST'])
@login_required
def new_strength():
    if request.method == 'POST':
        try:
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

            # Get the subtype
            subtype = request.form.get('subtype', 'strength_full')
            print(f"DEBUG STRENGTH: Using subtype: {subtype}")
            
            # Create workout
            workout = Workout(
                user_id=current_user.id,
                type='strength',
                name=request.form.get('name', ''),
                duration=safe_int(request.form.get('duration')),
                intensity=safe_int(request.form.get('intensity'), 5),
                notes=request.form.get('notes', '')
            )
            
            # Add subtype if the column exists
            try:
                if hasattr(workout, 'subtype'):
                    workout.subtype = subtype
                    print(f"DEBUG STRENGTH: Set workout subtype to: {subtype}")
            except Exception as e:
                print(f"DEBUG STRENGTH: Failed to set subtype: {e}")
            
            # Validate required fields
            if not workout.name:
                flash('Workout name is required', 'error')
                return render_template('workout/new_strength.html', exercise_options=get_exercise_options())
            
            if workout.duration <= 0:
                flash('Duration must be greater than 0', 'error')
                return render_template('workout/new_strength.html', exercise_options=get_exercise_options())
            
            # Process exercises data from form
            try:
                exercises_data = request.form.get('exercises_data', '[]')
                print(f"DEBUG STRENGTH: Exercises data length: {len(exercises_data)}")
                
                exercises_data = json.loads(exercises_data)
                print(f"DEBUG STRENGTH: Found {len(exercises_data)} exercises")
            except json.JSONDecodeError as e:
                print(f"DEBUG STRENGTH: JSON decode error: {e}")
                exercises_data = []
            
            # Save workout to get an ID
            db.session.add(workout)
            db.session.flush()
            print(f"DEBUG STRENGTH: Created workout with ID: {workout.id}")
            
            # Process and add exercises
            for i, exercise_data in enumerate(exercises_data):
                try:
                    exercise_name = exercise_data.get('name', '').strip()
                    if not exercise_name:
                        print(f"DEBUG STRENGTH: Skipping exercise {i+1} - no name")
                        continue
                        
                    # Create the exercise
                    exercise = Exercise(
                        workout_id=workout.id,
                        name=exercise_name
                    )
                    db.session.add(exercise)
                    db.session.flush()
                    print(f"DEBUG STRENGTH: Added exercise: {exercise_name} with ID: {exercise.id}")
                    
                    # Add sets for this exercise
                    sets_data = exercise_data.get('sets', [])
                    print(f"DEBUG STRENGTH: Processing {len(sets_data)} sets for exercise '{exercise_name}'")
                    
                    for set_idx, set_data in enumerate(sets_data, 1):
                        exercise_set = ExerciseSet(
                            exercise_id=exercise.id,
                            set_number=set_idx,
                            reps=safe_int(set_data.get('reps')),
                            weight=safe_float(set_data.get('weight')),
                            notes=set_data.get('notes', '')
                        )
                        db.session.add(exercise_set)
                        print(f"DEBUG STRENGTH: Added set {set_idx} with {safe_int(set_data.get('reps'))} reps at {safe_float(set_data.get('weight'))} kg")
                except Exception as e:
                    print(f"DEBUG STRENGTH: Error adding exercise {i+1}: {e}")
            
            # Calculate XP and update user
            try:
                xp_earned = workout.calculate_xp()
                print(f"DEBUG STRENGTH: Calculated XP: {xp_earned}")
                
                current_user.add_xp(xp_earned)
                print(f"DEBUG STRENGTH: Added XP to user")
            except Exception as e:
                print(f"DEBUG STRENGTH: XP calculation/assignment error: {e}")
                xp_earned = 50  # Fallback
            
            db.session.commit()
            print(f"DEBUG STRENGTH: Successfully committed workout with {len(exercises_data)} exercises")
            
            flash(f'Strength workout logged! Earned {xp_earned} XP', 'success')
            return redirect(url_for('workout.index'))
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"ERROR in strength workout submission: {e}")
            print(traceback.format_exc())
            flash(f'Error logging workout: {str(e)}', 'error')
            return render_template('workout/new_strength.html', exercise_options=get_exercise_options())
    
    # For GET requests, get exercise history for all exercises
    exercise_history = {}
    for exercise_name in get_exercise_options():
        history = get_exercise_history(exercise_name, current_user.id)
        if history:
            exercise_history[exercise_name] = history
    
    return render_template('workout/new_strength.html', 
                         exercise_options=get_exercise_options(),
                         exercise_history=exercise_history)

# Helper function to get exercise options
def get_exercise_options():
    return [
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

# Get workout details for a specific workout
@bp.route('/workouts/<int:workout_id>')
@login_required
def view(workout_id):
    # Get the workout
    try:
        workout = Workout.query.get_or_404(workout_id)
        
        # Security check
        if workout.user_id != current_user.id:
            flash('You do not have permission to view this workout', 'error')
            return redirect(url_for('workout.index'))
        
        # Variable to store all exercises and their sets
        exercises = []
        
        # Only get exercises for strength workouts
        if workout.type == 'strength':
            # Get all exercises for this workout using raw SQL with proper parameters
            try:
                # Get all exercises
                exercise_sql = """
                    SELECT id, workout_id, name 
                    FROM exercise 
                    WHERE workout_id = :workout_id
                """
                exercises_result = db.session.execute(exercise_sql, {"workout_id": workout_id})
                exercise_rows = exercises_result.fetchall()
                
                print(f"Found {len(exercise_rows)} exercises for workout {workout_id}")
                
                # Process each exercise
                for ex_row in exercise_rows:
                    ex_id = ex_row[0]
                    ex_name = ex_row[2]
                    
                    print(f"Processing exercise {ex_id}: {ex_name}")
                    
                    # Get all sets for this exercise using SQL
                    sets_sql = """
                        SELECT id, exercise_id, set_number, reps, weight, notes
                        FROM exercise_set
                        WHERE exercise_id = :exercise_id
                        ORDER BY set_number
                    """
                    sets_result = db.session.execute(sets_sql, {"exercise_id": ex_id})
                    set_rows = sets_result.fetchall()
                    
                    print(f"Found {len(set_rows)} sets for exercise {ex_name}")
                    
                    # Create exercise object
                    exercise = {
                        'model': {
                            'id': ex_id,
                            'name': ex_name
                        },
                        'ordered_sets': []
                    }
                    
                    # Add all sets to this exercise
                    for set_row in set_rows:
                        # Create a set dictionary
                        exercise_set = {
                            'id': set_row[0],
                            'set_number': set_row[2],
                            'reps': set_row[3],
                            'weight': set_row[4],
                            'notes': set_row[5] if set_row[5] else ''
                        }
                        exercise['ordered_sets'].append(exercise_set)
                        print(f"  Added set {exercise_set['set_number']}: {exercise_set['reps']} reps at {exercise_set['weight']}kg")
                    
                    # Add this exercise to our list
                    exercises.append(exercise)
            
            except Exception as e:
                import traceback
                print(f"Error fetching exercises: {e}")
                print(traceback.format_exc())
                # Don't fail completely - continue with empty exercises list
        
        # Render the template with all our data
        return render_template('workout/view.html', workout=workout, exercises=exercises)
    
    except Exception as e:
        import traceback
        print(f"Error loading workout {workout_id}: {e}")
        print(traceback.format_exc())
        flash('Error loading workout details. Please try again.', 'error')
        return redirect(url_for('workout.index'))