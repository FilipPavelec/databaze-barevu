#!/bin/bash
# Skript pro vytvoření EXE souboru

echo "======================================"
echo "Vytváření EXE souboru..."
echo "======================================"

# Kontrola, zda je nainstalován PyInstaller
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller není nainstalován. Instaluji..."
    pip install pyinstaller
fi

# Vytvořit EXE soubor
pyinstaller --onefile \
    --windowed \
    --name="DatabazeBarevu" \
    --add-data="testExport.XML:." \
    --icon=NONE \
    --clean \
    gui.py

echo ""
echo "======================================"
echo "Hotovo!"
echo "======================================"
echo "EXE soubor najdete v: dist/DatabazeBarevu"
echo ""
