@echo off
echo Checking for virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo WARNING: Virtual environment not found!
    echo Please run setup.bat first to create the virtual environment.
    echo.
    echo Attempting to run with base Python installation...
    py app.py
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo WARNING: Failed to activate virtual environment!
    echo Attempting to run with base Python installation...
    py app.py
    pause
    exit /b 1
)

echo.
echo Starting the application...
py app.py

pause

