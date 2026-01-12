@echo off
REM ====================================================================
REM CLOs Measurement System - Startup Script
REM نظام قياس مخرجات التعلم - ملف التشغيل
REM ====================================================================

chcp 65001 > nul
color 0A
cls

echo.
echo ====================================================================
echo.
echo    CLOs Measurement System
echo    نظام قياس مخرجات التعلم للمقررات الدراسية
echo.
echo    University of Tabuk - جامعة تبوك
echo    Department of Statistics - قسم الإحصاء
echo.
echo ====================================================================
echo.
echo Starting application...
echo جاري تشغيل البرنامج...
echo.
echo Login credentials - بيانات الدخول:
echo   Username - اسم المستخدم: admin
echo   Password - كلمة المرور: admin123
echo.
echo ====================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run the application
python main.py

REM Check if there was an error
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo ERROR - خطأ
    echo ====================================================================
    echo.
    echo The application encountered an error.
    echo البرنامج واجه خطأ.
    echo.
    echo Please check:
    echo الرجاء التحقق من:
    echo   1. Python is installed correctly
    echo   2. All required libraries are installed
    echo   3. Run: python diagnose.py
    echo.
    echo ====================================================================
    echo.
    pause
) else (
    echo.
    echo ====================================================================
    echo Application closed successfully.
    echo تم إغلاق البرنامج بنجاح.
    echo ====================================================================
    echo.
)

exit /b
