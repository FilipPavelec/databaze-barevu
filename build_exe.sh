#!/bin/bash
# Skript pro vytvoření EXE souboru na Linuxu

echo "======================================"
echo "Databaze Barevu - Linux Build"
echo "======================================"

# Kontrola Pythonu
if ! command -v python3 &> /dev/null; then
    echo "[CHYBA] Python3 neni nainstalovan!"
    exit 1
fi

# Instalace zavislosti
echo "Instaluji zavislosti..."
pip install pyinstaller ttkbootstrap matplotlib tkcalendar reportlab

# Vytvoreni EXE
echo "Vytvarim EXE..."
pyinstaller --onefile \
    --windowed \
    --name="DatabazeBarevu" \
    --add-data="model_logo.ico:." \
    --add-data="MODEL_Logo_M.png:." \
    --add-data="fonts/DejaVuSans.ttf:fonts" \
    --add-data="fonts/DejaVuSans-Bold.ttf:fonts" \
    --hidden-import=ttkbootstrap \
    --hidden-import=matplotlib \
    --hidden-import=matplotlib.backends.backend_tkagg \
    --hidden-import=tkcalendar \
    --hidden-import=babel.numbers \
    --hidden-import=reportlab \
    --collect-all=tkcalendar \
    --collect-all=reportlab \
    --clean \
    gui.py

echo ""
echo "======================================"
echo "Hotovo! EXE: dist/DatabazeBarevu"
echo "======================================"
