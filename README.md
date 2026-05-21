# Databáze barev - Vyhledávání

Aplikace pro vyhledávání receptů barev v XML databázi s podporou čtečky čárových kódů.

## Funkce

- GUI i CLI rozhraní
- Podpora čtečky čárových kódů
- Vyhledávání receptů podle kódu
- Zobrazení složení receptu (barvy a množství)
- Filtrování podle data
- Automatické zpracování čárových kódů

## Spuštění

### GUI verze (doporučeno):
```bash
cd python_project
python gui.py
```

### CLI verze:
```bash
cd python_project
python main.py testExport.XML
```

## Použití GUI

1. Aplikace automaticky načte `testExport.XML` pokud existuje
2. Nebo klikněte na "Načíst soubor" pro výběr jiného XML souboru
3. Naskenujte čárový kód nebo zadejte kód ručně
4. Stiskněte Enter nebo klikněte "Vyhledat"
5. Zobrazí se recept s kompletním složením

## Formát čárového kódu

Aplikace podporuje různé formáty:
- `315` - přímý kód
- `641.........#00012821` - kód s tečkami a #
- `315#00012745` - kód s #

Automaticky extrahuje relevantní část (číslo před tečkami).

## Výstup

Pro každý recept zobrazí:
- Název receptu
- PK (primární klíč)
- Celkové množství v gramech
- Datum vytvoření
- Seznam základních barev s:
  - Název barvy
  - Číslo ventilu
  - Množství v gramech
- Celkový součet

## Požadavky

- Python 3.6+
- tkinter (součástí standardní instalace Pythonu)
- Žádné další závislosti