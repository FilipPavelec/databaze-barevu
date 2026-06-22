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

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ColorDatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Databáze barev - Vyhledávání")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 650)

        self.db = None
        self.xml_file = None

        # Fonty — používáme jen fonty dostupné v systému
        self._setup_fonts()
        self.setup_ui()

        default_file = "testExport.XML"
        if os.path.exists(default_file):
            self.load_database(default_file)

    def _setup_fonts(self):
        """Nastavit fonty — jen fonty dostupné v systému."""
        import tkinter.font as tkfont
        available = set(tkfont.families())

        # Proporcionální font pro UI
        for candidate in ("Ubuntu", "nimbus sans l", "helvetica", "TkDefaultFont"):
            if candidate in available or candidate.startswith("Tk"):
                self.font_ui      = (candidate, 12)
                self.font_ui_bold = (candidate, 12, "bold")
                self.font_ui_big  = (candidate, 14, "bold")
                self.font_ui_sm   = (candidate, 10, "italic")
                break

        # Monospace font pro detail receptu
        for candidate in ("courier 10 pitch", "nimbus mono l", "courier", "TkFixedFont"):
            if candidate in available or candidate.startswith("Tk"):
                self.font_mono    = (candidate, 12)
                self.font_mono_sm = (candidate, 11)
                break

        # Vstupní pole (velký font pro skener)
        self.font_entry = (self.font_ui[0], 18)

    def setup_ui(self):
        """Vytvořit uživatelské rozhraní."""
        top_frame = ttk.Frame(self.root, padding="15")
        top_frame.pack(fill=tk.X)

        file_info_frame = ttk.Frame(top_frame)
        file_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(file_info_frame, text="📁", font=self.font_ui_big).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(file_info_frame, text="XML soubor:", font=self.font_ui_bold).pack(side=tk.LEFT, padx=5)

        self.file_label = ttk.Label(file_info_frame, text="Žádný soubor", foreground="gray", font=self.font_ui)
        self.file_label.pack(side=tk.LEFT, padx=5)

        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(top_frame, text="📂 Načíst soubor", command=self.browse_file, bootstyle="primary").pack(side=tk.RIGHT, padx=5)
        else:
            ttk.Button(top_frame, text="📂 Načíst soubor", command=self.browse_file).pack(side=tk.RIGHT, padx=5)

        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)

        if TTKBOOTSTRAP_AVAILABLE:
            self.notebook = ttk.Notebook(self.root, bootstyle="primary")
        else:
            self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="🔍 Vyhledávání podle kódu")
        self.setup_search_tab()

        self.date_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.date_tab, text="📅 Filtrování podle data")
        self.setup_date_tab()

        self.advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_tab, text="⚙️ Pokročilé filtrování")
        self.setup_advanced_tab()

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        if TTKBOOTSTRAP_AVAILABLE:
            self.status_bar = ttk.Label(status_frame, text="✓ Připraveno", relief=tk.FLAT,
                                        anchor=tk.W, padding="5", bootstyle="inverse-secondary")
        else:
            self.status_bar = ttk.Label(status_frame, text="✓ Připraveno", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X)

        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_change)

    def _on_tab_change(self, event):
        if self.notebook.index(self.notebook.select()) == 0:
            self.search_entry.focus()

    def setup_search_tab(self):
        """Nastavit záložku vyhledávání."""
        search_frame = ttk.LabelFrame(self.search_tab, text="🔎 Vyhledávání receptu")
        search_frame.pack(fill=tk.X, padx=15, pady=10)

        inner_frame = ttk.Frame(search_frame, padding=15)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(inner_frame)
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Naskenujte čárový kód nebo zadejte kód:",
                  font=self.font_ui_bold).pack(anchor=tk.W, pady=(0, 5))

        entry_container = ttk.Frame(input_frame)
        entry_container.pack(fill=tk.X, pady=5)

        self.search_entry = ttk.Entry(entry_container, font=self.font_entry)
        self.search_entry.pack(fill=tk.X, ipady=8)
        self.search_entry.bind('<Return>', lambda e: self.search_barcode())

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

        result_container = ttk.Frame(self.search_tab)
        result_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        left_frame = ttk.LabelFrame(result_container, text="📋 Detail receptu")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        left_inner = ttk.Frame(left_frame, padding=10)
        left_inner.pack(fill=tk.BOTH, expand=True)

        self.result_text = scrolledtext.ScrolledText(
            left_inner, wrap=tk.WORD, font=self.font_mono, width=50,
            relief=tk.FLAT, borderwidth=0)
        self.result_text.pack(fill=tk.BOTH, expand=True)

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
        input_frame = ttk.LabelFrame(self.date_tab, text="📅 Zadejte rozsah dat")
        input_frame.pack(fill=tk.X, padx=15, pady=10)

        inner_input = ttk.Frame(input_frame, padding=15)
        inner_input.pack(fill=tk.BOTH, expand=True)
        inner_input.columnconfigure(1, weight=1)

        ttk.Label(inner_input, text="Od (RRRR-MM-DD):", font=self.font_ui_bold).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.start_date_entry = ttk.Entry(inner_input, font=self.font_ui, width=20)
        self.start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=8)
        self.start_date_entry.insert(0, "2020-01-01")

        ttk.Label(inner_input, text="Do (RRRR-MM-DD):", font=self.font_ui_bold).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.end_date_entry = ttk.Entry(inner_input, font=self.font_ui, width=20)
        self.end_date_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=8)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

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

        result_frame = ttk.LabelFrame(self.date_tab, text="📊 Výsledky")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        inner_result = ttk.Frame(result_frame, padding=10)
        inner_result.pack(fill=tk.BOTH, expand=True)

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

        scrollbar = ttk.Scrollbar(inner_result, orient=tk.VERTICAL, command=self.date_tree.yview)
        self.date_tree.configure(yscroll=scrollbar.set)
        self.date_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.date_tree.bind('<Double-1>', self.show_recipe_detail)

        ttk.Label(result_frame, text="💡 Tip: Dvojklikem na recept zobrazíte detail",
                  font=self.font_ui_sm, foreground="gray").pack(pady=5)

    def setup_advanced_tab(self):
        """Nastavit záložku pokročilého filtrování."""
        filter_frame = ttk.LabelFrame(self.advanced_tab, text="⚙️ Filtry")
        filter_frame.pack(fill=tk.X, padx=15, pady=10)

        inner_filter = ttk.Frame(filter_frame, padding=15)
        inner_filter.pack(fill=tk.BOTH, expand=True)
        inner_filter.columnconfigure(1, weight=1)

        ttk.Label(inner_filter, text="📅 Datum od:", font=self.font_ui_bold).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_start_date = ttk.Entry(inner_filter, font=self.font_ui, width=15)
        self.adv_start_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_start_date.insert(0, "2020-01-01")

        ttk.Label(inner_filter, text="📅 Datum do:", font=self.font_ui_bold).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_end_date = ttk.Entry(inner_filter, font=self.font_ui, width=15)
        self.adv_end_date.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(inner_filter, text="🕐 Čas od (HH:MM):", font=self.font_ui_bold).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_start_time = ttk.Entry(inner_filter, font=self.font_ui, width=10)
        self.adv_start_time.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_start_time.insert(0, "00:00")

        ttk.Label(inner_filter, text="🕐 Čas do (HH:MM):", font=self.font_ui_bold).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_end_time = ttk.Entry(inner_filter, font=self.font_ui, width=10)
        self.adv_end_time.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.adv_end_time.insert(0, "23:59")

        ttk.Label(inner_filter, text="🔧 Ventil (číslo):", font=self.font_ui_bold).grid(
            row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_valve = ttk.Entry(inner_filter, font=self.font_ui, width=10)
        self.adv_valve.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(inner_filter, text="(Nechte prázdné pro všechny ventily)",
                  font=self.font_ui_sm, foreground="gray").grid(
            row=5, column=1, sticky=tk.W, padx=5, pady=0)

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

        result_frame = ttk.LabelFrame(self.advanced_tab, text="📊 Výsledky")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        inner_result = ttk.Frame(result_frame, padding=10)
        inner_result.pack(fill=tk.BOTH, expand=True)

        # Sloupce včetně Šarže
        columns = ("PK", "Název", "Množství", "Datum", "Čas", "Ventily", "Šarže")

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
        self.adv_tree.heading("Šarže", text="Šarže")

        self.adv_tree.column("PK", width=60, anchor=tk.CENTER)
        self.adv_tree.column("Název", width=150)
        self.adv_tree.column("Množství", width=90, anchor=tk.E)
        self.adv_tree.column("Datum", width=90, anchor=tk.CENTER)
        self.adv_tree.column("Čas", width=70, anchor=tk.CENTER)
        self.adv_tree.column("Ventily", width=120)
        self.adv_tree.column("Šarže", width=180)

        scrollbar = ttk.Scrollbar(inner_result, orient=tk.VERTICAL, command=self.adv_tree.yview)
        self.adv_tree.configure(yscroll=scrollbar.set)
        self.adv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.adv_tree.bind('<Double-1>', self.show_advanced_recipe_detail)

        ttk.Label(result_frame, text="💡 Tip: Dvojklikem na recept zobrazíte detail",
                  font=self.font_ui_sm, foreground="gray").pack(pady=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Vyberte XML soubor",
            filetypes=[("XML soubory", "*.xml *.XML"), ("Všechny soubory", "*.*")]
        )
        if filename:
            self.load_database(filename)

    def load_database(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            self.db = {'tree': tree, 'root': root}
            self.xml_file = filepath

            # Předpočítat lookup tabulky pro rychlé filtrování
            self._build_lookup_tables(root)

            filename = os.path.basename(filepath)
            if TTKBOOTSTRAP_AVAILABLE:
                self.file_label.config(text=filename, bootstyle="success")
            else:
                self.file_label.config(text=filename, foreground="green")

            self.status_bar.config(text=f"✓ Načteno: {filepath}")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"✓ Databáze načtena: {filename}\n\n", "success")
            self.result_text.insert(tk.END, "Naskenujte čárový kód nebo zadejte kód receptu...\n", "info")
            self.result_text.tag_config("success", foreground="#28a745", font=(self.font_ui[0], 13, "bold"))
            self.result_text.tag_config("info", foreground="#6c757d", font=self.font_ui)
        except Exception as e:
            messagebox.showerror("Chyba", f"Nelze načíst soubor:\n{e}")
            self.status_bar.config(text="✗ Chyba při načítání")

    def _build_lookup_tables(self, root):
        """Předpočítat lookup tabulky jednou při načtení — klíč pro rychlost filtrování."""
        # PK -> DBBaseColor element
        self._basecolor_by_pk = {}
        for bc in root.iter('DBBaseColor'):
            pk = bc.get('PK')
            if pk:
                self._basecolor_by_pk[pk] = bc

        # recipe_pk -> list of (valve, charge) z DBLine
        from collections import defaultdict
        recipe_valves  = defaultdict(list)   # recipe_pk -> [valve_str, ...]
        recipe_charges = defaultdict(list)   # recipe_pk -> [charge_str, ...]

        for line in root.iter('DBLine'):
            recipe_ref = line.find('.//Recipe[@CLASS="DBRef"]')
            if recipe_ref is None:
                continue
            r_pk = recipe_ref.get('PK')
            if not r_pk:
                continue

            basecolor_ref = line.find('.//BaseColor[@CLASS="DBRef"]')
            if basecolor_ref is None:
                continue
            bc_pk = basecolor_ref.get('PK')
            bc = self._basecolor_by_pk.get(bc_pk)
            if bc is None:
                continue

            valve_elem = bc.find('.//ValveNr[@CLASS="Integer"]')
            if valve_elem is not None:
                valve = valve_elem.get('VAL', '')
                if valve and valve not in recipe_valves[r_pk]:
                    recipe_valves[r_pk].append(valve)

            charge_elem = bc.find('.//Charge[@CLASS="String"]')
            if charge_elem is not None:
                charge = charge_elem.get('VAL', '')
                if charge and charge not in recipe_charges[r_pk]:
                    recipe_charges[r_pk].append(charge)

        self._recipe_valves  = dict(recipe_valves)
        self._recipe_charges = dict(recipe_charges)

    def search_barcode(self):
        if not self.db:
            messagebox.showwarning("Upozornění", "Nejprve načtěte XML soubor!")
            return
        barcode = self.search_entry.get().strip()
        if not barcode:
            return
        code = self.process_barcode(barcode)
        self.status_bar.config(text=f"Hledám kód: {code}")
        results = self.search_by_code(code)
        self.display_results(results, code)
        self.search_entry.delete(0, tk.END)
        self.search_entry.focus()

    def process_barcode(self, barcode):
        barcode = barcode.strip()
        if '.' in barcode:
            code = barcode.split('.')[0].strip()
            if code:
                return code
        if '#' in barcode:
            code = barcode.split('#')[0].strip()
            code = code.rstrip('.')
            if code:
                return code
        return barcode

    def search_by_code(self, code):
        """Vyhledat recept podle kódu — vrátí jen nejnovější verzi každého názvu."""
        candidates = []
        for elem in self.db['root'].iter('DBRecipe'):
            pk = elem.get('PK', '')
            name_elem = elem.find('.//Name[@CLASS="String"]')
            name = name_elem.get('VAL', '') if name_elem is not None else ''
            if code == pk or code.lower() == name.lower() or code in name:
                # Získat datum pro řazení
                date_elem = elem.find('.//DazeitC[@CLASS="DBDate"]')
                recipe_date = None
                if date_elem is not None:
                    timestamp = date_elem.get('TIME')
                    if timestamp:
                        try:
                            recipe_date = datetime.fromtimestamp(int(timestamp) / 1000.0)
                        except:
                            pass
                candidates.append((elem, name, recipe_date))

        # Pokud hledáme podle PK, vrátíme přesnou shodu přímo
        exact_pk = [c for c in candidates if c[0].get('PK', '') == code]
        if exact_pk:
            return [exact_pk[0][0]]

        # Jinak seskupit podle názvu a vzít nejnovější verzi každého
        from collections import defaultdict
        by_name = defaultdict(list)
        for elem, name, date in candidates:
            by_name[name].append((elem, date))

        results = []
        for name, versions in by_name.items():
            # Seřadit podle data sestupně, vzít nejnovější
            versions.sort(key=lambda x: x[1] if x[1] else datetime.min, reverse=True)
            results.append(versions[0][0])

        return results

    def display_results(self, results, search_code):
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
                self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
            self.display_recipe(recipe)

    def display_recipe(self, recipe_elem):
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

        self.result_text.insert(tk.END, f"RECEPT: {name}\n", "header")
        self.result_text.insert(tk.END, f"{'─' * 80}\n")
        self.result_text.insert(tk.END, f"PK:       {pk}\n")
        self.result_text.insert(tk.END, f"Množství: {amount} g\n")
        self.result_text.insert(tk.END, f"Datum:    {date_time}\n\n")

        recipe_pk = recipe_elem.get('PK')
        lines = []
        for line in self.db['root'].iter('DBLine'):
            recipe_ref = line.find('.//Recipe[@CLASS="DBRef"]')
            if recipe_ref is not None and recipe_ref.get('PK') == recipe_pk:
                lines.append(line)

        if lines:
            self.result_text.insert(tk.END, f"SLOŽENÍ ({len(lines)} složek):\n", "subheader")
            self.result_text.insert(tk.END, f"{'─' * 80}\n")

            labels_data = []
            values_data = []
            colors_data = []
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

                        bc_charge_elem = basecolor.find('.//Charge[@CLASS="String"]')
                        bc_charge = bc_charge_elem.get('VAL', '') if bc_charge_elem is not None else ''

                        labels_data.append(bc_name)
                        values_data.append(value)
                        colors_data.append(self.get_color_for_name(bc_name))

                        charge_info = f"  [Šarže: {bc_charge}]" if bc_charge else ""
                        if bc_valve:
                            self.result_text.insert(tk.END,
                                f"  • {bc_name:<30} (Ventil {bc_valve:>2}):  {value:>6} g{charge_info}\n", "ingredient")
                        else:
                            self.result_text.insert(tk.END,
                                f"  • {bc_name:<30}              {value:>6} g{charge_info}\n", "ingredient")

            self.result_text.insert(tk.END, f"\n{'─' * 80}\n")
            self.result_text.insert(tk.END, f"CELKEM: {total} g\n\n", "total")

            self.display_recipe_history(recipe_pk, name)

            if MATPLOTLIB_AVAILABLE and values_data:
                self.draw_pie_chart(labels_data, values_data, colors_data, name)

        self.result_text.tag_config("header", font=(self.font_mono[0], 16, "bold"), foreground="blue")
        self.result_text.tag_config("subheader", font=(self.font_mono[0], 13, "bold"))
        self.result_text.tag_config("ingredient", font=self.font_mono)
        self.result_text.tag_config("total", font=(self.font_mono[0], 13, "bold"), foreground="green")
        self.result_text.tag_config("history_header", font=(self.font_mono[0], 13, "bold"), foreground="purple")
        self.result_text.tag_config("history_item", font=self.font_mono_sm, foreground="#555")

    def display_recipe_history(self, recipe_pk, recipe_name):
        history_items = []
        for stat_recipe in self.db['root'].iter('DBStatRecipe'):
            recipe_ref = stat_recipe.find('.//Recipe[@CLASS="DBRef"]')
            if recipe_ref is not None and recipe_ref.get('PK') == recipe_pk:
                mix_date_elem = stat_recipe.find('.//MixDate[@CLASS="DBDate"]')
                if mix_date_elem is not None:
                    timestamp = mix_date_elem.get('TIME')
                    if timestamp:
                        try:
                            mix_datetime = datetime.fromtimestamp(int(timestamp) / 1000.0)
                            history_items.append(mix_datetime)
                        except:
                            continue

        self.result_text.insert(tk.END, f"{'─' * 80}\n")
        self.result_text.insert(tk.END, f"📜 HISTORIE MÍCHÁNÍ", "history_header")

        if history_items:
            history_items.sort(reverse=True)
            self.result_text.insert(tk.END, f" ({len(history_items)}x):\n", "history_header")
            self.result_text.insert(tk.END, f"{'─' * 80}\n")

            for i, mix_dt in enumerate(history_items[:10], 1):
                date_str = mix_dt.strftime('%d.%m.%Y %H:%M:%S')
                now = datetime.now()
                delta = now - mix_dt
                if delta.days == 0:
                    time_ago = "Dnes"
                elif delta.days == 1:
                    time_ago = "Včera"
                elif delta.days < 7:
                    time_ago = f"Před {delta.days} dny"
                elif delta.days < 30:
                    weeks = delta.days // 7
                    time_ago = f"Před {weeks} týdny" if weeks > 1 else "Před týdnem"
                elif delta.days < 365:
                    months = delta.days // 30
                    time_ago = f"Před {months} měsíci" if months > 1 else "Před měsícem"
                else:
                    years = delta.days // 365
                    time_ago = f"Před {years} lety" if years > 1 else "Před rokem"
                self.result_text.insert(tk.END, f"  {i:2}. {date_str}  ({time_ago})\n", "history_item")

            if len(history_items) > 10:
                self.result_text.insert(tk.END, f"  ... a dalších {len(history_items) - 10} míchání\n", "history_item")

            last_mix = history_items[0]
            days_ago = (datetime.now() - last_mix).days
            if days_ago == 0:
                last_info = "Naposledy míchán DNES"
            elif days_ago == 1:
                last_info = "Naposledy míchán VČERA"
            else:
                last_info = f"Naposledy míchán před {days_ago} dny"
            self.result_text.insert(tk.END, f"\n  ⏱️  {last_info}\n", "history_header")
        else:
            self.result_text.insert(tk.END, ":\n", "history_header")
            self.result_text.insert(tk.END, f"{'─' * 80}\n")
            self.result_text.insert(tk.END, "  Tento recept ještě nebyl míchán (pouze vytvořen)\n", "history_item")

    def get_color_for_name(self, name):
        name_lower = name.lower()
        color_map = {
            'yellow': '#FFD700', 'žlut': '#FFD700',
            'red': '#DC143C', 'červen': '#DC143C', 'rot': '#DC143C',
            'rubine': '#E30B5C', 'magenta': '#FF00FF',
            'blue': '#1E90FF', 'modr': '#1E90FF',
            'green': '#32CD32', 'zelen': '#32CD32',
            'black': '#2F4F4F', 'čern': '#2F4F4F', 'schwarz': '#2F4F4F',
            'orange': '#FF8C00', 'oranž': '#FF8C00',
            'violet': '#8B00FF', 'fialov': '#8B00FF',
            'pink': '#FF69B4', 'růžov': '#FF69B4',
            'white': '#F5F5F5', 'bíl': '#F5F5F5',
            'transparent': '#E8E8E8',
        }
        for key, color in color_map.items():
            if key in name_lower:
                return color
        return '#A9A9A9'

    def draw_pie_chart(self, labels, values, colors, title):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        total = sum(values)

        # Popisky s názvem a procentem
        labels_with_pct = [f'{label}\n{(v/total)*100:.1f}%' for label, v in zip(labels, values)]

        # Vlastní funkce pro zobrazení gramů uvnitř výseče
        def make_autopct(vals):
            def autopct(pct):
                absolute = int(round(pct * total / 100.0))
                return f'{absolute} g'
            return autopct

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels_with_pct,
            colors=colors,
            autopct=make_autopct(values),
            startangle=90,
            textprops={'fontsize': 8}
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        ax.set_title(f'Složení: {title}', fontsize=11, fontweight='bold')
        self.figure.tight_layout()
        self.canvas.draw()

    def filter_by_date(self):
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

        for item in self.date_tree.get_children():
            self.date_tree.delete(item)

        results = []
        for recipe in self.db['root'].iter('DBRecipe'):
            date_elem = recipe.find('.//DazeitC[@CLASS="DBDate"]')
            if date_elem is not None:
                timestamp = date_elem.get('TIME')
                if timestamp:
                    try:
                        recipe_date = datetime.fromtimestamp(int(timestamp) / 1000.0)
                        if start_date and recipe_date < start_date:
                            continue
                        if end_date and recipe_date > end_date:
                            continue
                        results.append((recipe, recipe_date))
                    except:
                        continue

        results.sort(key=lambda x: x[1], reverse=True)

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
        for item in self.date_tree.get_children():
            self.date_tree.delete(item)
        self.status_bar.config(text="Připraveno")

    def show_recipe_detail(self, event):
        selection = self.date_tree.selection()
        if not selection:
            return
        item = self.date_tree.item(selection[0])
        pk = item['values'][0]
        for recipe in self.db['root'].iter('DBRecipe'):
            if recipe.get('PK') == str(pk):
                self.notebook.select(0)
                self.result_text.delete(1.0, tk.END)
                self.display_recipe(recipe)
                break

    def advanced_filter(self):
        """Pokročilé filtrování podle data, času a ventilu."""
        if not self.db:
            messagebox.showwarning("Upozornění", "Nejprve načtěte XML soubor!")
            return

        start_date_str = self.adv_start_date.get().strip()
        end_date_str = self.adv_end_date.get().strip()
        start_time_str = self.adv_start_time.get().strip()
        end_time_str = self.adv_end_time.get().strip()
        valve_str = self.adv_valve.get().strip()

        try:
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

        for item in self.adv_tree.get_children():
            self.adv_tree.delete(item)

        results = []

        for recipe in self.db['root'].iter('DBRecipe'):
            date_elem = recipe.find('.//DazeitC[@CLASS="DBDate"]')
            if date_elem is None:
                continue
            timestamp = date_elem.get('TIME')
            if not timestamp:
                continue
            try:
                recipe_datetime = datetime.fromtimestamp(int(timestamp) / 1000.0)
            except:
                continue

            if start_datetime and recipe_datetime < start_datetime:
                continue
            if end_datetime and recipe_datetime > end_datetime:
                continue

            recipe_pk = recipe.get('PK')

            if valve_str:
                valves_used = self.get_recipe_valves(recipe_pk)
                if valve_str not in valves_used:
                    continue

            results.append((recipe, recipe_datetime))

        results.sort(key=lambda x: x[1], reverse=True)

        for recipe, recipe_datetime in results:
            pk = recipe.get('PK', 'N/A')

            name_elem = recipe.find('.//Name[@CLASS="String"]')
            name = name_elem.get('VAL', 'Bez názvu') if name_elem is not None else 'Bez názvu'

            amount_elem = recipe.find('.//BezugsMenge[@CLASS="Double"]')
            amount = amount_elem.get('VAL', 'N/A') if amount_elem is not None else 'N/A'

            date_str = recipe_datetime.strftime('%d.%m.%Y')
            time_str = recipe_datetime.strftime('%H:%M:%S')

            valves = self.get_recipe_valves(pk)
            valves_str = ', '.join(valves) if valves else 'N/A'

            charges = self.get_recipe_charges(pk)
            charges_str = ', '.join(charges) if charges else ''

            self.adv_tree.insert('', tk.END,
                values=(pk, name, amount, date_str, time_str, valves_str, charges_str),
                tags=(pk,))

        self.status_bar.config(text=f"✓ Nalezeno {len(results)} receptů podle pokročilých filtrů")

    def get_recipe_valves(self, recipe_pk):
        """Získat seznam ventilů použitých v receptu — z předpočítané tabulky."""
        return sorted(self._recipe_valves.get(recipe_pk, []))

    def get_recipe_charges(self, recipe_pk):
        """Získat seznam šarží použitých v receptu — z předpočítané tabulky."""
        return self._recipe_charges.get(recipe_pk, [])

    def find_basecolor(self, pk):
        """Najít základní barvu podle PK — z předpočítané tabulky."""
        return self._basecolor_by_pk.get(pk)

    def clear_advanced_filter(self):
        for item in self.adv_tree.get_children():
            self.adv_tree.delete(item)
        self.status_bar.config(text="Připraveno")

    def show_advanced_recipe_detail(self, event):
        selection = self.adv_tree.selection()
        if not selection:
            return
        item = self.adv_tree.item(selection[0])
        pk = item['values'][0]
        for recipe in self.db['root'].iter('DBRecipe'):
            if recipe.get('PK') == str(pk):
                self.notebook.select(0)
                self.result_text.delete(1.0, tk.END)
                self.display_recipe(recipe)
                break

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.search_entry.focus()


def main():
    if TTKBOOTSTRAP_AVAILABLE:
        root = ttk.Window(themename="cosmo")
    else:
        root = tk.Tk()

    app = ColorDatabaseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
