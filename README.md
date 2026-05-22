# 🎨 Databáze barev — Model Obaly Hostinné

![Model Group](MODEL_Logo_M.png)

Interní nástroj pro vyhledávání a správu tiskových inkoustů.  
Vyvinut pro závod **Model Obaly a.s. — Hostinné**, součást skupiny [Model Group](https://www.modelgroup.com).

**Autor:** Filip Pavelec

---

## Stažení (Windows EXE)

Nejnovější verzi stáhněte ze záložky **[Releases](../../releases)** — soubor `DatabazeBarevu.exe`.  
Nevyžaduje instalaci Pythonu ani žádných knihoven, stačí spustit.

> **Poznámka:** Windows může zobrazit varování SmartScreen.  
> Klikněte **„Další informace" → „Přesto spustit"**.

---

## Co aplikace umí

| Záložka | Popis |
|---|---|
| 🔍 **Vyhledávání podle kódu** | Zadejte kód ručně nebo naskenujte čárový kód. Zobrazí složení receptu, šarže a historii míchání. |
| 📅 **Filtrování podle data** | Zobrazí všechny recepty vytvořené v zadaném období. |
| ⚙️ **Pokročilé filtrování** | Kombinace data, času a čísla ventilu. Výsledky obsahují šarže všech složek. |

Dále:
- **Koláčový graf** složení receptu s množstvím v gramech
- **Historie míchání** — kdy a kolikrát byl recept namíchán
- **Branding** — logo Model Group, menu Nápověda → O aplikaci

---

## Spuštění ze zdrojového kódu

### Požadavky

- Python 3.9 nebo novější

```bash
pip install ttkbootstrap matplotlib
```

> Obě závislosti jsou **volitelné** — aplikace funguje i bez nich  
> (bez moderního vzhledu a bez koláčového grafu).

### Spuštění

```bash
python gui.py
```

---

## Jak používat

### 1. Načtení databáze

Klikněte **„📂 Načíst soubor"** a vyberte XML export z míchacího stroje.

### 2. Vyhledávání receptu

- Zadejte kód receptu do pole nebo naskenujte čárový kód
- Stiskněte **Enter** nebo klikněte **„🔍 Vyhledat"**
- Zobrazí se složení, šarže každé složky a historie míchání

**Formáty čárových kódů:**  
Skenery někdy posílají kódy ve formátu `315.001` nebo `315#ABC` — aplikace automaticky extrahuje čistý kód (`315`).

**Duplicitní recepty:**  
Pokud existuje více verzí receptu se stejným názvem (přepracovaný recept), zobrazí se vždy jen **nejnovější verze**.

### 3. Filtrování podle data

- Zadejte rozsah ve formátu `RRRR-MM-DD`
- Klikněte **„🔍 Filtrovat"**
- Dvojklikem na řádek zobrazíte plný detail receptu

### 4. Pokročilé filtrování

- Zadejte rozsah data a času
- Volitelně zadejte číslo ventilu — zobrazí jen recepty, které daný ventil používají
- Sloupec **Šarže** zobrazuje čísla šarží všech složek receptu

---

## Struktura XML souboru

Aplikace načítá XML export z míchacího stroje s touto strukturou:

| Element | Popis |
|---|---|
| `DBRecipe` | Recept — název, referenční množství, datum vytvoření |
| `DBLine` | Jedna složka receptu — odkaz na barvu a množství v gramech |
| `DBBaseColor` | Základní barva — název, číslo ventilu, šarže |
| `DBStatRecipe` | Záznam o namíchání — datum a čas míchání |

Datum je uloženo jako Unix timestamp v milisekundách v atributu `TIME`.

---

## Build Windows EXE

EXE se buildí automaticky přes **GitHub Actions** při každém push na `main`.

### Stažení artefaktu (bez release)

1. Záložka **Actions** → poslední úspěšný běh
2. Sekce **Artifacts** → `DatabazeBarevu-Windows`
3. Artefakt je dostupný 30 dní

### Vytvoření release (trvalé stažení)

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions automaticky vytvoří **Release** s `DatabazeBarevu.exe` ke stažení.

---

## Závislosti

| Balíček | Verze | Účel | Povinný |
|---|---|---|---|
| `ttkbootstrap` | ≥ 1.10 | Moderní vzhled UI | Ne |
| `matplotlib` | ≥ 3.5 | Koláčový graf složení | Ne |
| `pyinstaller` | ≥ 6.0 | Build Windows EXE | Jen pro build |

---

## Technické poznámky

**Výkon filtrování:**  
Při načtení souboru se jednou předpočítají lookup tabulky (slovníky ventilů a šarží pro každý recept). Pokročilé filtrování pak trvá ~20ms i pro stovky receptů — bez tabulek by trvalo ~17 sekund.

**Fonty:**  
Aplikace automaticky vybere font dostupný v systému, aby se předešlo problémům s diakritikou na různých platformách.

---

## Licence

Interní nástroj — Model Obaly a.s., závod Hostinné.  
Není určen pro veřejné šíření.

---

*Vytvořil Filip Pavelec pro Model Obaly a.s. — závod Hostinné*
