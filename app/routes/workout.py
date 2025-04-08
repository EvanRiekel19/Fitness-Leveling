from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.workout import Workout
from app.models.exercise import Exercise
from app.models.exercise_set import ExerciseSet
from app import db
import json
from sqlalchemy import text

bp = Blueprint('workout', __name__)

@bp.route('/workouts')
@login_required
def index():
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.created_at.desc()).all()
    return render_template('workout/index.html', workouts=workouts)

@bp.route('/workouts/new', methods=['GET', 'POST'])
@login_required
def new():
    # Show workout type selection page
    return render_template('workout/new.html')

@bp.route('/workouts/new/cardio', methods=['GET', 'POST'])
@login_required
def new_cardio():
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
            subtype = request.form.get('subtype', 'cardio_other')
            print(f"DEBUG CARDIO: Using subtype: {subtype}")
            
            # Get distance and convert if needed
            distance = safe_float(request.form.get('distance'))
            if distance > 0 and current_user.distance_unit == 'miles':
                # Convert miles to kilometers for storage
                distance = distance * 1.60934
            
            # Create workout
            workout = Workout(
                user_id=current_user.id,
                type='cardio',
                subtype=subtype,
                name=request.form.get('name', ''),
                duration=safe_int(request.form.get('duration')),
                intensity=safe_int(request.form.get('intensity'), 5),
                distance=distance,
                notes=request.form.get('notes', '')
            )
            
            # Validate required fields
            if not workout.name:
                flash('Workout name is required', 'error')
                return render_template('workout/new_cardio.html')
            
            if workout.duration <= 0:
                flash('Duration must be greater than 0', 'error')
                return render_template('workout/new_cardio.html')
            
            # Save workout
            db.session.add(workout)
            
            # Calculate XP and update user
            try:
                xp_earned = workout.calculate_xp()
                print(f"DEBUG CARDIO: Calculated XP: {xp_earned}")
                
                current_user.add_xp(xp_earned)
                print(f"DEBUG CARDIO: Added XP to user")
            except Exception as e:
                print(f"DEBUG CARDIO: XP calculation/assignment error: {e}")
                xp_earned = 50  # Fallback
            
            db.session.commit()
            print(f"DEBUG CARDIO: Successfully committed workout")
            
            flash(f'Cardio workout logged! Earned {xp_earned} XP', 'success')
            return redirect(url_for('workout.index'))
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"ERROR in cardio workout submission: {e}")
            print(traceback.format_exc())
            flash(f'Error logging workout: {str(e)}', 'error')
            return render_template('workout/new_cardio.html')
    else:  # GET request
        # Get workout history for all cardio workout types
        workout_history = {}
        for workout_type in ['cardio_running', 'cardio_cycling', 'cardio_swimming', 'cardio_hiit', 'cardio_other']:
            history = get_workout_history(workout_type, current_user.id)
            if history:
                workout_history[workout_type] = history
        
        # Render template with user's distance unit preference
        return render_template(
            'workout/new_cardio.html',
            workout_history=workout_history,
            distance_unit=current_user.distance_unit
        )

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

