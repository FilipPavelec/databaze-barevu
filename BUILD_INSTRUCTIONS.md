# Návod na vytvoření EXE souboru

## Automatické vytvoření (doporučeno)

### Windows — pomocí skriptu:
```cmd
build_windows_simple.bat
```

### Linux — pomocí skriptu:
```bash
chmod +x build_exe.sh
./build_exe.sh
```

---

## Ruční vytvoření

### 1. Instalace závislostí
```bash
pip install -r requirements.txt
```

### 2. Vytvoření EXE na Windows
```cmd
pyinstaller --onefile --windowed --name="DatabazeBarevu" ^
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
    --collect-all=tkcalendar ^
    --collect-all=reportlab ^
    --clean gui.py
```

### 3. Výsledek
EXE soubor najdete v `dist\DatabazeBarevu.exe`

---

## Závislosti

| Balíček | Verze | Účel |
|---|---|---|
| `ttkbootstrap` | ≥ 1.10 | Moderní vzhled UI |
| `matplotlib` | ≥ 3.5 | Koláčový graf složení |
| `tkcalendar` | ≥ 1.6 | Kalendář pro výběr data |
| `reportlab` | ≥ 4.0 | Export do PDF s diakritikou |
| `pyinstaller` | ≥ 6.0 | Build EXE |

Všechny závislosti jsou volitelné — aplikace funguje i bez nich (bez grafu, bez kalendáře, bez PDF exportu).

---

## Parametry PyInstaller

| Parametr | Účel |
|---|---|
| `--onefile` | Jeden EXE soubor |
| `--windowed` | Bez konzolového okna |
| `--add-data "fonts/...;fonts"` | Přibalí fonty pro PDF export |
| `--collect-all=tkcalendar` | Zabalí všechny soubory tkcalendar (locale atd.) |
| `--collect-all=reportlab` | Zabalí všechny soubory reportlab |
| `--hidden-import=babel.numbers` | Potřebné pro tkcalendar |
| `--clean` | Vyčistí dočasné soubory |

---

## Velikost EXE

Cca 80–120 MB kvůli matplotlib, tkcalendar a reportlab.

---

## Poznámky

- EXE funguje bez instalace Pythonu
- Windows Defender může označit soubor jako podezřelý — klikněte „Další informace" → „Přesto spustit"
