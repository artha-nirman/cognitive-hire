@echo off
REM This script activates the virtual environment and runs the AI recruitment agent

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Running AI recruitment agent...
venv\Scripts\python.exe -m src.main %*

REM Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo An error occurred while running the agent.
  pause
)