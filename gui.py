#!/usr/bin/env python3
"""
GUI pro vyhledávání v XML databázi barev - Moderní verze
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
from datetime import datetime
import os

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    from tkinter import ttk
    TTKBOOTSTRAP_AVAILABLE = False
    print("Upozornění: ttkbootstrap není nainstalován. Použije se standardní vzhled.")
    print("Pro moderní vzhled nainstalujte: pip install ttkbootstrap")

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Upozornění: matplotlib není nainstalován. Grafy nebudou dostupné.")
    print("Nainstalujte: pip install matplotlib")


class ColorDatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Databáze barev - Vyhledávání")
        self.root.geometry("1100x750")
        
        # Nastavit minimální velikost
        self.root.minsize(900, 600)
        
        self.db = None
        self.xml_file = None
        
        self.setup_ui()
        
        # Automaticky načíst testExport.XML pokud existuje
        default_file = "testExport.XML"
        if os.path.exists(default_file):
            self.load_database(default_file)
    
    def setup_ui(self):
        """Vytvořit uživatelské rozhraní."""
        # Horní panel - načtení souboru s moderním designem
        top_frame = ttk.Frame(self.root, padding="15")
        top_frame.pack(fill=tk.X)
        
        # Ikona a název souboru
        file_info_frame = ttk.Frame(top_frame)
        file_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(file_info_frame, text="📁", font=("Arial", 16)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(file_info_frame, text="XML soubor:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(file_info_frame, text="Žádný soubor", foreground="gray", font=("Arial", 10))
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        # Tlačítko načíst s ikonou
        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(top_frame, text="📂 Načíst soubor", command=self.browse_file, bootstyle="primary").pack(side=tk.RIGHT, padx=5)
        else:
            ttk.Button(top_frame, text="📂 Načíst soubor", command=self.browse_file).pack(side=tk.RIGHT, padx=5)
        
        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)
        
        # Notebook pro záložky
        if TTKBOOTSTRAP_AVAILABLE:
            self.notebook = ttk.Notebook(self.root, bootstyle="primary")
        else:
            self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Záložka 1: Vyhledávání podle kódu
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="🔍 Vyhledávání podle kódu")
        self.setup_search_tab()
        
        # Záložka 2: Filtrování podle data
        self.date_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.date_tab, text="📅 Filtrování podle data")
        self.setup_date_tab()
        
        # Záložka 3: Pokročilé filtrování
        self.advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_tab, text="⚙️ Pokročilé filtrování")
        self.setup_advanced_tab()
        
        # Stavový řádek s moderním designem
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        if TTKBOOTSTRAP_AVAILABLE:
            self.status_bar = ttk.Label(status_frame, text="✓ Připraveno", relief=tk.FLAT, anchor=tk.W, 
                                       padding="5", bootstyle="inverse-secondary")
        else:
            self.status_bar = ttk.Label(status_frame, text="✓ Připraveno", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X)
    
    def setup_search_tab(self):
        """Nastavit záložku vyhledávání."""
        # Hlavní panel - vyhledávání s kartou
        search_frame = ttk.LabelFrame(self.search_tab, text="🔎 Vyhledávání receptu")
        search_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Vnitřní padding frame
        inner_frame = ttk.Frame(search_frame, padding=15)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Vstupní pole pro skener/ručně
        input_frame = ttk.Frame(inner_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Naskenujte čárový kód nebo zadejte kód:", 
                 font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Entry s větším fontem a padding
        entry_container = ttk.Frame(input_frame)
        entry_container.pack(fill=tk.X, pady=5)
        
        self.search_entry = ttk.Entry(entry_container, font=("Arial", 16))
        self.search_entry.pack(fill=tk.X, ipady=8)
        self.search_entry.bind('<Return>', lambda e: self.search_barcode())
        
        # Tlačítka s ikonami
        button_frame = ttk.Frame(inner_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="🔍 Vyhledat", command=self.search_barcode, 
                      bootstyle="success", width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_search, 
                      bootstyle="secondary", width=15).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="🔍 Vyhledat", command=self.search_barcode).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Panel výsledků s grafem
        result_container = ttk.Frame(self.search_tab)
        result_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Levá strana - text
        left_frame = ttk.LabelFrame(result_container, text="📋 Detail receptu")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        left_inner = ttk.Frame(left_frame, padding=10)
        left_inner.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(
            left_inner,
            wrap=tk.WORD,
            font=("Consolas", 10),
            width=50,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Pravá strana - graf
        if MATPLOTLIB_AVAILABLE:
            right_frame = ttk.LabelFrame(result_container, text="📊 Graf složení")
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
            
            right_inner = ttk.Frame(right_frame, padding=10)
            right_inner.pack(fill=tk.BOTH, expand=True)
            
            self.figure = Figure(figsize=(5, 6), dpi=100)
            self.figure.patch.set_facecolor('#f8f9fa')
            self.canvas = FigureCanvasTkAgg(self.figure, right_inner)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_date_tab(self):
        """Nastavit záložku filtrování podle data."""
        # Panel pro zadání dat
        input_frame = ttk.LabelFrame(self.date_tab, text="📅 Zadejte rozsah dat")
        input_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Vnitřní padding
        inner_input = ttk.Frame(input_frame, padding=15)
        inner_input.pack(fill=tk.BOTH, expand=True)
        
        # Grid layout pro lepší zarovnání
        inner_input.columnconfigure(1, weight=1)
        
        # Počáteční datum
        ttk.Label(inner_input, text="Od (RRRR-MM-DD):", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.start_date_entry = ttk.Entry(inner_input, font=("Arial", 11), width=20)
        self.start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=8)
        self.start_date_entry.insert(0, "2020-01-01")
        
        # Koncové datum
        ttk.Label(inner_input, text="Do (RRRR-MM-DD):", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.end_date_entry = ttk.Entry(inner_input, font=("Arial", 11), width=20)
        self.end_date_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=8)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Tlačítka
        button_frame = ttk.Frame(inner_input)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W, padx=5)
        
        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="🔍 Filtrovat", command=self.filter_by_date, 
                      bootstyle="success", width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_date_filter, 
                      bootstyle="secondary", width=15).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="🔍 Filtrovat", command=self.filter_by_date).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_date_filter).pack(side=tk.LEFT, padx=5)
        
        # Panel výsledků
        result_frame = ttk.LabelFrame(self.date_tab, text="📊 Výsledky")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Vnitřní padding
        inner_result = ttk.Frame(result_frame, padding=10)
        inner_result.pack(fill=tk.BOTH, expand=True)
        
        # Treeview pro zobrazení seznamu
        columns = ("PK", "Název", "Množství", "Datum")
        
        if TTKBOOTSTRAP_AVAILABLE:
            self.date_tree = ttk.Treeview(inner_result, columns=columns, show="headings", 
                                         height=15, bootstyle="primary")
        else:
            self.date_tree = ttk.Treeview(inner_result, columns=columns, show="headings", height=15)
        
        self.date_tree.heading("PK", text="PK")
        self.date_tree.heading("Název", text="Název")
        self.date_tree.heading("Množství", text="Množství (g)")
        self.date_tree.heading("Datum", text="Datum")
        
        self.date_tree.column("PK", width=80, anchor=tk.CENTER)
        self.date_tree.column("Název", width=250)
        self.date_tree.column("Množství", width=120, anchor=tk.E)
        self.date_tree.column("Datum", width=180, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(inner_result, orient=tk.VERTICAL, command=self.date_tree.yview)
        self.date_tree.configure(yscroll=scrollbar.set)
        
        self.date_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Dvojklik pro zobrazení detailu
        self.date_tree.bind('<Double-1>', self.show_recipe_detail)
        
        # Hint
        hint_label = ttk.Label(result_frame, text="💡 Tip: Dvojklikem na recept zobrazíte detail", 
                              font=("Arial", 9, "italic"), foreground="gray")
        hint_label.pack(pady=5)
    
    def setup_advanced_tab(self):
        """Nastavit záložku pokročilého filtrování."""
        # Panel pro filtry
        filter_frame = ttk.LabelFrame(self.advanced_tab, text="⚙️ Filtry")
        filter_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Vnitřní padding
        inner_filter = ttk.Frame(filter_frame, padding=15)
        inner_filter.pack(fill=tk.BOTH, expand=True)
        
        # Grid layout
        inner_filter.columnconfigure(1, weight=1)
        
        # Filtr podle data a času
        ttk.Label(inner_filter, text="📅 Datum od:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_start_date = ttk.Entry(inner_filter, font=("Arial", 10), width=15)
        self.adv_start_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_start_date.insert(0, "2020-01-01")
        
        ttk.Label(inner_filter, text="📅 Datum do:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_end_date = ttk.Entry(inner_filter, font=("Arial", 10), width=15)
        self.adv_end_date.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Filtr podle času
        ttk.Label(inner_filter, text="🕐 Čas od (HH:MM):", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_start_time = ttk.Entry(inner_filter, font=("Arial", 10), width=10)
        self.adv_start_time.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_start_time.insert(0, "00:00")
        
        ttk.Label(inner_filter, text="🕐 Čas do (HH:MM):", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_end_time = ttk.Entry(inner_filter, font=("Arial", 10), width=10)
        self.adv_end_time.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_end_time.insert(0, "23:59")
        
        # Filtr podle ventilu
        ttk.Label(inner_filter, text="🔧 Ventil (číslo):", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_valve = ttk.Entry(inner_filter, font=("Arial", 10), width=10)
        self.adv_valve.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(inner_filter, text="(Nechte prázdné pro všechny ventily)", 
                 font=("Arial", 8, "italic"), foreground="gray").grid(
            row=5, column=1, sticky=tk.W, padx=5, pady=0)
        
        # Tlačítka
        button_frame = ttk.Frame(inner_filter)
        button_frame.grid(row=6, column=0, columnspan=2, pady=15, sticky=tk.W, padx=5)
        
        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="🔍 Filtrovat", command=self.advanced_filter, 
                      bootstyle="success", width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_advanced_filter, 
                      bootstyle="secondary", width=15).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="🔍 Filtrovat", command=self.advanced_filter).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_advanced_filter).pack(side=tk.LEFT, padx=5)
        
        # Panel výsledků
        result_frame = ttk.LabelFrame(self.advanced_tab, text="📊 Výsledky")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Vnitřní padding
        inner_result = ttk.Frame(result_frame, padding=10)
        inner_result.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ("PK", "Název", "Množství", "Datum", "Čas", "Ventily")
        
        if TTKBOOTSTRAP_AVAILABLE:
            self.adv_tree = ttk.Treeview(inner_result, columns=columns, show="headings", 
                                        height=12, bootstyle="primary")
        else:
            self.adv_tree = ttk.Treeview(inner_result, columns=columns, show="headings", height=12)
        
        self.adv_tree.heading("PK", text="PK")
        self.adv_tree.heading("Název", text="Název")
        self.adv_tree.heading("Množství", text="Množství (g)")
        self.adv_tree.heading("Datum", text="Datum")
        self.adv_tree.heading("Čas", text="Čas")
        self.adv_tree.heading("Ventily", text="Použité ventily")
        
        self.adv_tree.column("PK", width=60, anchor=tk.CENTER)
        self.adv_tree.column("Název", width=150)
        self.adv_tree.column("Množství", width=100, anchor=tk.E)
        self.adv_tree.column("Datum", width=100, anchor=tk.CENTER)
        self.adv_tree.column("Čas", width=80, anchor=tk.CENTER)
        self.adv_tree.column("Ventily", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(inner_result, orient=tk.VERTICAL, command=self.adv_tree.yview)
        self.adv_tree.configure(yscroll=scrollbar.set)
        
        self.adv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Dvojklik pro detail
        self.adv_tree.bind('<Double-1>', self.show_advanced_recipe_detail)
        
        # Hint
        hint_label = ttk.Label(result_frame, text="💡 Tip: Dvojklikem na recept zobrazíte detail", 
                              font=("Arial", 9, "italic"), foreground="gray")
        hint_label.pack(pady=5)
    
    def browse_file(self):
        """Otevřít dialog pro výběr souboru."""
        filename = filedialog.askopenfilename(
            title="Vyberte XML soubor",
            filetypes=[("XML soubory", "*.xml *.XML"), ("Všechny soubory", "*.*")]
        )
        if filename:
            self.load_database(filename)
    
    def load_database(self, filepath):
        """Načíst XML databázi."""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            self.db = {'tree': tree, 'root': root}
            self.xml_file = filepath
            
            filename = os.path.basename(filepath)
            if TTKBOOTSTRAP_AVAILABLE:
                self.file_label.config(text=filename, bootstyle="success")
            else:
                self.file_label.config(text=filename, foreground="green")
            
            self.status_bar.config(text=f"✓ Načteno: {filepath}")
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"✓ Databáze načtena: {filename}\n\n", "success")
            self.result_text.insert(tk.END, "Naskenujte čárový kód nebo zadejte kód receptu...\n", "info")
            
            self.result_text.tag_config("success", foreground="#28a745", font=("Arial", 11, "bold"))
            self.result_text.tag_config("info", foreground="#6c757d", font=("Arial", 10))
            
        except Exception as e:
            messagebox.showerror("Chyba", f"Nelze načíst soubor:\n{e}")
            self.status_bar.config(text=f"✗ Chyba při načítání")
    
    def search_barcode(self):
        """Vyhledat podle čárového kódu."""
        if not self.db:
            messagebox.showwarning("Upozornění", "Nejprve načtěte XML soubor!")
            return
        
        barcode = self.search_entry.get().strip()
        if not barcode:
            return
        
        # Zpracovat čárový kód
        code = self.process_barcode(barcode)
        
        self.status_bar.config(text=f"Hledám kód: {code}")
        
        # Vyhledat recept
        results = self.search_by_code(code)
        
        # Zobrazit výsledky
        self.display_results(results, code)
        
        # Vymazat vstupní pole pro další sken
        self.search_entry.delete(0, tk.END)
        self.search_entry.focus()
    
    def process_barcode(self, barcode):
        """Zpracovat čárový kód."""
        barcode = barcode.strip()
        
        # Pokud obsahuje tečky, vzít část před tečkami
        if '.' in barcode:
            code = barcode.split('.')[0].strip()
            if code:
                return code
        
        # Pokud obsahuje #, vzít část před #
        if '#' in barcode:
            code = barcode.split('#')[0].strip()
            code = code.rstrip('.')
            if code:
                return code
        
        return barcode
    
    def search_by_code(self, code):
        """Vyhledat recept podle kódu."""
        results = []
        
        for elem in self.db['root'].iter('DBRecipe'):
            pk = elem.get('PK', '')
            name_elem = elem.find('.//Name[@CLASS="String"]')
            name = name_elem.get('VAL', '') if name_elem is not None else ''
            
            if code == pk or code.lower() == name.lower() or code in name:
                results.append(elem)
        
        return results
    
    def display_results(self, results, search_code):
        """Zobrazit výsledky."""
        self.result_text.delete(1.0, tk.END)
        
        if not results:
            self.result_text.insert(tk.END, f"✗ Žádné výsledky pro kód: {search_code}\n\n", "error")
            self.result_text.tag_config("error", foreground="red")
            self.status_bar.config(text=f"✗ Nenalezeno: {search_code}")
            if MATPLOTLIB_AVAILABLE:
                self.figure.clear()
                self.canvas.draw()
            return
        
        self.status_bar.config(text=f"✓ Nalezeno {len(results)} výsledků")
        
        for i, recipe in enumerate(results, 1):
            if i > 1:
                self.result_text.insert(tk.END, "\n" + "="*80 + "\n\n")
            
            self.display_recipe(recipe)
    
    def display_recipe(self, recipe_elem):
        """Zobrazit detail receptu."""
        # Základní informace
        pk = recipe_elem.get('PK', 'N/A')
        
        name_elem = recipe_elem.find('.//Name[@CLASS="String"]')
        name = name_elem.get('VAL', 'Bez názvu') if name_elem is not None else 'Bez názvu'
        
        amount_elem = recipe_elem.find('.//BezugsMenge[@CLASS="Double"]')
        amount = amount_elem.get('VAL', 'N/A') if amount_elem is not None else 'N/A'
        
        date_elem = recipe_elem.find('.//DazeitC[@CLASS="DBDate"]')
        date_time = 'N/A'
        if date_elem is not None:
            timestamp = date_elem.get('TIME')
            if timestamp:
                try:
                    dt = datetime.fromtimestamp(int(timestamp) / 1000.0)
                    date_time = dt.strftime('%d.%m.%Y %H:%M:%S')
                except:
                    date_time = timestamp
        
        # Zobrazit hlavičku
        self.result_text.insert(tk.END, f"RECEPT: {name}\n", "header")
        self.result_text.insert(tk.END, f"{'─'*80}\n")
        self.result_text.insert(tk.END, f"PK:       {pk}\n")
        self.result_text.insert(tk.END, f"Množství: {amount} g\n")
        self.result_text.insert(tk.END, f"Datum:    {date_time}\n\n")
        
        # Najít složení
        recipe_pk = recipe_elem.get('PK')
        lines = []
        
        for line in self.db['root'].iter('DBLine'):
            recipe_ref = line.find('.//Recipe[@CLASS="DBRef"]')
            if recipe_ref is not None and recipe_ref.get('PK') == recipe_pk:
                lines.append(line)
        
        if lines:
            self.result_text.insert(tk.END, f"SLOŽENÍ ({len(lines)} složek):\n", "subheader")
            self.result_text.insert(tk.END, f"{'─'*80}\n")
            
            # Data pro graf
            colors_data = []
            labels_data = []
            values_data = []
            
            total = 0
            for line in lines:
                value_elem = line.find('.//Value[@CLASS="Integer"]')
                value = int(value_elem.get('VAL', '0')) if value_elem is not None else 0
                total += value
                
                basecolor_ref = line.find('.//BaseColor[@CLASS="DBRef"]')
                if basecolor_ref is not None:
                    bc_pk = basecolor_ref.get('PK')
                    basecolor = self.find_basecolor(bc_pk)
                    
                    if basecolor:
                        bc_name_elem = basecolor.find('.//Name[@CLASS="String"]')
                        bc_name = bc_name_elem.get('VAL', f'Barva PK={bc_pk}') if bc_name_elem is not None else f'Barva PK={bc_pk}'
                        
                        bc_valve_elem = basecolor.find('.//ValveNr[@CLASS="Integer"]')
                        bc_valve = bc_valve_elem.get('VAL', '') if bc_valve_elem is not None else ''
                        
                        # Přidat do grafu
                        labels_data.append(bc_name)
                        values_data.append(value)
                        colors_data.append(self.get_color_for_name(bc_name))
                        
                        if bc_valve:
                            self.result_text.insert(tk.END, f"  • {bc_name:<30} (Ventil {bc_valve:>2}):  {value:>6} g\n", "ingredient")
                        else:
                            self.result_text.insert(tk.END, f"  • {bc_name:<30}              {value:>6} g\n", "ingredient")
            
            self.result_text.insert(tk.END, f"\n{'─'*80}\n")
            self.result_text.insert(tk.END, f"CELKEM: {total} g\n", "total")
            
            # Vykreslit graf
            if MATPLOTLIB_AVAILABLE and values_data:
                self.draw_pie_chart(labels_data, values_data, colors_data, name)
        
        # Konfigurace tagů
        self.result_text.tag_config("header", font=("Arial", 14, "bold"), foreground="blue")
        self.result_text.tag_config("subheader", font=("Arial", 11, "bold"))
        self.result_text.tag_config("ingredient", font=("Courier", 10))
        self.result_text.tag_config("total", font=("Arial", 11, "bold"), foreground="green")
    
    def get_color_for_name(self, name):
        """Získat barvu pro graf podle názvu."""
        name_lower = name.lower()
        
        color_map = {
            'yellow': '#FFD700',
            'žlut': '#FFD700',
            'red': '#DC143C',
            'červen': '#DC143C',
            'rubine': '#E30B5C',
            'magenta': '#FF00FF',
            'blue': '#1E90FF',
            'modr': '#1E90FF',
            'green': '#32CD32',
            'zelen': '#32CD32',
            'black': '#2F4F4F',
            'čern': '#2F4F4F',
            'orange': '#FF8C00',
            'oranž': '#FF8C00',
            'violet': '#8B00FF',
            'fialov': '#8B00FF',
            'pink': '#FF69B4',
            'růžov': '#FF69B4',
            'white': '#F5F5F5',
            'bíl': '#F5F5F5',
            'transparent': '#E8E8E8',
        }
        
        for key, color in color_map.items():
            if key in name_lower:
                return color
        
        return '#A9A9A9'  # Výchozí šedá
    
    def draw_pie_chart(self, labels, values, colors, title):
        """Vykreslit koláčový graf."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Vypočítat procenta
        total = sum(values)
        percentages = [(v/total)*100 for v in values]
        
        # Vytvořit popisky s procenty
        labels_with_pct = [f'{label}\n{pct:.1f}%' for label, pct in zip(labels, percentages)]
        
        # Koláčový graf
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels_with_pct,
            colors=colors,
            autopct='%d g',
            startangle=90,
            textprops={'fontsize': 8}
        )
        
        # Nastavit bílý text pro procenta
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title(f'Složení receptu: {title}', fontsize=12, fontweight='bold')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def filter_by_date(self):
        """Filtrovat recepty podle data."""
        if not self.db:
            messagebox.showwarning("Upozornění", "Nejprve načtěte XML soubor!")
            return
        
        start_str = self.start_date_entry.get().strip()
        end_str = self.end_date_entry.get().strip()
        
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d') if start_str else None
            end_date = datetime.strptime(end_str, '%Y-%m-%d') if end_str else None
        except ValueError:
            messagebox.showerror("Chyba", "Neplatný formát data! Použijte RRRR-MM-DD")
            return
        
        # Vymazat předchozí výsledky
        for item in self.date_tree.get_children():
            self.date_tree.delete(item)
        
        results = []
        
        # Projít všechny recepty
        for recipe in self.db['root'].iter('DBRecipe'):
            date_elem = recipe.find('.//DazeitC[@CLASS="DBDate"]')
            
            if date_elem is not None:
                timestamp = date_elem.get('TIME')
                if timestamp:
                    try:
                        recipe_date = datetime.fromtimestamp(int(timestamp) / 1000.0)
                        
                        # Kontrola rozsahu
                        if start_date and end_date:
                            if start_date <= recipe_date <= end_date:
                                results.append((recipe, recipe_date))
                        elif start_date:
                            if recipe_date >= start_date:
                                results.append((recipe, recipe_date))
                        elif end_date:
                            if recipe_date <= end_date:
                                results.append((recipe, recipe_date))
                    except:
                        continue
        
        # Seřadit podle data (nejnovější první)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Zobrazit výsledky
        for recipe, recipe_date in results:
            pk = recipe.get('PK', 'N/A')
            
            name_elem = recipe.find('.//Name[@CLASS="String"]')
            name = name_elem.get('VAL', 'Bez názvu') if name_elem is not None else 'Bez názvu'
            
            amount_elem = recipe.find('.//BezugsMenge[@CLASS="Double"]')
            amount = amount_elem.get('VAL', 'N/A') if amount_elem is not None else 'N/A'
            
            date_str = recipe_date.strftime('%d.%m.%Y %H:%M:%S')
            
            self.date_tree.insert('', tk.END, values=(pk, name, amount, date_str), tags=(pk,))
        
        self.status_bar.config(text=f"✓ Nalezeno {len(results)} receptů v daném období")
    
    def clear_date_filter(self):
        """Vymazat filtr data."""
        for item in self.date_tree.get_children():
            self.date_tree.delete(item)
        self.status_bar.config(text="Připraveno")
    
    def show_recipe_detail(self, event):
        """Zobrazit detail receptu po dvojkliku."""
        selection = self.date_tree.selection()
        if not selection:
            return
        
        item = self.date_tree.item(selection[0])
        pk = item['values'][0]
        
        # Najít recept podle PK
        for recipe in self.db['root'].iter('DBRecipe'):
            if recipe.get('PK') == str(pk):
                # Přepnout na záložku vyhledávání
                self.notebook.select(0)
                
                # Zobrazit detail
                self.result_text.delete(1.0, tk.END)
                self.display_recipe(recipe)
                break
    
    def advanced_filter(self):
        """Pokročilé filtrování podle data, času a ventilu."""
        if not self.db:
            messagebox.showwarning("Upozornění", "Nejprve načtěte XML soubor!")
            return
        
        # Získat hodnoty filtrů
        start_date_str = self.adv_start_date.get().strip()
        end_date_str = self.adv_end_date.get().strip()
        start_time_str = self.adv_start_time.get().strip()
        end_time_str = self.adv_end_time.get().strip()
        valve_str = self.adv_valve.get().strip()
        
        try:
            # Parsovat datum a čas
            start_datetime = None
            end_datetime = None
            
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                start_datetime = datetime.combine(start_date.date(), start_time)
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
                end_datetime = datetime.combine(end_date.date(), end_time)
        
        except ValueError as e:
            messagebox.showerror("Chyba", f"Neplatný formát data nebo času!\n{e}")
            return
        
        # Vymazat předchozí výsledky
        for item in self.adv_tree.get_children():
            self.adv_tree.delete(item)
        
        results = []
        
        # Projít všechny recepty
        for recipe in self.db['root'].iter('DBRecipe'):
            # Kontrola data a času
            date_elem = recipe.find('.//DazeitC[@CLASS="DBDate"]')
            
            if date_elem is not None:
                timestamp = date_elem.get('TIME')
                if timestamp:
                    try:
                        recipe_datetime = datetime.fromtimestamp(int(timestamp) / 1000.0)
                        
                        # Kontrola rozsahu data a času
                        if start_datetime and recipe_datetime < start_datetime:
                            continue
                        if end_datetime and recipe_datetime > end_datetime:
                            continue
                        
                        # Kontrola ventilu (pokud je zadán)
                        if valve_str:
                            recipe_pk = recipe.get('PK')
                            valves_used = self.get_recipe_valves(recipe_pk)
                            
                            if valve_str not in valves_used:
                                continue
                        
                        # Přidat do výsledků
                        results.append((recipe, recipe_datetime))
                    
                    except:
                        continue
        
        # Seřadit podle data (nejnovější první)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Zobrazit výsledky
        for recipe, recipe_datetime in results:
            pk = recipe.get('PK', 'N/A')
            
            name_elem = recipe.find('.//Name[@CLASS="String"]')
            name = name_elem.get('VAL', 'Bez názvu') if name_elem is not None else 'Bez názvu'
            
            amount_elem = recipe.find('.//BezugsMenge[@CLASS="Double"]')
            amount = amount_elem.get('VAL', 'N/A') if amount_elem is not None else 'N/A'
            
            date_str = recipe_datetime.strftime('%d.%m.%Y')
            time_str = recipe_datetime.strftime('%H:%M:%S')
            
            # Získat seznam ventilů
            valves = self.get_recipe_valves(pk)
            valves_str = ', '.join(valves) if valves else 'N/A'
            
            self.adv_tree.insert('', tk.END, values=(pk, name, amount, date_str, time_str, valves_str), tags=(pk,))
        
        self.status_bar.config(text=f"✓ Nalezeno {len(results)} receptů podle pokročilých filtrů")
    
    def get_recipe_valves(self, recipe_pk):
        """Získat seznam ventilů použitých v receptu."""
        valves = []
        
        for line in self.db['root'].iter('DBLine'):
            recipe_ref = line.find('.//Recipe[@CLASS="DBRef"]')
            if recipe_ref is not None and recipe_ref.get('PK') == recipe_pk:
                basecolor_ref = line.find('.//BaseColor[@CLASS="DBRef"]')
                if basecolor_ref is not None:
                    bc_pk = basecolor_ref.get('PK')
                    basecolor = self.find_basecolor(bc_pk)
                    
                    if basecolor:
                        bc_valve_elem = basecolor.find('.//ValveNr[@CLASS="Integer"]')
                        if bc_valve_elem is not None:
                            valve = bc_valve_elem.get('VAL', '')
                            if valve and valve not in valves:
                                valves.append(valve)
        
        return sorted(valves)
    
    def clear_advanced_filter(self):
        """Vymazat pokročilé filtry."""
        for item in self.adv_tree.get_children():
            self.adv_tree.delete(item)
        self.status_bar.config(text="Připraveno")
    
    def show_advanced_recipe_detail(self, event):
        """Zobrazit detail receptu z pokročilého filtrování."""
        selection = self.adv_tree.selection()
        if not selection:
            return
        
        item = self.adv_tree.item(selection[0])
        pk = item['values'][0]
        
        # Najít recept podle PK
        for recipe in self.db['root'].iter('DBRecipe'):
            if recipe.get('PK') == str(pk):
                # Přepnout na záložku vyhledávání
                self.notebook.select(0)
                
                # Zobrazit detail
                self.result_text.delete(1.0, tk.END)
                self.display_recipe(recipe)
                break
    
    def find_basecolor(self, pk):
        """Najít základní barvu podle PK."""
        for basecolor in self.db['root'].iter('DBBaseColor'):
            if basecolor.get('PK') == pk:
                return basecolor
        return None
    
    def clear_search(self):
        """Vymazat vyhledávání."""
        self.search_entry.delete(0, tk.END)
        self.search_entry.focus()
        
        # Přepnout focus na search entry při přepnutí na záložku
        def on_tab_change(event):
            if self.notebook.index(self.notebook.select()) == 0:
                self.search_entry.focus()
        
        self.notebook.bind('<<NotebookTabChanged>>', on_tab_change)


def main():
    if TTKBOOTSTRAP_AVAILABLE:
        # Moderní téma
        root = ttk.Window(themename="cosmo")  # Můžete změnit: cosmo, flatly, litera, minty, pulse, sandstone, united, yeti
    else:
        root = tk.Tk()
    
    app = ColorDatabaseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
