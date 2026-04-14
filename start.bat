@echo off
chcp 65001 >nul
title CB_VideoCraft Dev Server

echo ========================================
echo   CB_VideoCraft Development Server
echo ========================================
echo.

:: Start backend
echo [1/2] Starting backend...
start "CB_VideoCraft Backend" cmd /k "cd /d d:\codebudy-code\video-craft-main\backend && d:\codebudy-code\video-craft-main\backend\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
echo [2/2] Starting frontend...
start "CB_VideoCraft Frontend" cmd /k "cd /d d:\codebudy-code\video-craft-main\frontend && npm run dev"

echo.
echo ========================================
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:5174
echo ========================================
echo.
echo Two new windows opened. Close them to stop the servers.
pause
