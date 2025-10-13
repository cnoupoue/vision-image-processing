@echo off
SET VENV_NAME=venv
SET WORKDIR=src

:help
echo.
echo Commands:
echo   setup.bat install   => create virtual environment and install dependencies
echo   setup.bat up        => start Flask server from src/ and display URL
echo.
goto :eof

:install
echo Creating virtual environment...
python -m venv %VENV_NAME%

echo Activating virtual environment and upgrading pip...
call %VENV_NAME%\Scripts\activate.bat
pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt
goto :eof

:up
echo Starting Flask server from %WORKDIR%...
echo Visit: http://127.0.0.1:5000/
call %VENV_NAME%\Scripts\activate.bat
cd %WORKDIR%
python app.py
goto :eof

:: Check arguments
if "%1"=="install" goto install
if "%1"=="up" goto up
goto help

