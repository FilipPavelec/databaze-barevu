# Jak vytvořit Windows EXE — krok za krokem

## Co potřebujete
- Windows 10 nebo 11
- Připojení k internetu
- 10 minut času

---

## Postup

### Krok 1 — Nainstalujte Python (pokud nemáte)
1. Jděte na https://www.python.org/downloads/
2. Stáhněte Python 3.11 nebo novější
3. Spusťte instalátor
4. **DŮLEŽITÉ:** Zaškrtněte „Add Python to PATH"
5. Klikněte „Install Now"

### Krok 2 — Spusťte build skript
1. Otevřete složku projektu na Windows
2. Dvojklik na soubor `build_windows_simple.bat`
3. Počkejte 3–7 minut (skript automaticky nainstaluje vše potřebné)
4. Po dokončení se otevře složka `dist` s EXE souborem

### Krok 3 — Hotovo
Soubor `dist\DatabazeBarevu.exe` je připraven k použití.

---

## Co skript nainstaluje automaticky

| Balíček | Účel |
|---|---|
| `pyinstaller` | Vytvoření EXE |
| `ttkbootstrap` | Moderní vzhled aplikace |
| `matplotlib` | Koláčový graf složení |
| `tkcalendar` | Výběr data kliknutím (kalendář) |
| `reportlab` | Export do PDF s českou diakritikou |

---

## Použití EXE na Windows

1. Zkopírujte `DatabazeBarevu.exe` kamkoliv
2. Dvojklik — aplikace se spustí bez instalace čehokoliv
3. Klikněte „Načíst soubor" a vyberte XML export z míchacího stroje

---

## Co aplikace umí

**Záložka Vyhledávání podle kódu**
- Zadejte kód receptu nebo naskenujte čárový kód čtečkou
- Formát skeneru `286.........#00012979` — aplikace automaticky vyhledá podle čísla za `#`
- Zobrazí složení s časy nadávkování, ventily, šaržemi a hmotností v kg
- Koláčový graf složení
- Historie míchání receptu

**Záložka Filtrování podle data**
- Kliknutím na pole vyberte datum z kalendáře
- Zobrazí seznam receptů v daném období
- Dvojklik na řádek = detail receptu

**Záložka Pokročilé filtrování**
- Filtr podle data a času
- Filtr podle čísla ventilu
- Filtr podle názvu nebo čísla barvy (např. „48", „Blue 17", „Transparent")
- Dvojklik na řádek = detail receptu

**Export výsledků**
- Tlačítko „Export" v záložce Vyhledávání i Pokročilé filtrování
- Formáty: TXT, CSV (pro Excel), PDF (s českou diakritikou)

---

## Varování Windows Defenderu

Při prvním spuštění může Windows zobrazit:
```
Windows chránil váš počítač
```

To je normální u PyInstaller EXE. Postup:
1. Klikněte „Další informace"
2. Klikněte „Přesto spustit"

---

## Časté problémy

**„Python není rozpoznán jako příkaz"**
Řešení: Přeinstalujte Python a zaškrtněte „Add Python to PATH"

**Build selže s chybou**
Řešení: Spusťte `build_windows_simple.bat` znovu — někdy pomůže druhý pokus

**EXE se nespustí**
Řešení: Zkuste pravý klik → „Spustit jako správce"
