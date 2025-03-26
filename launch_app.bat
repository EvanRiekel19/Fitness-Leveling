@echo off
cd /d "%~dp0"
call venv\Scripts\activate
set FLASK_APP=app
set FLASK_ENV=development
start http://localhost:5000
flask run
pause 