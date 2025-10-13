@echo off
SET VENV_NAME=venv
SET WORKDIR=src
SET DOCKER_COMPOSE=docker-compose

::-----------------------
:: Help
::-----------------------
:help
echo.
echo Commands:
echo   setup.bat install        => create virtual environment and install dependencies
echo   setup.bat up             => start Flask server from src/ and display URL
echo   setup.bat docker-build   => build Docker image using Docker Compose
echo   setup.bat docker-up      => start Flask server using Docker Compose
echo.
goto :eof

::-----------------------
:: Install venv
::-----------------------
:install
echo Creating virtual environment...
python -m venv %VENV_NAME%

echo Activating virtual environment and upgrading pip...
call %VENV_NAME%\Scripts\activate.bat
pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt
goto :eof

::-----------------------
:: Run Flask with venv
::-----------------------
:up
echo Starting Flask server from %WORKDIR%...
call %VENV_NAME%\Scripts\activate.bat
cd %WORKDIR%
python app.py
goto :eof

::-----------------------
:: Build Docker image
::-----------------------
:docker-build
echo Building Docker image using Docker Compose...
%DOCKER_COMPOSE% -f docker-compose.yml build
goto :eof

::-----------------------
:: Run Flask with Docker
::-----------------------
:docker-up
echo Starting Flask server with Docker Compose...
%DOCKER_COMPOSE% -f docker-compose.yml up
goto :eof

::-----------------------
:: Check arguments
::-----------------------
if "%1"=="install" goto install
if "%1"=="up" goto up
if "%1"=="docker-build" goto docker-build
if "%1"=="docker-up" goto docker-up
goto help

