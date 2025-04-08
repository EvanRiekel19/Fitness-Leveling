from app import db
from datetime import datetime

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'strength' or 'cardio'
    subtype = db.Column(db.String(50))  # e.g., 'push', 'pull', 'legs', 'running', 'cycling'
    name = db.Column(db.String(100))
    duration = db.Column(db.Integer)  # in minutes
    intensity = db.Column(db.Integer)  # scale of 1-10
    distance = db.Column(db.Float)  # in kilometers
    calories = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    xp_earned = db.Column(db.Integer)
    
    # Relationships
    exercises = db.relationship('Exercise', back_populates='workout', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Workout {self.id}: {self.type}>'
    
    def calculate_xp(self):
        """Calculate XP earned for this workout."""
        base_xp = 50  # Base XP for completing any workout
        
        # Duration bonus (every 10 minutes = +5 XP)
        duration_bonus = (self.duration or 0) // 10 * 5
        
        # Intensity bonus (intensity level * 5)
        intensity_bonus = (self.intensity or 0) * 5
        
        # Distance bonus for cardio (every km = +10 XP)
        distance_bonus = int((self.distance or 0) * 10)
        
        # Exercise bonus for strength (+10 XP per exercise)
        exercise_bonus = 0
        if self.type == 'strength':
            exercise_bonus = self.exercises.count() * 10
        
        total_xp = base_xp + duration_bonus + intensity_bonus + distance_bonus + exercise_bonus
        self.xp_earned = total_xp
        return total_xp

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