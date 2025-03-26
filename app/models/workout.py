from app import db
from datetime import datetime

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'cardio', 'strength', 'flexibility'
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
    
    def calculate_xp(self):
        """Calculate XP based on workout type and parameters."""
        # Base XP is now lower
        base_xp = 50
        
        # Duration multiplier (1-2x) - reduced from 1-3x
        duration_multiplier = min(2, max(1, self.duration / 45))
        
        # Intensity multiplier (1-1.5x) - reduced from 1-2x
        intensity_multiplier = 1 + (self.intensity / 20)
        
        # Type-specific bonuses - reduced values
        if self.type == 'cardio':
            if self.distance:
                # 25 XP per km instead of 50
                base_xp += self.distance * 25
        elif self.type == 'strength':
            if self.sets and self.reps:
                # 0.25 XP per rep instead of 0.5
                base_xp += (self.sets * self.reps) * 0.25
        elif self.type == 'flexibility':
            # 1 XP per minute instead of 2
            base_xp += self.duration
            
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