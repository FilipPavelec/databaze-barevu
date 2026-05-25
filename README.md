# Databáze barev — Model Obaly Hostinné

Interní nástroj pro vyhledávání a správu tiskových inkoustů.  
Vyvinut pro závod **Model Obaly a.s. — Hostinné**, součást skupiny [Model Group](https://www.modelgroup.com).

---

## Stažení (Windows EXE)

Nejnovější verzi stáhněte ze záložky **[Releases](../../releases)** — soubor `DatabazeBarevu.exe`.  
Nevyžaduje instalaci Pythonu ani žádných knihoven.

> Windows může zobrazit varování SmartScreen — klikněte „Další informace" → „Přesto spustit".

---

## Co aplikace umí

### Záložka — Vyhledávání podle kódu
- Zadejte kód receptu nebo naskenujte čárový kód čtečkou
- Podporovaný formát skeneru: `286.........#00012979` — aplikace vyhledá podle čísla za `#`
- Zobrazí složení receptu: čas nadávkování každé složky, číslo ventilu, šarže, hmotnost v kg
- Koláčový graf složení
- Historie míchání receptu (kdy a kolikrát byl namíchán)

### Záložka — Filtrování podle data
- Výběr data kliknutím z kalendáře
- Zobrazí seznam receptů vytvořených v daném období
- Dvojklik na řádek = přehledný detail receptu

### Záložka — Pokročilé filtrování
- Filtr podle rozsahu data a času
- Filtr podle čísla ventilu
- Filtr podle názvu nebo čísla barvy (např. „48", „Blue 17", „Transparent")
- Dvojklik na řádek = přehledný detail receptu

### Export výsledků
- Tlačítko „Export" v záložce Vyhledávání i Pokročilé filtrování
- Formáty: **TXT**, **CSV** (pro Excel), **PDF** (s českou diakritikou)

---

## Spuštění ze zdrojového kódu

### Požadavky
- Python 3.9 nebo novější

### Instalace závislostí
```bash
pip install ttkbootstrap matplotlib tkcalendar reportlab
```

Všechny závislosti jsou volitelné — aplikace funguje i bez nich (bez moderního vzhledu, bez grafu, bez kalendáře, bez PDF exportu).

### Spuštění
```bash
python gui.py
```

---

## Jak používat

### Načtení databáze
Klikněte „Načíst soubor" a vyberte XML export z míchacího stroje.

### Vyhledávání receptu
- Zadejte kód nebo naskenujte čárový kód → Enter nebo „Vyhledat"
- Formát `286.........#00012979` → vyhledá míchání `#12979` a zobrazí skutečné složení s časy nadávkování

### Filtrování
- Kliknutím na pole data se otevře kalendář
- Výsledky v tabulce — dvojklik = detail

### Export
- Klikněte „Export" → vyberte formát (TXT / CSV / PDF)
- PDF používá font DejaVuSans — plná podpora české diakritiky

---

## Build Windows EXE

EXE se sestavuje automaticky přes GitHub Actions při každém push na `main`.

```bash
# Stažení jako artefakt (30 dní)
# Actions → poslední běh → Artifacts → DatabazeBarevu-Windows

# Vytvoření trvalého Release
git tag v1.0.0
git push origin v1.0.0
```

Podrobnosti viz `BUILD_WINDOWS.md` a `README_GITHUB.md`.

---

## Závislosti

| Balíček | Verze | Účel | Povinný |
|---|---|---|---|
| `ttkbootstrap` | ≥ 1.10 | Moderní vzhled UI | Ne |
| `matplotlib` | ≥ 3.5 | Koláčový graf | Ne |
| `tkcalendar` | ≥ 1.6 | Kalendář pro výběr data | Ne |
| `reportlab` | ≥ 4.0 | PDF export s diakritikou | Ne |
| `pyinstaller` | ≥ 6.0 | Build EXE | Jen pro build |

---

## Struktura XML souboru

| Element | Popis |
|---|---|
| `DBRecipe` | Recept — název, referenční množství, datum vytvoření |
| `DBLine` | Složka receptu — odkaz na barvu a referenční množství |
| `DBBaseColor` | Základní barva — název, číslo ventilu, šarže |
| `DBStatRecipe` | Záznam o namíchání — datum a čas míchání |
| `DBStatLine` | Skutečné složení míchání — čas nadávkování, skutečná hmotnost, šarže |

---

## Technické poznámky

**Výkon filtrování:**  
Při načtení souboru se předpočítají lookup tabulky (ventily, šarže, barvy, složení pro každý recept). Pokročilé filtrování pak trvá ~20ms i pro stovky receptů.

**PDF export:**  
Používá font DejaVuSans přibalený ve složce `fonts/` — plná podpora české diakritiky na všech platformách včetně Windows EXE.

---

*Vytvořil Filip Pavelec pro Model Obaly a.s. — závod Hostinné*
