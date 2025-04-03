from datetime import datetime, timedelta
from app import db
from app.models.workout import Workout
from app.models.user import User

class StravaService:
    def __init__(self, client_id, client_secret):
        try:
            from stravalib import Client
            self.client = Client()
            self.client_id = client_id
            self.client_secret = client_secret
            self._strava_available = True
        except ImportError:
            self._strava_available = False
            self.client = None
            self.client_id = None
            self.client_secret = None

    def is_available(self):
        return self._strava_available

    def _check_availability(self):
        if not self._strava_available:
            raise ImportError("stravalib package is not installed")

    def get_authorization_url(self, redirect_uri):
        """Generate the authorization URL for Strava OAuth."""
        self._check_availability()
        print(f"Generating auth URL with redirect URI: {redirect_uri}")
        return self.client.authorization_url(
            client_id=self.client_id,
            redirect_uri=redirect_uri,
            approval_prompt='auto',
            scope=['read', 'activity:read_all', 'activity:read']
        )

    def get_access_token(self, code):
        """Exchange authorization code for access token."""
        self._check_availability()
        try:
            print(f"Exchanging code for token... Client ID: {self.client_id}")
            token_response = self.client.exchange_code_for_token(
                client_id=self.client_id,
                client_secret=self.client_secret,
                code=code
            )
            print("Token exchange successful")
            return token_response
        except Exception as e:
            print(f"Error exchanging code for token: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def get_athlete_activities(self, access_token, after_date=None):
        """Fetch athlete activities from Strava."""
        self._check_availability()
        try:
            print(f"Fetching activities with token: {access_token[:10]}... after date: {after_date}")
            self.client = self.client.__class__(access_token)  # Create new client instance with token
            activities = list(self.client.get_activities(limit=30))  # Get last 30 activities
            print(f"Found {len(activities)} activities")
            return activities
        except Exception as e:
            print(f"Error fetching activities: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

    def import_activity(self, activity, user):
        """Import a Strava activity as a workout."""
        self._check_availability()
        try:
            print(f"Importing activity: {activity.name} ({activity.type})")
            
            # Check if activity already exists
            existing_workout = Workout.query.filter_by(strava_id=str(activity.id)).first()
            if existing_workout:
                print(f"Activity {activity.name} already exists, skipping...")
                return None
            
            # Convert Strava activity type to our workout type
            activity_type = activity.type.root.lower() if hasattr(activity.type, 'root') else str(activity.type).lower()
            print(f"Activity type: {activity_type}")
            
            if activity_type in ['run', 'walk', 'hike']:
                workout_type = 'cardio'
            elif activity_type in ['ride', 'virtualride', 'cycling']:
                workout_type = 'cardio'
            elif activity_type in ['swim']:
                workout_type = 'cardio'
            elif activity_type in ['weighttraining', 'workout', 'strength']:
                workout_type = 'strength'
            else:
                workout_type = 'other'

            print(f"Mapped to workout type: {workout_type}")

            # Calculate duration in minutes - handle Duration object
            if hasattr(activity.elapsed_time, 'seconds'):
                duration = int(activity.elapsed_time.seconds / 60)
            else:
                duration = int(float(str(activity.elapsed_time)) / 60)
            print(f"Duration: {duration} minutes")

            # Get distance if available
            distance = None
            if hasattr(activity, 'distance'):
                if hasattr(activity.distance, 'num'):
                    distance = float(activity.distance.num) / 1000  # Convert to km
                else:
                    distance = float(str(activity.distance)) / 1000  # Convert to km
                print(f"Distance: {distance} km")

            # Calculate intensity based on distance for runs
            intensity = 5  # Default intensity
            if activity_type == 'run' and distance is not None:
                # Convert km to miles
                miles = distance * 0.621371
                # Set intensity based on miles (1-10 scale)
                intensity = min(10, max(1, int(miles)))
                print(f"Run distance: {miles:.2f} miles -> Intensity: {intensity}")
            elif hasattr(activity, 'suffer_score') and activity.suffer_score:
                intensity = min(10, max(1, int(activity.suffer_score / 10)))
            print(f"Final intensity: {intensity}")

            # Create workout
            workout = Workout(
                user_id=user.id,
                name=str(activity.name),
                type=workout_type,
                duration=duration,
                intensity=intensity,
                distance=distance,
                notes=f"Imported from Strava: {activity.description if hasattr(activity, 'description') else ''}",
                created_at=activity.start_date_local,
                strava_id=str(activity.id)  # Store Strava ID to prevent duplicates
            )
            
            print(f"Adding workout to database: {workout.name}")
            db.session.add(workout)
            db.session.commit()
            
            # Calculate XP after commit to ensure we have the workout ID
            xp = workout.calculate_xp()
            print(f"Workout base XP calculated: {xp}")
            
            # Update user's XP using the proper method
            leveled_up = user.add_xp(xp)
            print(f"Added {xp} XP to user (new total: {user.xp})")
            if leveled_up:
                print(f"Level up! Now level {user.level}")
            
            db.session.commit()
            
            return workout
        except Exception as e:
            print(f"Error importing activity: {str(e)}")
            import traceback
            print(traceback.format_exc())
            db.session.rollback()
            return None

    def sync_activities(self, user):
        """Sync recent activities from Strava."""
        self._check_availability()
        print("\n=== Starting Strava Sync ===")
        if not user.strava_access_token:
            print("No Strava access token found")
            return []

        # Get the last sync time or default to 7 days ago
        last_sync = user.strava_last_sync or (datetime.utcnow() - timedelta(days=7))
        print(f"Last sync: {last_sync}")
        
        try:
            print("Fetching activities from Strava...")
            activities = self.get_athlete_activities(user.strava_access_token, after_date=last_sync)
            imported_workouts = []
            
            print(f"Processing {len(activities)} activities...")
            for activity in activities:
                workout = self.import_activity(activity, user)
                if workout:
                    imported_workouts.append(workout)
                    print(f"Successfully imported: {workout.name}")
            
            # Update last sync time
            user.strava_last_sync = datetime.utcnow()
            db.session.commit()
            
            print(f"=== Sync Complete: Imported {len(imported_workouts)} activities ===\n")
            return imported_workouts
        except Exception as e:
            print(f"Error syncing Strava activities: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return [] 