# Automatické vytvoření Windows EXE pomocí GitHub Actions

## Jak to funguje

Při každém push na větev `main` GitHub automaticky sestaví `DatabazeBarevu.exe` na Windows serveru. Stačí stáhnout hotový soubor.

---

## Stažení EXE (nejrychlejší způsob)

1. Záložka **Actions** v repozitáři
2. Klikněte na poslední úspěšný běh (zelená fajfka ✓)
3. Sekce **Artifacts** → klikněte `DatabazeBarevu-Windows`
4. Rozbalte ZIP → uvnitř je `DatabazeBarevu.exe`

Artefakt je dostupný 30 dní od buildu.

---

## Trvalé stažení přes Release

Pro trvalý odkaz ke stažení vytvořte Release pomocí tagu:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions automaticky vytvoří Release a přiloží EXE. Stáhnout lze ze záložky **Releases**.

---

## Ruční spuštění buildu

1. Záložka **Actions**
2. Vlevo klikněte „Build Windows EXE"
3. Tlačítko **Run workflow** → **Run workflow**
4. Počkejte 5–10 minut

---

## Co EXE obsahuje

Všechny závislosti jsou zabaleny přímo v EXE — na cílovém počítači není potřeba nic instalovat.

| Knihovna | Funkce |
|---|---|
| `ttkbootstrap` | Moderní vzhled |
| `matplotlib` | Koláčový graf složení |
| `tkcalendar` | Výběr data kliknutím z kalendáře |
| `reportlab` + DejaVuSans | Export do PDF s českou diakritikou |

---

## Při každé změně kódu

Push na `main` → GitHub automaticky spustí nový build → stáhněte nový artefakt.

---

## Časté problémy

**Build selhal (červený křížek)**
Klikněte na běh → zobrazí se log s chybou. Nejčastěji pomůže znovu spustit workflow.

**Artifact není vidět**
Počkejte až build dokončí — artefakt se objeví až po úspěšném dokončení.

**Složka `.github/workflows/` chybí**
Ujistěte se, že je soubor `.github/workflows/build-windows.yml` správně nahrán do repozitáře.
