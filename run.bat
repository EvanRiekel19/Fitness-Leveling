@echo off
echo Starting Fitness Leveling Application...
python run.py
if errorlevel 1 (
    echo Application terminated with an error.
    pause
) else (
    echo Application closed successfully.
    timeout /t 2 >nul
) 