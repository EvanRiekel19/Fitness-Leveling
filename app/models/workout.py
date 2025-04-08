from app import db
from datetime import datetime

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'cardio', 'strength', 'flexibility'
    subtype = db.Column(db.String(50))  # e.g., 'cardio_running', 'strength_upper'
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer)  # Duration in minutes
    intensity = db.Column(db.Integer)  # 1-10 scale
    sets = db.Column(db.Integer)  # For strength training
    reps = db.Column(db.Integer)  # For strength training
    distance = db.Column(db.Float)  # For cardio (in kilometers)
    xp_earned = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    strava_id = db.Column(db.String(50), unique=True)  # Added to prevent duplicates
    
    # Add relationship to exercises
    exercises = db.relationship('Exercise', back_populates='workout', lazy='dynamic', cascade="all, delete-orphan")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.user import User
        if self.user_id:
            user = User.query.get(self.user_id)
            if user:
                try:
                    user.update_last_workout()
                except:
                    # For backward compatibility with old databases
                    pass
    
    def calculate_xp(self):
        """Calculate XP based on workout type and parameters."""
        # Base XP is higher for longer workouts
        base_xp = 75
        
        # Duration multiplier (1-3x for longer workouts)
        duration_multiplier = min(3, max(1, self.duration / 30))
        
        # Intensity multiplier (1-2x)
        intensity_multiplier = 1 + (self.intensity / 10)
        
        # Type-specific bonuses
        if self.type == 'cardio':
            if self.distance:
                # 30 XP per km
                base_xp += self.distance * 30
        elif self.type == 'strength':
            # Calculate XP based on exercises if present
            exercise_xp = 0
            
            # Extra base XP for strength workouts over 45 minutes
            if self.duration > 45:
                base_xp += (self.duration - 45) * 2  # 2 XP per minute over 45
            
            if self.exercises.count() > 0:
                # Count the total number of sets across all exercises
                total_sets = 0
                total_reps = 0
                
                for exercise in self.exercises:
                    for exercise_set in exercise.sets:
                        total_sets += 1
                        if exercise_set.reps:
                            total_reps += exercise_set.reps
                
                # Award XP based on total volume
                exercise_xp = total_sets * 12 + total_reps * 0.35
                base_xp += exercise_xp
            elif self.sets and self.reps:
                # Fallback to old calculation if no exercises are recorded
                base_xp += (self.sets * self.reps) * 0.5
        elif self.type == 'flexibility':
            # 1.5 XP per minute
            base_xp += self.duration * 1.5
            
        # Calculate final XP
        self.xp_earned = int(base_xp * duration_multiplier * intensity_multiplier)
        return self.xp_earned
        
    def get_distance_miles(self):
        """Convert kilometers to miles."""
        if self.distance:
            return self.distance * 0.621371
        return None
        
    def get_pace_per_km(self):
        """Calculate pace in minutes per kilometer for cardio workouts."""
        if self.type == 'cardio' and self.distance and self.duration:
            # Calculate pace (minutes per kilometer)
            pace = self.duration / self.distance
            # Format pace as minutes:seconds per km
            minutes = int(pace)
            seconds = int((pace - minutes) * 60)
            return f"{minutes}:{seconds:02d} /km"
        return None
        
    def get_pace_per_mile(self):
        """Calculate pace in minutes per mile for cardio workouts."""
        if self.type == 'cardio' and self.distance and self.duration:
            # Convert distance to miles and calculate pace
            miles = self.get_distance_miles()
            if miles:
                pace = self.duration / miles
                # Format pace as minutes:seconds per mile
                minutes = int(pace)
                seconds = int((pace - minutes) * 60)
                return f"{minutes}:{seconds:02d} /mi"
        return None

    def get_readable_type(self):
        """Return a human-readable workout type name."""
        # Map workout types to readable names for display
        workout_type_names = {
            # Cardio subtypes
            'cardio_running': 'Running',
            'cardio_walking': 'Walking',
            'cardio_cycling': 'Cycling',
            'cardio_swimming': 'Swimming',
            'cardio_hiit': 'HIIT',
            'cardio_other': 'Cardio',
            
            # Strength subtypes
            'strength_upper': 'Upper Body',
            'strength_lower': 'Lower Body',
            'strength_push': 'Push Workout',
            'strength_pull': 'Pull Workout',
            'strength_full': 'Full Body',
            'strength_other': 'Strength Training',
            
            # Flexibility subtypes
            'flexibility_yoga': 'Yoga',
            'flexibility_stretching': 'Stretching',
            'flexibility_other': 'Flexibility',
            
            # Legacy types (for backward compatibility)
            'cardio': 'Cardio',
            'strength': 'Strength Training',
            'flexibility': 'Flexibility'
        }
        
        # Get the readable type name
        return workout_type_names.get(self.subtype or self.type, self.type.capitalize()) 