# Návod na vytvoření EXE souboru

## Automatické vytvoření (doporučeno)

### Linux:
```bash
cd python_project
chmod +x build_exe.sh
./build_exe.sh
```

### Windows:
```cmd
cd python_project
build_exe.bat
```

## Ruční vytvoření

### 1. Instalace závislostí
```bash
pip install -r requirements.txt
```

### 2. Vytvoření EXE
```bash
pyinstaller --onefile --windowed --name="DatabazeBarevu" --add-data="testExport.XML:." gui.py
```

Na Windows použijte `;` místo `:` v `--add-data`:
```cmd
pyinstaller --onefile --windowed --name="DatabazeBarevu" --add-data="testExport.XML;." gui.py
```

### 3. Výsledek
EXE soubor najdete v:
- **Linux:** `dist/DatabazeBarevu`
- **Windows:** `dist\DatabazeBarevu.exe`

## Parametry PyInstaller

- `--onefile` - Vytvoří jeden EXE soubor (ne složku)
- `--windowed` - Bez konzolového okna (jen GUI)
- `--name` - Název výsledného souboru
- `--add-data` - Přibalí testExport.XML do EXE
- `--clean` - Vyčistí dočasné soubory před buildem

## Distribuce

Po vytvoření můžete distribuovat:
1. Samotný EXE soubor z `dist/` složky
2. Uživatel může načíst vlastní XML soubor přes "Načíst soubor"

## Velikost souboru

EXE bude cca 50-80 MB kvůli matplotlib a tkinter knihovnám.

## Poznámky

- EXE funguje bez instalace Pythonu
- Obsahuje všechny potřebné knihovny
- Automaticky načte testExport.XML pokud je ve stejné složce
- Antivirus může označit soubor jako podezřelý (false positive) - je to normální u PyInstaller EXE
