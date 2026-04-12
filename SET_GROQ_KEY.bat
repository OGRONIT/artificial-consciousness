@echo off
REM Simple batch file to set Groq API key and launch the UI
REM Right-click and edit this file, replace YOUR_KEY_HERE with your actual Groq API key

setlocal enabledelayedexpansion

echo.
echo ====================================================
echo  ANTAHKARANA - Groq API Key Setup
echo ====================================================
echo.

REM Set your Groq key here
set "GROQ_API_KEY=YOUR_KEY_HERE"

if "%GROQ_API_KEY%"=="YOUR_KEY_HERE" (
    echo ERROR: You need to edit this file!
    echo.
    echo 1. Right-click this batch file: SET_GROQ_KEY.bat
    echo 2. Click "Edit"
    echo 3. Find: set "GROQ_API_KEY=YOUR_KEY_HERE"
    echo 4. Replace YOUR_KEY_HERE with your actual Groq key
    echo 5. Save and run again
    echo.
    echo Example: set "GROQ_API_KEY=gsk_abc123def456xyz789"
    echo.
    pause
    exit /b 1
)

echo [OK] GROQ_API_KEY set to: %GROQ_API_KEY:~0,10%...
echo.
echo Launching Mission Control UI...
echo.

cd /d "D:\Artificial Consciousness\antahkarana_kernel"
python UnifiedConsciousnessUI.py

pause
