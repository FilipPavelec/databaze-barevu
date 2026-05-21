# Vytvoření Windows EXE

## Problém
Na Linuxu nelze přímo vytvořit Windows EXE soubor. Existují 3 možnosti:

## ✅ Možnost 1: Použít Windows počítač (nejjednodušší)

### Kroky:
1. Zkopírujte celou složku `python_project` na Windows počítač
2. Nainstalujte Python 3.11+ z https://www.python.org/downloads/
3. Otevřete Command Prompt (cmd) ve složce `python_project`
4. Spusťte:
```cmd
pip install pyinstaller ttkbootstrap matplotlib
pyinstaller --onefile --windowed --name="DatabazeBarevu" --add-data="testExport.XML;." --clean gui.py
```
5. EXE najdete v `dist\DatabazeBarevu.exe`

## ✅ Možnost 2: GitHub Actions (automatické)

### Kroky:
1. Vytvořte GitHub repozitář
2. Nahrajte složku `python_project` do repozitáře
3. GitHub automaticky vytvoří Windows EXE pomocí workflow
4. Stáhněte EXE z "Actions" záložky

Workflow soubor je již připraven v `.github/workflows/build-windows.yml`

## ✅ Možnost 3: Wine na Linuxu (pokročilé)

### Instalace Wine a Python pro Windows:
```bash
# Nainstalovat Wine
sudo apt install wine64 winetricks

# Stáhnout Python pro Windows
wget https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe

# Nainstalovat Python ve Wine
wine python-3.11.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

# Nainstalovat závislosti
wine python -m pip install pyinstaller ttkbootstrap matplotlib

# Vytvořit EXE
cd python_project
wine pyinstaller --onefile --windowed --name="DatabazeBarevu" --add-data="testExport.XML;." --clean gui.py
```

## 📦 Výsledek

Po úspěšném buildu získáte:
- **Soubor:** `DatabazeBarevu.exe`
- **Velikost:** cca 60-80 MB
- **Požadavky:** Žádné! Funguje na jakémkoliv Windows 10/11 bez instalace

## 🚀 Použití na Windows

1. Zkopírujte `DatabazeBarevu.exe` kamkoliv
2. Dvojklik na EXE
3. Aplikace se spustí s moderním GUI
4. Automaticky načte `testExport.XML` pokud je ve stejné složce
5. Nebo použijte tlačítko "Načíst soubor" pro jiný XML

## ⚠️ Poznámky

- Windows Defender může označit EXE jako podezřelý (false positive)
- To je normální u PyInstaller EXE souborů
- Klikněte "Další informace" → "Přesto spustit"
- Nebo přidejte výjimku do Windows Defenderu
