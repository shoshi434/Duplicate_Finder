@echo off
chcp 65001 >nul
echo ========================================
echo   בונה EXE - SHOSHI Duplicate Finder
echo ========================================
echo.

echo [1/2] בונה את הקובץ...
echo זה יכול לקחת 1-2 דקות...
echo.

python -m pip install pyinstaller --user --quiet

python -m PyInstaller --noconfirm --onefile --windowed --name="SHOSHI_Duplicate_Finder" duplicate_finder.py 2>build_errors.txt

if exist "dist\SHOSHI_Duplicate_Finder.exe" (
    echo.
    echo ========================================
    echo   SUCCESS! הקובץ מוכן
    echo ========================================
    echo.
    echo הקובץ נמצא ב: dist\SHOSHI_Duplicate_Finder.exe
    echo.
    echo אפשר להעתיק אותו לכל מחשב!
    echo.
    explorer dist
) else (
    echo.
    echo ========================================
    echo   שגיאה - ראה הוראות חלופיות למטה
    echo ========================================
    echo.
    echo פתרון חלופי:
    echo 1. פתח PowerShell כ-Administrator
    echo 2. הרץ: cd "%cd%"
    echo 3. הרץ: python -m pip install pyinstaller
    echo 4. הרץ: python -m PyInstaller --onefile --windowed --name="SHOSHI_Duplicate_Finder" duplicate_finder.py
    echo.
    if exist build_errors.txt (
        echo פרטי השגיאה נשמרו ב: build_errors.txt
    )
)

echo.
pause
