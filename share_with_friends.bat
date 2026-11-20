@echo off
title Share ParkEase with Friends Anywhere
cd /d "%~dp0"

echo ================================================================
echo   ParkEase - Instant Public Sharing Tunnel
echo ================================================================
echo.
echo  1. Make sure your Django server is running in another window!
echo  2. Connecting to secure public gateway...
echo.
echo  Copy the link that appears below and send it to your friend:
echo ================================================================
echo.

ssh -o StrictHostKeyChecking=no -p 443 -R0:127.0.0.1:8000 a.pinggy.io

pause
