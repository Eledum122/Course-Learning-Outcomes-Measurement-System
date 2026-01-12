@echo off
REM ====================================================================
REM CLOs Measurement System - Install Required Libraries
REM نظام قياس مخرجات التعلم - تثبيت المكتبات المطلوبة
REM ====================================================================

chcp 65001 > nul
color 0B
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║     CLOs Measurement System - Install Libraries                 ║
echo ║     نظام قياس مخرجات التعلم - تثبيت المكتبات                   ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo ✓ Virtual environment detected - تم العثور على البيئة الافتراضية
    echo.
    echo Installing libraries in virtual environment...
    echo جاري تثبيت المكتبات في البيئة الافتراضية...
    echo.

    REM Fix pip first
    .venv\Scripts\python.exe -m ensurepip --upgrade

    REM Install requirements
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt

    echo.
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo ✅ Installation complete! - اكتمل التثبيت!
    echo.
    echo To run the application, double-click:
    echo لتشغيل البرنامج، اضغط مرتين على:
    echo    START_WITH_VENV.bat
    echo.
) else (
    echo ⚠ No virtual environment found - لم يتم العثور على بيئة افتراضية
    echo.
    echo Installing libraries in global Python...
    echo جاري تثبيت المكتبات في Python العام...
    echo.

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

    echo.
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo ✅ Installation complete! - اكتمل التثبيت!
    echo.
    echo To run the application, double-click:
    echo لتشغيل البرنامج، اضغط مرتين على:
    echo    START_HERE.bat
    echo.
)

echo ════════════════════════════════════════════════════════════════
echo.
pause