def get_workout_history(workout_type, user_id):
    """Get previous workout data and PRs for a specific workout type."""
    try:
        print(f"\nDEBUG: Getting workout history for type: {workout_type}")
        
        # First, let's see what workouts exist with their exact types/subtypes
        all_workouts = db.session.execute(text("""
            SELECT id, name, type, subtype, created_at
            FROM workout 
            WHERE user_id = :user_id
            AND (
                type = 'strength' 
                OR subtype LIKE '%push%'
                OR subtype LIKE '%pull%'
                OR subtype LIKE '%legs%'
                OR name LIKE '%push%'
                OR name LIKE '%pull%'
                OR name LIKE '%legs%'
            )
            ORDER BY created_at DESC
        """), {'user_id': user_id}).fetchall()
        
        print("\nDEBUG: Recent strength/split workouts in system:")
        for w in all_workouts:
            print(f"ID: {w[0]}, Name: {w[1]}, Type: {w[2]}, Subtype: {w[3]}, Date: {w[4]}")
        
        # Now get the matching workouts with expanded matching criteria
        workouts = db.session.execute(text("""
            SELECT id, name, duration, intensity, created_at, notes, type, subtype
            FROM workout
            WHERE user_id = :user_id 
            AND (
                subtype = :workout_type 
                OR subtype LIKE :like_pattern
                OR (subtype IS NULL AND type = 'strength' AND (
                    name ILIKE :name_pattern
                    OR name ILIKE :alt_pattern
                ))
            )
            ORDER BY created_at DESC
            LIMIT 5
        """), {
            'workout_type': workout_type,
            'user_id': user_id,
            'like_pattern': f'%{workout_type.replace("strength_", "")}%',
            'name_pattern': f'%{workout_type.replace("strength_", "").replace("_", " ")}%',
            'alt_pattern': f'%{workout_type.replace("strength_", "").replace("_", "")}%'
        }).fetchall()
        
        print(f"\nDEBUG: Found {len(workouts) if workouts else 0} matching workouts")
        for w in (workouts or []):
            print(f"Matching workout - ID: {w[0]}, Name: {w[1]}, Date: {w[4]}, Type: {w[6]}, Subtype: {w[7]}")
        
        if not workouts:
            print("DEBUG: No matching workouts found")
            return None
            
        # Process the most recent workout
        last_workout = workouts[0]
        workout_id = last_workout[0]
        
        # Get exercises and their sets for this workout
        exercises = db.session.execute(text("""
            SELECT 
                e.id, 
                e.name,
                array_agg(s.set_number ORDER BY s.set_number) as set_numbers,
                array_agg(s.reps ORDER BY s.set_number) as reps,
                array_agg(s.weight ORDER BY s.set_number) as weights,
                array_agg(s.notes ORDER BY s.set_number) as notes
            FROM exercise e
            LEFT JOIN exercise_set s ON e.id = s.exercise_id
            WHERE e.workout_id = :workout_id
            GROUP BY e.id, e.name
            ORDER BY e.id
        """), {'workout_id': workout_id}).fetchall()
        
        print(f"\nDEBUG: Found {len(exercises)} exercises")
        for ex in exercises:
            print(f"Exercise: {ex[1]}")
            for i in range(len(ex[2])):
                print(f"  Set {ex[2][i]}: {ex[3][i]} reps at {ex[4][i]}kg")
        
        # Format the response
        return {
            'last_workout': {
                'id': last_workout[0],
                'name': last_workout[1],
                'duration': last_workout[2],
                'intensity': last_workout[3],
                'date': last_workout[4],
                'notes': last_workout[5],
                'exercises': [{
                    'name': ex[1],
                    'sets': [{
                        'set_number': set_num,
                        'reps': reps,
                        'weight': weight,
                        'notes': note
                    } for set_num, reps, weight, note in zip(ex[2], ex[3], ex[4], ex[5])]
                } for ex in exercises]
            }
        }
    except Exception as e:
        print(f"Error in get_workout_history: {str(e)}")
        db.session.rollback()  # Add rollback to handle transaction errors
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

            # Process exercises data from form
            try:
                exercises_data = request.form.get('exercises_data', '[]')
                print(f"DEBUG STRENGTH: Exercises data length: {len(exercises_data)}")
                
                exercises_data = json.loads(exercises_data)
                print(f"DEBUG STRENGTH: Found {len(exercises_data)} exercises")
            except json.JSONDecodeError as e:
                print(f"DEBUG STRENGTH: JSON decode error: {e}")
                exercises_data = []

            # Create workout
            workout = Workout(
                user_id=current_user.id,
                type='strength',
                subtype=request.form.get('subtype', 'strength_full'),
                name=request.form.get('name', ''),
                duration=safe_int(request.form.get('duration')),
                intensity=safe_int(request.form.get('intensity')),
                notes=request.form.get('notes', '')
            )

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

                    # Create exercise
                    exercise = Exercise(
                        workout_id=workout.id,
                        name=exercise_name
                    )
                    db.session.add(exercise)
                    db.session.flush()
                    print(f"DEBUG STRENGTH: Created exercise '{exercise_name}' with ID: {exercise.id}")

                    # Add sets for this exercise
                    sets_data = exercise_data.get('sets', [])
                    print(f"DEBUG STRENGTH: Processing {len(sets_data)} sets for exercise '{exercise_name}'")

                    for set_data in sets_data:
                        exercise_set = ExerciseSet(
                            exercise_id=exercise.id,
                            set_number=set_data.get('set_number', 1),
                            reps=safe_int(set_data.get('reps')),
                            weight=safe_float(set_data.get('weight')),
                            notes=set_data.get('notes', '')
                        )
                        db.session.add(exercise_set)
                        print(f"DEBUG STRENGTH: Added set {exercise_set.set_number} with {safe_int(set_data.get('reps'))} reps at {safe_float(set_data.get('weight'))} kg")

                except Exception as e:
                    print(f"DEBUG STRENGTH: Error adding exercise {i+1}: {e}")
                    db.session.rollback()
                    flash('Error adding exercise. Please try again.', 'error')
                    return redirect(url_for('workout.new_strength'))

            # Calculate and set XP
            xp_earned = workout.calculate_xp()
            print(f"DEBUG STRENGTH: Calculated XP: {xp_earned}")
            workout.xp_earned = xp_earned

            # Commit all changes
            db.session.commit()
            print(f"DEBUG STRENGTH: Successfully committed workout with {len(exercises_data)} exercises")

            flash(f'Strength workout logged! Earned {xp_earned} XP', 'success')
            return redirect(url_for('workout.index'))

        except Exception as e:
            print(f"ERROR in strength workout submission: {e}")
            db.session.rollback()
            flash('Error logging workout. Please try again.', 'error')
            return redirect(url_for('workout.new_strength'))

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
    # Get the workout
    try:
        workout = Workout.query.get_or_404(workout_id)
        print(f"\nDEBUG: Loading workout {workout_id}")
        
        # Security check
        if workout.user_id != current_user.id:
            flash('You do not have permission to view this workout', 'error')
            return redirect(url_for('workout.index'))
        
        # Variable to store all exercises and their sets
        exercises = []
        
        # Only get exercises for strength workouts
        if workout.type == 'strength':
            print(f"DEBUG: Processing strength workout")
            try:
                # Get all exercises using parameterized query
                exercise_sql = """
                    SELECT id, workout_id, name 
                    FROM exercise 
                    WHERE workout_id = :workout_id
                    ORDER BY id
                """
                exercises_result = db.session.execute(exercise_sql, {"workout_id": workout_id})
                exercise_rows = exercises_result.fetchall()
                
                print(f"DEBUG: Found {len(exercise_rows)} exercises")
                
                # Process each exercise
                for ex_row in exercise_rows:
                    ex_id = ex_row[0]
                    ex_name = ex_row[2]
                    
                    print(f"\nDEBUG: Processing exercise {ex_id}: {ex_name}")
                    
                    # Get all sets for this exercise using parameterized query
                    sets_sql = """
                        SELECT es.id, es.exercise_id, es.set_number, es.reps, es.weight, es.notes
                        FROM exercise_set es
                        WHERE es.exercise_id = :exercise_id
                        ORDER BY es.set_number ASC
                    """
                    sets_result = db.session.execute(sets_sql, {"exercise_id": ex_id})
                    set_rows = sets_result.fetchall()
                    
                    print(f"DEBUG: Found {len(set_rows)} sets")
                    
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
                        set_number = set_row[2]  # Get the set number from the database
                        exercise_set = {
                            'id': set_row[0],
                            'set_number': set_number,
                            'reps': set_row[3],
                            'weight': set_row[4],
                            'notes': set_row[5] if set_row[5] else ''
                        }
                        print(f"DEBUG: Processing set {set_number}: {exercise_set['reps']} reps at {exercise_set['weight']}kg")
                        exercise['ordered_sets'].append(exercise_set)
                    
                    # Sort sets by set number to ensure correct order
                    exercise['ordered_sets'].sort(key=lambda x: x['set_number'])
                    
                    # Add this exercise to our list
                    exercises.append(exercise)
                    print(f"DEBUG: Added exercise {ex_name} with {len(exercise['ordered_sets'])} sets")
                    print("DEBUG: Set numbers:", [s['set_number'] for s in exercise['ordered_sets']])
            
            except Exception as e:
                import traceback
                print(f"ERROR fetching exercises: {e}")
                print(traceback.format_exc())
                # Don't fail completely - continue with empty exercises list
        
        # Render the template with all our data
        print("\nDEBUG: Final data:")
        print(f"Workout: {workout.name}")
        print(f"Total exercises: {len(exercises)}")
        for ex in exercises:
            print(f"Exercise {ex['model']['name']}: {len(ex['ordered_sets'])} sets")
        
        return render_template('workout/view.html', workout=workout, exercises=exercises)
    
    except Exception as e:
        import traceback
        print(f"Error loading workout {workout_id}: {e}")
        print(traceback.format_exc())
        flash('Error loading workout details. Please try again.', 'error')
        return redirect(url_for('workout.index'))

