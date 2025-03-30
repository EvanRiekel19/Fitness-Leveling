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
        try:
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

            # Get workout type and determine the main category
            workout_type = request.form.get('type', 'cardio_other')
            print(f"DEBUG: Received workout type: {workout_type}")
            
            main_type = workout_type.split('_')[0] if '_' in workout_type else workout_type
            print(f"DEBUG: Extracted main type: {main_type}")
            
            # Create workout instance
            workout = Workout(
                user_id=current_user.id,
                type=main_type,  # Store the main type (cardio, strength, flexibility)
                name=request.form.get('name', ''),
                duration=safe_int(request.form.get('duration')),
                intensity=safe_int(request.form.get('intensity'), 5),
                sets=safe_int(request.form.get('sets')),
                reps=safe_int(request.form.get('reps')),
                distance=safe_float(request.form.get('distance')),
                notes=request.form.get('notes', '')
            )
            
            # Add subtype if the column exists
            try:
                if hasattr(workout, 'subtype'):
                    workout.subtype = workout_type
                    print(f"DEBUG: Set workout subtype to: {workout_type}")
            except Exception as e:
                print(f"DEBUG: Failed to set subtype: {e}")
            
            # Validate required fields
            if not workout.name:
                flash('Workout name is required', 'error')
                return render_template('workout/new.html')
            
            if workout.duration <= 0:
                flash('Duration must be greater than 0', 'error')
                return render_template('workout/new.html')
            
            # Calculate XP
            try:
                xp_earned = workout.calculate_xp()
                print(f"DEBUG: Calculated XP: {xp_earned}")
                
                # Add the XP to the user
                current_user.add_xp(xp_earned)
                print(f"DEBUG: Added XP to user")
            except Exception as e:
                print(f"DEBUG: XP calculation/assignment error: {e}")
                xp_earned = 50  # Fallback
            
            # Save to database
            db.session.add(workout)
            db.session.commit()
            print(f"DEBUG: Workout saved successfully with ID: {workout.id}")
            
            flash(f'Workout logged! Earned {xp_earned} XP', 'success')
            return redirect(url_for('workout.index'))
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"ERROR in workout submission: {e}")
            print(traceback.format_exc())
            flash(f'Error logging workout: {str(e)}', 'error')
            return render_template('workout/new.html')
    
    return render_template('workout/new.html')

# New route for detailed strength workout entry
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
    
    return render_template('workout/new_strength.html', exercise_options=get_exercise_options())

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
    # Simple try block for the entire function
    try:
        # Simple query for the workout
        workout = Workout.query.get_or_404(workout_id)
        
        # Security check
        if workout.user_id != current_user.id:
            flash('You do not have permission to view this workout', 'error')
            return redirect(url_for('workout.index'))
        
        # Get exercises - simpler approach
        exercises = []
        
        # Only try to get exercises if this is a strength workout
        if workout.type == 'strength':
            try:
                # Log for debugging
                print(f"DEBUG: Retrieving exercises for workout {workout_id}")
                
                # Get all exercises using direct SQL (better reliability)
                exercise_query = "SELECT id, workout_id, name FROM exercise WHERE workout_id = :workout_id"
                exercise_rows = db.session.execute(exercise_query, {'workout_id': workout_id}).fetchall()
                print(f"DEBUG: Found {len(exercise_rows)} exercises using SQL")
                
                # Process each exercise
                for exercise_row in exercise_rows:
                    exercise_id = exercise_row[0]
                    exercise_name = exercise_row[2]
                    
                    print(f"DEBUG: Processing exercise: {exercise_id} - {exercise_name}")
                    
                    # Create a basic exercise object
                    exercise = Exercise(
                        id=exercise_id,
                        workout_id=workout_id,
                        name=exercise_name
                    )
                    
                    # Get all sets for this exercise using direct SQL
                    set_query = """
                        SELECT id, exercise_id, set_number, reps, weight, notes 
                        FROM exercise_set 
                        WHERE exercise_id = :exercise_id 
                        ORDER BY set_number
                    """
                    set_rows = db.session.execute(set_query, {'exercise_id': exercise_id}).fetchall()
                    print(f"DEBUG: Found {len(set_rows)} sets for exercise {exercise_name}")
                    
                    # Map raw SQL rows to ExerciseSet objects
                    sets = []
                    for set_row in set_rows:
                        # Create exercise set objects directly from SQL data
                        set_obj = ExerciseSet(
                            id=set_row[0],
                            exercise_id=set_row[1],
                            set_number=set_row[2], 
                            reps=set_row[3],
                            weight=set_row[4],
                            notes=set_row[5] if len(set_row) > 5 and set_row[5] is not None else ""
                        )
                        sets.append(set_obj)
                        print(f"DEBUG: Added set {set_obj.set_number}: {set_obj.reps} reps at {set_obj.weight}kg")
                    
                    # Add this exercise and its sets to our collection
                    exercises.append({
                        'model': exercise,
                        'ordered_sets': sets
                    })
            except Exception as e:
                # Just log the error, don't crash
                import traceback
                print(f"ERROR getting exercises: {e}")
                print(traceback.format_exc())
        
        # Basic template render with workout data
        return render_template('workout/view.html', 
                              workout=workout, 
                              exercises=exercises)
                              
    except Exception as e:
        # Log the error but return a user-friendly message
        import traceback
        print(f"ERROR viewing workout {workout_id}: {e}")
        print(traceback.format_exc())
        flash(f"Error loading workout. Please try again.", "error")
        return redirect(url_for('workout.index'))