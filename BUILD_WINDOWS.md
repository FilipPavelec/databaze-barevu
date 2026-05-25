# Vytvoření Windows EXE

## Možnost 1 — Windows počítač (nejjednodušší)

1. Zkopírujte celou složku projektu na Windows
2. Nainstalujte Python 3.11+ z https://www.python.org/downloads/ (zaškrtněte „Add Python to PATH")
3. Dvojklik na `build_windows_simple.bat`
4. EXE najdete v `dist\DatabazeBarevu.exe`

Nebo ručně v příkazovém řádku:
```cmd
pip install pyinstaller ttkbootstrap matplotlib tkcalendar reportlab
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

---

## Možnost 2 — GitHub Actions (automatické, bez Windows PC)

Při každém push na větev `main` GitHub automaticky sestaví EXE.

**Stažení artefaktu:**
1. Záložka **Actions** na GitHubu
2. Klikněte na poslední úspěšný běh
3. Sekce **Artifacts** → stáhněte `DatabazeBarevu-Windows`
4. Artefakt je dostupný 30 dní

**Vytvoření trvalého Release:**
```bash
git tag v1.0.0
git push origin v1.0.0
```
GitHub Actions automaticky vytvoří Release s EXE ke stažení.

---

## Výsledný EXE

- Velikost: cca 80–120 MB
- Funguje na Windows 10 a 11 bez instalace čehokoliv
- Obsahuje: Python runtime, všechny knihovny, fonty pro PDF export

## Obsah EXE

| Soubor/knihovna | Účel |
|---|---|
| `ttkbootstrap` | Moderní vzhled |
| `matplotlib` | Koláčový graf |
| `tkcalendar` | Kalendář pro výběr data |
| `reportlab` | PDF export s českou diakritikou |
| `fonts/DejaVuSans.ttf` | Font pro PDF (diakritika) |
| `MODEL_Logo_M.png` | Logo v aplikaci |

## Poznámky

- Windows Defender může označit EXE jako podezřelý — to je normální u PyInstaller souborů
- Klikněte „Další informace" → „Přesto spustit"