@bp.route('/api/workouts/last/<workout_type>')
@login_required
def get_last_workout(workout_type):
    """Get the last workout of a specific type."""
    try:
        print(f"DEBUG API: Getting last workout for type: {workout_type}")
        # Get the last workout of this type, handling both old and new format
        workout = db.session.execute("""
            SELECT id, name, duration, intensity, date, notes
            FROM workout
            WHERE user_id = :user_id 
            AND (
                subtype = :workout_type 
                OR (subtype IS NULL AND type = 'strength' AND name ILIKE :name_pattern)
            )
            ORDER BY date DESC
            LIMIT 1
        """, {
            'workout_type': workout_type, 
            'user_id': current_user.id,
            'name_pattern': '%' + workout_type.replace('strength_', '').replace('_', ' ') + '%'
        }).fetchone()
        
        print(f"DEBUG API: Found workout: {workout is not None}")
        
        if not workout:
            return jsonify({'last_workout': None})
            
        # Get exercises for this workout
        exercises = db.session.execute("""
            SELECT e.id, e.name, 
                   COUNT(DISTINCT es.id) as total_sets,
                   MAX(es.weight) as max_weight,
                   MAX(es.reps) as max_reps,
                   SUM(es.weight * es.reps) as total_volume
            FROM exercise e
            LEFT JOIN exercise_set es ON e.id = es.exercise_id
            WHERE e.workout_id = :workout_id
            GROUP BY e.id, e.name
        """, {'workout_id': workout[0]}).fetchall()
        
        workout_data = {
            'id': workout[0],
            'name': workout[1],
            'duration': workout[2],
            'intensity': workout[3],
            'date': workout[4].isoformat() if workout[4] else None,
            'notes': workout[5],
            'exercises': [{
                'name': ex[1],
                'total_sets': ex[2],
                'max_weight': ex[3],
                'max_reps': ex[4],
                'total_volume': ex[5]
            } for ex in exercises]
        }
        
        return jsonify({'last_workout': workout_data})
    except Exception as e:
        print(f"Error getting last workout: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/workouts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Get the workout
    workout = Workout.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
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

            # Update workout details
            workout.name = request.form.get('name', workout.name)
            workout.duration = safe_int(request.form.get('duration'), workout.duration)
            workout.intensity = safe_int(request.form.get('intensity'), workout.intensity)
            workout.notes = request.form.get('notes', workout.notes)
            workout.subtype = request.form.get('subtype', workout.subtype)
            
            # Process exercises data from form
            try:
                exercises_data = json.loads(request.form.get('exercises_data', '[]'))
                
                # Delete existing exercises and their sets
                for exercise in workout.exercises:
                    for set_ in exercise.sets:
                        db.session.delete(set_)
                    db.session.delete(exercise)
                
                # Create new exercises and sets
                for exercise_data in exercises_data:
                    exercise = Exercise(
                        workout_id=workout.id,
                        name=exercise_data['name']
                    )
                    db.session.add(exercise)
                    db.session.flush()  # Get the exercise ID
                    
                    # Add sets for this exercise
                    for set_data in exercise_data['sets']:
                        set_ = ExerciseSet(
                            exercise_id=exercise.id,
                            set_number=set_data['set_number'],
                            weight=safe_float(set_data.get('weight')),
                            reps=safe_int(set_data.get('reps')),
                            notes=set_data.get('notes', '')
                        )
                        db.session.add(set_)
                
                db.session.commit()
                flash('Workout updated successfully!', 'success')
                return redirect(url_for('workout.view', workout_id=workout.id))
                
            except json.JSONDecodeError:
                flash('Invalid exercise data format', 'error')
                db.session.rollback()
                return redirect(url_for('workout.edit', id=workout.id))
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating workout: {str(e)}', 'error')
            return redirect(url_for('workout.edit', id=workout.id))
    
    # GET request - show edit form
    # Get exercises and their sets
    exercises = []
    for exercise in workout.exercises:
        sets = []
        for set_ in sorted(exercise.sets, key=lambda x: x.set_number):
            sets.append({
                'set_number': set_.set_number,
                'weight': set_.weight,
                'reps': set_.reps,
                'notes': set_.notes
            })
        exercises.append({
            'name': exercise.name,
            'sets': sets
        })
    
    # Convert exercises to JSON for the form
    exercises_json = json.dumps(exercises)
    
    # Get exercise history for this user
    exercise_history = {}
    for exercise in workout.exercises:
        history = get_exercise_history(exercise.name, current_user.id)
        if history:
            exercise_history[exercise.name] = history
    
    # Get workout history for this user
    workout_history = get_workout_history(workout.subtype or 'strength_full', current_user.id)
    
    return render_template('workout/new_strength.html', 
                         workout=workout,
                         exercise_options=get_exercise_options(),
                         initial_exercises=exercises_json,
                         exercise_history=exercise_history,
                         workout_history=workout_history)