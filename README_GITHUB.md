# 🚀 Automatické vytvoření Windows EXE pomocí GitHub

## Postup (5 minut):

### 1. Vytvořte GitHub účet (pokud nemáte)
- Jděte na: https://github.com/signup
- Zaregistrujte se zdarma

### 2. Vytvořte nový repozitář
1. Přihlaste se na GitHub
2. Klikněte na "+" vpravo nahoře → "New repository"
3. Název: `databaze-barevu` (nebo jakýkoliv)
4. Nastavte jako **Public** (nebo Private, obojí funguje)
5. Klikněte "Create repository"

### 3. Nahrajte soubory
Máte 2 možnosti:

#### Možnost A: Přes webové rozhraní (jednodušší)
1. Na stránce repozitáře klikněte "uploading an existing file"
2. Přetáhněte všechny soubory z `python_project` složky
3. Klikněte "Commit changes"

#### Možnost B: Přes Git (pokud máte nainstalovaný)
```bash
cd python_project
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/VAS_UZIVATEL/databaze-barevu.git
git push -u origin main
```

### 4. Spusťte GitHub Actions
1. V repozitáři klikněte na záložku "Actions"
2. Pokud vidíte "Build Windows EXE", klikněte na něj
3. Klikněte "Run workflow" → "Run workflow"
4. Počkejte 5-10 minut (GitHub automaticky vytvoří EXE)

### 5. Stáhněte Windows EXE
1. Po dokončení (zelená fajfka ✓) klikněte na workflow run
2. Scrollujte dolů na "Artifacts"
3. Klikněte na "DatabazeBarevu-Windows"
4. Stáhne se ZIP soubor s EXE

### 6. Rozbalte a použijte
1. Rozbalte ZIP
2. Uvnitř najdete `DatabazeBarevu.exe`
3. Zkopírujte na Windows počítač
4. Dvojklik a funguje! 🎉

## 🔄 Při každé změně kódu:

1. Nahrajte změněné soubory na GitHub
2. GitHub automaticky vytvoří nový EXE
3. Stáhněte z "Actions" → "Artifacts"

## ⚠️ Poznámky:

- GitHub Actions je **zdarma** pro veřejné repozitáře
- Pro soukromé repozitáře máte 2000 minut/měsíc zdarma
- Build trvá 5-10 minut
- EXE je platný 90 dní (pak ho musíte znovu stáhnout)

## 🆘 Problémy?

### Actions se nespustily
- Zkontrolujte, že složka `.github/workflows/` je správně nahraná
- Soubor musí být: `.github/workflows/build-windows.yml`

### Build selhal
- Klikněte na červený křížek pro zobrazení chyby
- Obvykle pomůže znovu spustit workflow

### Artifact není k dispozici
- Počkejte, až build dokončí (zelená fajfka)
- Artifact je dostupný pouze 90 dní

## 📧 Alternativa: Pošlete mi soubory

Pokud nechcete používat GitHub, můžete:
1. Zabalit složku `python_project` do ZIP
2. Poslat mi ji
3. Já vytvořím Windows EXE a pošlu zpět
