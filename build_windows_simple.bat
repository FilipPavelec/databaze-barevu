@echo off
REM ========================================
REM Jednoduchý skript pro vytvoření Windows EXE
REM Spusťte tento soubor na Windows počítači
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
pip install pyinstaller ttkbootstrap matplotlib

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
    --add-data="testExport.XML;." ^
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
