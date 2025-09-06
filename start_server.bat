@echo off
echo Starting IDVerse Flask Server...
echo.

REM Activate virtual environment
call env\Scripts\activate.bat

REM Run the Flask application
python run.py

pause

