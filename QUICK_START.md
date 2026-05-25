# Rychlý start

## Možnost 1 — GitHub Actions (doporučeno, bez Windows PC)

1. Push na větev `main` → GitHub automaticky sestaví EXE
2. Záložka **Actions** → poslední běh → **Artifacts** → stáhnout `DatabazeBarevu-Windows`

Pro trvalý Release (záložka Releases):
```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## Možnost 2 — Windows počítač

1. Nainstalujte Python 3.11+ (zaškrtněte „Add Python to PATH")
2. Dvojklik na `build_windows_simple.bat`
3. EXE je v `dist\DatabazeBarevu.exe`

---

## Spuštění ze zdrojového kódu

```bash
pip install ttkbootstrap matplotlib tkcalendar reportlab
python gui.py
```

---

## Co aplikace umí

- Vyhledávání receptu podle kódu nebo čárového kódu (formát `286.....#00012979`)
- Filtrování podle data — výběr kliknutím z kalendáře
- Pokročilé filtrování podle data, ventilu a barvy
- Detail složení: čas nadávkování, ventil, šarže, hmotnost v kg
- Koláčový graf složení
- Export výsledků do TXT, CSV nebo PDF (s českou diakritikou)

---

## Varování Windows Defenderu

Při prvním spuštění EXE klikněte „Další informace" → „Přesto spustit".  
Je to normální u PyInstaller souborů.
