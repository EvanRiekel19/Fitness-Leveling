# Fitness Leveling App

A gamified fitness tracking application that combines workout tracking with an XP-based leveling system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone or download this repository
2. Open a terminal/command prompt in the project directory
3. Run the setup script:
   ```bash
   python setup.py
   ```

The setup script will:
- Create a virtual environment
- Install all required dependencies
- Set up the project structure
- Create necessary directories and files

## Project Structure

```
fitness_leveling/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   ├── models/
│   ├── forms/
│   └── routes/
├── migrations/
├── instance/
├── venv/
├── requirements.txt
├── setup.py
└── README.md
```

## Running the Application

1. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

2. Run the Flask application:
   ```bash
   flask run
   ```

3. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Features

- User profile and avatar system
- Workout tracking
- XP-based leveling system
- Achievement system
- Progress tracking
- Gamified fitness experience

## Development

To start developing:
1. Make sure you're in the virtual environment
2. The project structure is set up for easy development
3. Follow Flask's development guidelines for best practices

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Ranks and XP Requirements

Your rank is determined by your total XP. Here are all available ranks and their requirements:

| Rank | XP Required |
|------|------------|
| Bronze | 0 - 1,999 XP |
| Silver | 2,000 - 4,999 XP |
| Gold | 5,000 - 9,999 XP |
| Platinum | 10,000 - 19,999 XP |
| Diamond | 20,000 - 34,999 XP |
| Master | 35,000 - 54,999 XP |
| Grandmaster | 55,000 - 79,999 XP |
| Elite | 80,000 - 109,999 XP |
| Legend | 110,000 - 149,999 XP |
| Mythic | 150,000 - 199,999 XP |
| GOAT | 200,000+ XP |

Each rank represents a significant milestone in your fitness journey. Keep working out to climb the ranks!

Note: Your rank is independent of your level. While levels increase more frequently to provide regular progress feedback, ranks are more challenging to achieve and represent long-term dedication to your fitness goals. 