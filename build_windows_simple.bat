@echo off
REM ========================================
REM Skript pro vytvoreni Windows EXE
REM Spustte tento soubor na Windows pocitaci
REM ========================================

echo.
echo ========================================
echo Databaze Barevu - Windows Build
echo ========================================
echo.

REM Kontrola Pythonu
python --version >nul 2>&1
if errorlevel 1 (
    echo [CHYBA] Python neni nainstalovan!
    echo.
    echo Prosim nainstalujte Python z:
    echo https://www.python.org/downloads/
    echo.
    echo Pri instalaci zatrhnete "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python nalezen
echo.

REM Instalace zavislosti
echo Instaluji zavislosti...
echo.
python -m pip install --upgrade pip
pip install pyinstaller ttkbootstrap matplotlib tkcalendar reportlab

if errorlevel 1 (
    echo.
    echo [CHYBA] Instalace zavislosti selhala!
    pause
    exit /b 1
)

echo.
echo [OK] Zavislosti nainstalovany
echo.

REM Vytvoreni EXE
echo Vytvarim Windows EXE...
echo (Muze to trvat 2-5 minut)
echo.

pyinstaller --onefile ^
    --windowed ^
    --name="DatabazeBarevu" ^
    --icon="model_logo.ico" ^
    --add-data="model_logo.ico;." ^
    --add-data="MODEL_Logo_M.png;." ^
    --add-data="fonts/DejaVuSans.ttf;fonts" ^
    --add-data="fonts/DejaVuSans-Bold.ttf;fonts" ^
    --hidden-import=ttkbootstrap ^
    --hidden-import=matplotlib ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=tkcalendar ^
    --hidden-import=babel.numbers ^
    --hidden-import=reportlab ^
    --hidden-import=reportlab.platypus ^
    --hidden-import=reportlab.lib.pagesizes ^
    --hidden-import=reportlab.lib.styles ^
    --hidden-import=reportlab.lib.units ^
    --hidden-import=reportlab.lib.colors ^
    --collect-all=tkcalendar ^
    --collect-all=reportlab ^
    --clean ^
    gui.py

if errorlevel 1 (
    echo.
    echo [CHYBA] Vytvoreni EXE selhalo!
    pause
    exit /b 1
)

echo.
echo ========================================
echo [USPECH] Windows EXE vytvoreno!
echo ========================================
echo.
echo Soubor: dist\DatabazeBarevu.exe
echo.
echo Muzete ho zkopirovat kamkoliv a spustit
echo bez instalace Pythonu nebo jinych zavislosti.
echo.

REM Otevrit slozku s EXE
explorer dist

pause
