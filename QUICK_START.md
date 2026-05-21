# ⚡ Rychlý start - Vytvoření Windows EXE

## 🎯 Máte 2 možnosti:

---

## ✅ Možnost 1: GitHub Actions (DOPORUČENO - bez Windows PC)

### Co potřebujete:
- GitHub účet (zdarma)
- 10 minut času

### Postup:
1. **Vytvořte GitHub repozitář** na https://github.com/new
2. **Nahrajte všechny soubory** z této složky
3. **Jděte do "Actions"** záložky
4. **Klikněte "Run workflow"**
5. **Počkejte 5-10 minut**
6. **Stáhněte EXE** z "Artifacts"

📖 **Detailní návod:** Viz `README_GITHUB.md`

---

## ✅ Možnost 2: Windows počítač (když máte přístup)

### Co potřebujete:
- Windows 10/11
- Python 3.11+ (https://www.python.org/downloads/)

### Postup:
1. **Zkopírujte tuto složku** na Windows
2. **Dvojklik** na `build_windows_simple.bat`
3. **Počkejte 2-5 minut**
4. **Hotovo!** EXE je v `dist\DatabazeBarevu.exe`

📖 **Detailní návod:** Viz `WINDOWS_INSTRUKCE.md`

---

## 🎉 Výsledek:

Po dokončení získáte:
- **Soubor:** `DatabazeBarevu.exe` (60-80 MB)
- **Funguje na:** Jakémkoliv Windows 10/11
- **Bez instalace:** Stačí dvojklik
- **Obsahuje:** Moderní GUI, grafy, čtečka čárových kódů

---

## 🚀 Použití EXE na Windows:

1. Zkopírujte `DatabazeBarevu.exe` kamkoliv
2. (Volitelně) Dejte `testExport.XML` do stejné složky
3. Dvojklik na EXE
4. Aplikace se spustí s moderním GUI
5. Naskenujte čárový kód nebo použijte filtry

---

## ⚠️ První spuštění na Windows:

Windows Defender může zobrazit varování:
```
Windows chránil váš počítač
```

**To je normální!** Klikněte:
1. "Další informace"
2. "Přesto spustit"

---

## 📞 Potřebujete pomoc?

- **GitHub Actions:** Viz `README_GITHUB.md`
- **Windows build:** Viz `WINDOWS_INSTRUKCE.md`
- **Technické detaily:** Viz `BUILD_WINDOWS.md`
