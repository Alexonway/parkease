@echo off
title Share ParkEase with Friends Anywhere
cd /d "%~dp0"

echo ================================================================
echo   ParkEase - Instant Public Sharing Tunnel
echo ================================================================
echo.

REM Verify that Django is active on port 8000
netstat -aon | findstr :8000 | findstr LISTENING >nul 2>&1
if errorlevel 1 (
    echo [WARNING] ParkEase server is NOT running on port 8000!
    echo Please double-click 'run_website.bat' first, then run this file.
    echo.
    pause
    exit /b
)

echo [OK] Local ParkEase server is active on port 8000.
echo Connecting to secure public gateway...
echo.
echo ================================================================
echo  Copy the link below and send it to your friend:
echo  (When opening in browser, click the red "Enter site" button)
echo ================================================================
echo.

ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -p 443 -R0:127.0.0.1:8000 a.pinggy.io

pause
