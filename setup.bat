@echo off
echo Creating virtual environment...
py -m venv venv

if %errorlevel% neq 0 (
    echo WARNING: Failed to create virtual environment!
    echo Installing requirements in base Python environment...
    py -m pip install -r requirements.txt
    echo.
    echo Setup complete with warnings! Check above for errors.
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo WARNING: Failed to activate virtual environment!
    echo Installing requirements anyway...
    py -m pip install -r requirements.txt
    echo.
    echo Setup complete with warnings! Check above for errors.
    pause
    exit /b 1
)

echo.
echo Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements!
    pause
    exit /b 1
)

echo.
echo Setup complete! You can now run the app using run.bat
pause

