# 🪟 Jak vytvořit Windows EXE - Krok za krokem

## 📋 Co potřebujete:
- Windows počítač (Windows 10 nebo 11)
- Připojení k internetu
- 10 minut času

## 🚀 Postup (velmi jednoduchý):

### Krok 1: Zkopírujte složku na Windows
Zkopírujte celou složku `python_project` na váš Windows počítač (např. na plochu).

### Krok 2: Nainstalujte Python (pokud nemáte)
1. Jděte na: https://www.python.org/downloads/
2. Stáhněte nejnovější Python (3.11 nebo novější)
3. Spusťte instalátor
4. ⚠️ **DŮLEŽITÉ:** Zaškrtněte "Add Python to PATH"
5. Klikněte "Install Now"

### Krok 3: Vytvořte EXE
1. Otevřete složku `python_project` na Windows
2. **Dvojklik** na soubor `build_windows_simple.bat`
3. Počkejte 2-5 minut (automaticky nainstaluje vše potřebné)
4. Hotovo! 🎉

### Krok 4: Najděte EXE
Po dokončení se automaticky otevře složka `dist` s vaším EXE souborem:
- **Soubor:** `DatabazeBarevu.exe`
- **Velikost:** cca 60-80 MB

## ✅ Použití EXE:

### Na jakémkoliv Windows počítači:
1. Zkopírujte `DatabazeBarevu.exe` kamkoliv
2. Dvojklik na EXE
3. Aplikace se spustí!

### S vlastní databází:
- Dejte `testExport.XML` do stejné složky jako EXE (automaticky se načte)
- Nebo použijte tlačítko "📂 Načíst soubor" v aplikaci

## ⚠️ Windows Defender varování

Při prvním spuštění může Windows Defender zobrazit varování:
```
Windows chránil váš počítač
```

**To je normální!** PyInstaller EXE jsou často označeny jako podezřelé.

### Jak spustit:
1. Klikněte "Další informace"
2. Klikněte "Přesto spustit"

### Nebo přidejte výjimku:
1. Otevřete Windows Security
2. Virus & threat protection
3. Manage settings
4. Add or remove exclusions
5. Přidejte složku s EXE

## 🎨 Co aplikace umí:

### Záložka 1: Vyhledávání podle kódu
- Naskenujte čárový kód čtečkou
- Nebo zadejte kód ručně
- Zobrazí recept s grafem složení

### Záložka 2: Filtrování podle data
- Zadejte rozsah dat
- Zobrazí seznam receptů
- Dvojklik pro detail

### Záložka 3: Pokročilé filtrování
- Filtr podle data a času
- Filtr podle čísla ventilu
- Kombinace filtrů

## 🆘 Problémy?

### Python není nainstalován
```
'python' is not recognized as an internal or external command
```
**Řešení:** Nainstalujte Python a zaškrtněte "Add Python to PATH"

### Chyba při buildu
**Řešení:** Zkuste znovu spustit `build_windows_simple.bat`

### EXE se nespustí
**Řešení:** 
1. Zkontrolujte Windows Defender
2. Zkuste spustit jako administrátor (pravý klik → "Run as administrator")

## 📞 Kontakt

Pokud máte problémy, pošlete screenshot chyby.
