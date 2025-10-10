@echo off
REM Safe validation summary script for Windows
REM This avoids indentation issues with inline Python commands

cd /d "%~dp0"
set PYTHONPATH=%PYTHONPATH%;%cd%\..

echo 📊 Generating validation summary...
python validation_summary.py

if %ERRORLEVEL% EQU 0 (
    echo ✅ Validation summary completed successfully
) else (
    echo ❌ Validation summary failed with error code %ERRORLEVEL%
)

pause
