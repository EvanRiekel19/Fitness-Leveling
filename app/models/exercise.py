from app import db

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Name of the exercise (e.g., "Bench Press")
    sets = db.relationship('app.models.exercise_set.ExerciseSet', back_populates='exercise', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Exercise {self.name}>'

# Removed duplicate ExerciseSet class 