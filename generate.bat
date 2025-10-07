@echo off
REM University Application Document Generator - Windows Batch Script
REM Usage: generate.bat [school_id|all|list]

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%build_scripts"

if "%1"=="" (
    echo 🎓 University Application Document Generator
    echo.
    echo Usage:
    echo   generate.bat list          - List all available schools
    echo   generate.bat all           - Generate documents for all active schools
    echo   generate.bat taltech       - Generate documents for TalTech
    echo   generate.bat aalto         - Generate documents for Aalto University
    echo.
    goto :end
)

if "%1"=="list" (
    python generate_docs.py --list
    goto :end
)

if "%1"=="all" (
    python generate_docs.py --all
    goto :end
)

REM Generate for specific school
python generate_docs.py --school %1

:end
pause
