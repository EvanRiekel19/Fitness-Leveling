import os
import signal
import sys
from app import create_app

app = create_app()

def signal_handler(sig, frame):
    print('\nShutting down gracefully...')
    sys.exit(0)

if __name__ == '__main__':
    # Register the signal handler for SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the Flask application
        app.run(debug=True)
    except KeyboardInterrupt:
        print('\nShutting down gracefully...')
        sys.exit(0) 