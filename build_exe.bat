@echo off
REM Skript pro vytvoření EXE souboru na Windows

echo ======================================
echo Vytváření EXE souboru...
echo ======================================

REM Kontrola, zda je nainstalován PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller není nainstalován. Instaluji...
    pip install pyinstaller
)

REM Vytvořit EXE soubor
pyinstaller --onefile ^
    --windowed ^
    --name=DatabazeBarevu ^
    --add-data="testExport.XML;." ^
    --clean ^
    gui.py

echo.
echo ======================================
echo Hotovo!
echo ======================================
echo EXE soubor najdete v: dist\DatabazeBarevu.exe
echo.
pause
