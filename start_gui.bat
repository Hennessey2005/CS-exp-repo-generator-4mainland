@echo off

REM Simple GUI Launch Script for Report Generator

cls
echo ==========================================================
echo           REPORT GENERATOR GUI LAUNCHER           
echo ==========================================================

REM Change to script directory
cd /d "%~dp0"
echo Working directory: %CD%

REM Use system Python
set "PYTHON_EXE=python"

REM Check Python environment
echo Checking Python environment...
%PYTHON_EXE% --version

REM Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies...
    %PYTHON_EXE% -m pip install -r requirements.txt --upgrade --user
)

REM Launch GUI using Python script
echo Starting GUI...
%PYTHON_EXE% start_gui.py

REM Check result
if %errorlevel% neq 0 (
    echo Launch failed! Trying alternative method...
    pause
    REM Try direct module execution
    %PYTHON_EXE% -m report_generator.gui
)

echo Program exited
pause