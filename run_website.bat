@echo off
title ParkEase - Development Server Launcher
cd /d "%~dp0"

echo ====================================================
echo   Starting ParkEase Website...
echo ====================================================
echo.

REM Automatically open the browser after 2 seconds in the background
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000/"

REM Start the Django server allowing local network & mobile access
C:\Users\Admin\anaconda3\python.exe manage.py runserver 0.0.0.0:8000

pause
