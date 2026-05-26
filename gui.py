#!/usr/bin/env python3
"""
Databáze barev — grafické rozhraní (GUI)
=========================================
Aplikace pro vyhledávání a filtrování receptů z XML exportu míchacího stroje.

Funkce:
  - Vyhledávání receptu podle kódu nebo čárového kódu
  - Filtrování receptů podle data vytvoření
  - Pokročilé filtrování podle data, času, ventilu a šarže
  - Koláčový graf složení receptu
  - Historie míchání každého receptu

Závislosti (volitelné, aplikace funguje i bez nich):
  - ttkbootstrap  → moderní vzhled (pip install ttkbootstrap)
  - matplotlib    → koláčový graf  (pip install matplotlib)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import csv

# Pokus o načtení reportlab pro export do PDF.
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors as rl_colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Pokus o načtení ttkbootstrap pro moderní vzhled.
# Pokud není nainstalován, použije se standardní tkinter ttk.
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    from tkinter import ttk
    TTKBOOTSTRAP_AVAILABLE = False

import calendar


class DatePickerPopup:
    """
    Jednoduchý popup kalendář v čistém tkinter.

    Nevyžaduje tkcalendar ani žádnou jinou závislost — funguje
    spolehlivě i s ttkbootstrap, protože nepoužívá žádné ttk widgety
    které by ttkbootstrap mohl přepsat.

    Použití:
        DatePickerPopup(parent, callback, initial_date="2024-01-15")
        # callback(date_str) je zavolán po výběru data ve formátu RRRR-MM-DD
    """

    def __init__(self, parent, callback, initial_date=None):
        self.callback = callback

        # Počáteční datum
        today = datetime.now()
        if initial_date:
            try:
                dt = datetime.strptime(initial_date, '%Y-%m-%d')
                self.year = dt.year
                self.month = dt.month
                self.selected_day = dt.day
            except ValueError:
                self.year = today.year
                self.month = today.month
                self.selected_day = today.day
        else:
            self.year = today.year
            self.month = today.month
            self.selected_day = today.day

        # Popup okno — používáme čistý tk.Toplevel, ne ttk
        self.win = tk.Toplevel(parent)
        self.win.title("Vyberte datum")
        self.win.resizable(False, False)
        self.win.grab_set()
        self.win.transient(parent)

        # Zarovnat popup pod kurzor / vedle rodiče
        parent.update_idletasks()
        x = parent.winfo_rootx()
        y = parent.winfo_rooty() + parent.winfo_height()
        self.win.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        """Sestavit UI kalendáře."""
        bg = "#ffffff"
        header_bg = "#2c6fad"
        header_fg = "#ffffff"
        day_bg = "#ffffff"
        day_hover = "#d0e8ff"
        day_selected = "#2c6fad"
        day_selected_fg = "#ffffff"
        weekend_fg = "#c0392b"
        other_month_fg = "#cccccc"
        today_fg = "#27ae60"

        self.win.configure(bg=bg)

        # ── Záhlaví: ← Měsíc Rok → ──────────────────────────────────
        header = tk.Frame(self.win, bg=header_bg, pady=6)
        header.pack(fill=tk.X)

        tk.Button(header, text="<", bg=header_bg, fg=header_fg,
                  relief=tk.FLAT, font=("TkDefaultFont", 12, "bold"),
                  activebackground="#1a4f80", activeforeground=header_fg,
                  cursor="hand2", command=self._prev_month).pack(side=tk.LEFT, padx=8)

        self.header_label = tk.Label(header, bg=header_bg, fg=header_fg,
                                     font=("TkDefaultFont", 11, "bold"))
        self.header_label.pack(side=tk.LEFT, expand=True)

        tk.Button(header, text=">", bg=header_bg, fg=header_fg,
                  relief=tk.FLAT, font=("TkDefaultFont", 12, "bold"),
                  activebackground="#1a4f80", activeforeground=header_fg,
                  cursor="hand2", command=self._next_month).pack(side=tk.RIGHT, padx=8)

        # ── Navigace roku ────────────────────────────────────────────
        year_nav = tk.Frame(self.win, bg=bg, pady=2)
        year_nav.pack(fill=tk.X)

        tk.Button(year_nav, text="<< rok", bg=bg, fg="#555",
                  relief=tk.FLAT, font=("TkDefaultFont", 9),
                  cursor="hand2", command=self._prev_year).pack(side=tk.LEFT, padx=8)
        tk.Label(year_nav, text="", bg=bg).pack(side=tk.LEFT, expand=True)
        tk.Button(year_nav, text="rok >>", bg=bg, fg="#555",
                  relief=tk.FLAT, font=("TkDefaultFont", 9),
                  cursor="hand2", command=self._next_year).pack(side=tk.RIGHT, padx=8)

        # ── Názvy dnů ────────────────────────────────────────────────
        days_header = tk.Frame(self.win, bg=bg)
        days_header.pack(fill=tk.X, padx=4)

        day_names = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
        for i, d in enumerate(day_names):
            fg = weekend_fg if i >= 5 else "#555555"
            tk.Label(days_header, text=d, bg=bg, fg=fg,
                     font=("TkDefaultFont", 9, "bold"),
                     width=4, anchor=tk.CENTER).grid(row=0, column=i, padx=1, pady=2)

        # ── Mřížka dnů ───────────────────────────────────────────────
        self.grid_frame = tk.Frame(self.win, bg=bg)
        self.grid_frame.pack(fill=tk.BOTH, padx=4, pady=(0, 4))

        # ── Tlačítko Dnes ────────────────────────────────────────────
        today_frame = tk.Frame(self.win, bg=bg, pady=4)
        today_frame.pack(fill=tk.X)

        tk.Button(today_frame, text="Dnes", bg="#f0f0f0", fg="#333",
                  relief=tk.FLAT, font=("TkDefaultFont", 9),
                  cursor="hand2", command=self._select_today,
                  padx=10, pady=3).pack()

        # Uložit barvy pro použití v _render_grid
        self._colors = {
            'bg': bg, 'day_hover': day_hover,
            'day_selected': day_selected, 'day_selected_fg': day_selected_fg,
            'weekend_fg': weekend_fg, 'other_month_fg': other_month_fg,
            'today_fg': today_fg, 'day_bg': day_bg,
        }

        self._render_grid()

    def _render_grid(self):
        """Překreslit mřížku dnů pro aktuální měsíc/rok."""
        c = self._colors
        today = datetime.now()

        # Vymazat starou mřížku
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Aktualizovat záhlaví
        month_names = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen",
                       "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"]
        self.header_label.config(text=f"{month_names[self.month - 1]} {self.year}")

        # Sestavit kalendář — calendar.monthcalendar vrátí týdny jako řádky
        # Každý týden je seznam 7 čísel (0 = den nepatří do tohoto měsíce)
        weeks = calendar.monthcalendar(self.year, self.month)

        for row_idx, week in enumerate(weeks):
            for col_idx, day in enumerate(week):
                if day == 0:
                    # Den z předchozího/následujícího měsíce — zobrazit šedě
                    lbl = tk.Label(self.grid_frame, text="", bg=c['bg'],
                                   width=4, height=1)
                    lbl.grid(row=row_idx, column=col_idx, padx=1, pady=1)
                    continue

                is_today = (day == today.day and self.month == today.month
                            and self.year == today.year)
                is_selected = (day == self.selected_day)
                is_weekend = col_idx >= 5

                if is_selected:
                    bg_color = c['day_selected']
                    fg_color = c['day_selected_fg']
                    font_weight = "bold"
                elif is_today:
                    bg_color = c['bg']
                    fg_color = c['today_fg']
                    font_weight = "bold"
                elif is_weekend:
                    bg_color = c['bg']
                    fg_color = c['weekend_fg']
                    font_weight = "normal"
                else:
                    bg_color = c['bg']
                    fg_color = "#333333"
                    font_weight = "normal"

                btn = tk.Button(
                    self.grid_frame,
                    text=str(day),
                    bg=bg_color, fg=fg_color,
                    relief=tk.FLAT,
                    font=("TkDefaultFont", 10, font_weight),
                    width=3, height=1,
                    cursor="hand2",
                    activebackground=c['day_hover'],
                    command=lambda d=day: self._select_day(d)
                )
                btn.grid(row=row_idx, column=col_idx, padx=1, pady=1)

    def _select_day(self, day):
        """Vybrat den a zavolat callback."""
        self.selected_day = day
        date_str = f"{self.year:04d}-{self.month:02d}-{day:02d}"
        self.win.destroy()
        self.callback(date_str)

    def _select_today(self):
        """Přeskočit na dnešní datum."""
        today = datetime.now()
        self._select_day(today.day) if (today.month == self.month and today.year == self.year) else None
        # Pokud jsme na jiném měsíci, přepnout a vybrat
        self.year = today.year
        self.month = today.month
        self.selected_day = today.day
        date_str = today.strftime('%Y-%m-%d')
        self.win.destroy()
        self.callback(date_str)

    def _prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.selected_day = min(self.selected_day,
                                calendar.monthrange(self.year, self.month)[1])
        self._render_grid()

    def _next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.selected_day = min(self.selected_day,
                                calendar.monthrange(self.year, self.month)[1])
        self._render_grid()

    def _prev_year(self):
        self.year -= 1
        self.selected_day = min(self.selected_day,
                                calendar.monthrange(self.year, self.month)[1])
        self._render_grid()

    def _next_year(self):
        self.year += 1
        self.selected_day = min(self.selected_day,
                                calendar.monthrange(self.year, self.month)[1])
        self._render_grid()


class DatePickerEntry(tk.Frame):
    """
    Složený widget: Entry pro datum + tlačítko 📅 pro otevření popup kalendáře.

    Náhrada za tkcalendar.DateEntry — bez závislostí, kompatibilní s ttkbootstrap.

    Použití:
        widget = DatePickerEntry(parent, font=..., width=15)
        widget.set("2024-03-15")
        value = widget.get()   # vrátí "RRRR-MM-DD"
        widget.pack(...)
    """

    def __init__(self, parent, font=None, width=15, **kwargs):
        # Použít čistý tk.Frame jako kontejner — ttkbootstrap ho nepřepíše
        try:
            bg = parent.cget('background')
        except Exception:
            bg = 'white'
        super().__init__(parent, bg=bg)

        self._entry = ttk.Entry(self, font=font, width=width)
        self._entry.pack(side=tk.LEFT)

        # Tlačítko kalendáře — čistý tk.Button, ne ttk (ttkbootstrap ho nepřepíše)
        self._btn = tk.Button(
            self, text="Datum",
            relief=tk.GROOVE,
            cursor="hand2",
            font=("TkDefaultFont", 9),
            bg="#e8e8e8", activebackground="#d0d0d0",
            padx=4, pady=1,
            command=self._open_picker
        )
        self._btn.pack(side=tk.LEFT, padx=(2, 0))

    def _open_picker(self):
        """Otevřít popup kalendář s aktuální hodnotou jako počátečním datem."""
        current = self._entry.get().strip()
        DatePickerPopup(self._btn, self._set_date, initial_date=current or None)

    def _set_date(self, date_str):
        """Callback z DatePickerPopup — nastavit hodnotu do Entry."""
        self._entry.delete(0, tk.END)
        self._entry.insert(0, date_str)

    def get(self):
        """Vrátit aktuální hodnotu (stejné rozhraní jako ttk.Entry)."""
        return self._entry.get()

    def insert(self, index, string):
        """Vložit text (stejné rozhraní jako ttk.Entry)."""
        self._entry.insert(index, string)

    def delete(self, first, last=None):
        """Smazat obsah (stejné rozhraní jako ttk.Entry)."""
        self._entry.delete(first, last)

    def grid(self, **kwargs):
        """Předat grid() na Frame kontejner."""
        super().grid(**kwargs)

    def pack(self, **kwargs):
        """Předat pack() na Frame kontejner."""
        super().pack(**kwargs)

# Pokus o načtení matplotlib pro koláčový graf složení.
# Pokud není nainstalován, záložka vyhledávání zobrazí jen textový detail.
try:
    import matplotlib
    matplotlib.use('TkAgg')          # backend kompatibilní s tkinter
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ColorDatabaseGUI:
    """
    Hlavní třída aplikace.

    Spravuje celé GUI — načítání databáze, záložky, vyhledávání a filtrování.
    Při inicializaci vytvoří okno a nastaví fonty a widgety.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Databáze barev — Model Obaly Hostinné")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 650)

        # Načtená databáze — None dokud uživatel nevybere soubor.
        # Po načtení: {'tree': ET.ElementTree, 'root': ET.Element}
        self.db = None
        self.xml_file = None  # cesta k aktuálně načtenému souboru

        # Lookup tabulky předpočítané při načtení databáze (viz _build_lookup_tables)
        self._basecolor_by_pk = {}   # PK -> DBBaseColor element
        self._recipe_valves   = {}   # recipe_pk -> [ventil, ...]
        self._recipe_charges  = {}   # recipe_pk -> [šarže, ...]

        self._setup_fonts()
        self.setup_ui()

    def _setup_fonts(self):
        """
        Vybrat fonty dostupné v aktuálním systému.

        Tkinter na Linuxu vidí jen X11 fonty (ne TrueType přímo).
        Proto procházíme seznam kandidátů a vezmeme první dostupný,
        aby se předešlo fallbacku na font bez podpory diakritiky.
        """
        import tkinter.font as tkfont
        available = set(tkfont.families())

        # Proporcionální font pro popisky, tlačítka a vstupní pole
        for candidate in ("Ubuntu", "nimbus sans l", "helvetica", "TkDefaultFont"):
            if candidate in available or candidate.startswith("Tk"):
                self.font_ui      = (candidate, 12)           # běžný text
                self.font_ui_bold = (candidate, 12, "bold")   # tučné popisky
                self.font_ui_big  = (candidate, 14, "bold")   # nadpisy
                self.font_ui_sm   = (candidate, 10, "italic") # nápovědy
                break

        # Monospace font pro detail receptu (zarovnání sloupců)
        for candidate in ("courier 10 pitch", "nimbus mono l", "courier", "TkFixedFont"):
            if candidate in available or candidate.startswith("Tk"):
                self.font_mono    = (candidate, 12)  # složení receptu
                self.font_mono_sm = (candidate, 11)  # historie míchání
                break

        # Velký font pro vstupní pole skeneru čárových kódů
        self.font_entry = (self.font_ui[0], 18)

    def setup_ui(self):
        """
        Sestavit hlavní okno aplikace.

        Struktura:
          - Horní lišta: logo Model Group + název souboru + tlačítko Načíst
          - Branding lišta: Model Obaly Hostinné
          - Notebook se třemi záložkami: Vyhledávání / Filtrování podle data / Pokročilé filtrování
          - Stavový řádek dole
        """
        # Nastavit ikonu okna (model_logo.ico pokud existuje)
        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_logo.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass  # na Linuxu iconbitmap nemusí fungovat, nevadí

        # Načíst PNG logo pro zobrazení v GUI
        self._logo_image = None
        png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MODEL_Logo_M.png")
        if os.path.exists(png_path):
            try:
                # Tkinter PhotoImage — zmenšit logo na výšku ~40px
                raw = tk.PhotoImage(file=png_path)
                # Poměr stran: 1514x681 → při výšce 40px šířka ~89px
                # subsample(n) zmenší n-krát; 681/40 ≈ 17
                factor = max(1, raw.height() // 40)
                self._logo_image = raw.subsample(factor, factor)
            except Exception:
                self._logo_image = None
        top_frame = ttk.Frame(self.root, padding="10 8")
        top_frame.pack(fill=tk.X)

        # Logo Model Group vlevo
        if self._logo_image:
            logo_label = ttk.Label(top_frame, image=self._logo_image)
            logo_label.pack(side=tk.LEFT, padx=(0, 15))

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

        # Branding lišta — Model Obaly Hostinné / Model Group
        brand_frame = ttk.Frame(self.root, padding="4 2")
        brand_frame.pack(fill=tk.X, padx=10)
        ttk.Label(brand_frame, text="Model Obaly a.s. — závod Hostinné",
                  font=self.font_ui_bold).pack(side=tk.LEFT)
        ttk.Label(brand_frame, text="| Model Group",
                  font=self.font_ui, foreground="gray").pack(side=tk.LEFT, padx=8)
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10, pady=2)

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
        """Při přepnutí na záložku Vyhledávání automaticky přesunout focus do vstupního pole."""
        if self.notebook.index(self.notebook.select()) == 0:
            self.search_entry.focus()

    def setup_search_tab(self):
        """
        Záložka „Vyhledávání podle kódu".

        Obsahuje:
          - Vstupní pole pro ruční zadání nebo sken čárového kódu (Enter = vyhledat)
          - Textová oblast s detailem receptu (název, PK, složení, šarže, historie míchání)
          - Koláčový graf složení (pouze pokud je nainstalován matplotlib)
        """
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
            ttk.Button(button_frame, text="💾 Export", command=lambda: self.export_results('search'),
                       bootstyle="info", width=15).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="🔍 Vyhledat", command=self.search_barcode).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_search).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="💾 Export", command=lambda: self.export_results('search')).pack(side=tk.LEFT, padx=5)

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
        """
        Záložka „Filtrování podle data".

        Umožňuje zobrazit všechny recepty vytvořené v zadaném časovém rozsahu.
        Výsledky jsou seřazeny od nejnovějšího. Dvojklik na řádek přepne na
        záložku Vyhledávání a zobrazí plný detail receptu.
        """
        input_frame = ttk.LabelFrame(self.date_tab, text="📅 Zadejte rozsah dat")
        input_frame.pack(fill=tk.X, padx=15, pady=10)

        inner_input = ttk.Frame(input_frame, padding=15)
        inner_input.pack(fill=tk.BOTH, expand=True)
        inner_input.columnconfigure(1, weight=1)

        ttk.Label(inner_input, text="Od:", font=self.font_ui_bold).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.start_date_entry = DatePickerEntry(inner_input, font=self.font_ui, width=14)
        self.start_date_entry.insert(0, "2020-01-01")
        self.start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=8)

        ttk.Label(inner_input, text="Do:", font=self.font_ui_bold).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.end_date_entry = DatePickerEntry(inner_input, font=self.font_ui, width=14)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=8)

        button_frame = ttk.Frame(inner_input)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W, padx=5)

        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="Filtrovat", command=self.filter_by_date,
                       bootstyle="success", width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Vymazat", command=self.clear_date_filter,
                       bootstyle="secondary", width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Export", command=lambda: self.export_results('date'),
                       bootstyle="info", width=15).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="Filtrovat", command=self.filter_by_date).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Vymazat", command=self.clear_date_filter).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Export", command=lambda: self.export_results('date')).pack(side=tk.LEFT, padx=5)

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

        ttk.Label(result_frame, text="Tip: Dvojklikem na recept zobrazíte detail",
                  font=self.font_ui_sm, foreground="gray").pack(pady=5)

    def setup_advanced_tab(self):
        """
        Záložka „Pokročilé filtrování".

        Kombinuje více filtrů najednou:
          - Rozsah data a času vytvoření receptu
          - Číslo ventilu (zobrazí jen recepty, které daný ventil používají)
        Výsledky obsahují sloupec Šarže — čísla šarží všech složek receptu.
        Dvojklik zobrazí plný detail na záložce Vyhledávání.

        Výkon: filtrování je rychlé díky lookup tabulkám předpočítaným
        při načtení souboru (viz _build_lookup_tables).
        """
        filter_frame = ttk.LabelFrame(self.advanced_tab, text="⚙️ Filtry")
        filter_frame.pack(fill=tk.X, padx=15, pady=10)

        inner_filter = ttk.Frame(filter_frame, padding=15)
        inner_filter.pack(fill=tk.BOTH, expand=True)
        inner_filter.columnconfigure(1, weight=1)

        ttk.Label(inner_filter, text="📅 Datum od:", font=self.font_ui_bold).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_start_date = DatePickerEntry(inner_filter, font=self.font_ui, width=13)
        self.adv_start_date.insert(0, "2020-01-01")
        self.adv_start_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(inner_filter, text="📅 Datum do:", font=self.font_ui_bold).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_end_date = DatePickerEntry(inner_filter, font=self.font_ui, width=13)
        self.adv_end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.adv_end_date.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

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

        ttk.Label(inner_filter, text="🎨 Barva (název nebo číslo):", font=self.font_ui_bold).grid(
            row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.adv_color = ttk.Entry(inner_filter, font=self.font_ui, width=20)
        self.adv_color.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(inner_filter, text="(Např. '48', 'Transparent', 'Blue 17')",
                  font=self.font_ui_sm, foreground="gray").grid(
            row=7, column=1, sticky=tk.W, padx=5, pady=0)

        button_frame = ttk.Frame(inner_filter)
        button_frame.grid(row=8, column=0, columnspan=2, pady=15, sticky=tk.W, padx=5)

        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="🔍 Filtrovat", command=self.advanced_filter,
                       bootstyle="success", width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_advanced_filter,
                       bootstyle="secondary", width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="💾 Export", command=lambda: self.export_results('advanced'),
                       bootstyle="info", width=15).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="🔍 Filtrovat", command=self.advanced_filter).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🗑️ Vymazat", command=self.clear_advanced_filter).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="💾 Export", command=lambda: self.export_results('advanced')).pack(side=tk.LEFT, padx=5)

        result_frame = ttk.LabelFrame(self.advanced_tab, text="📊 Výsledky")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        inner_result = ttk.Frame(result_frame, padding=10)
        inner_result.pack(fill=tk.BOTH, expand=True)

        columns = ("PK", "Název", "Množství", "Datum", "Čas", "Ventily", "Šarže")

        if TTKBOOTSTRAP_AVAILABLE:
            self.adv_tree = ttk.Treeview(inner_result, columns=columns, show="headings",
                                         height=12, bootstyle="primary")
        else:
            self.adv_tree = ttk.Treeview(inner_result, columns=columns, show="headings", height=12)

        self.adv_tree.heading("PK",      text="PK")
        self.adv_tree.heading("Název",   text="Název")
        self.adv_tree.heading("Množství",text="Množství (g)")
        self.adv_tree.heading("Datum",   text="Datum")
        self.adv_tree.heading("Čas",     text="Čas")
        self.adv_tree.heading("Ventily", text="Použité ventily")
        self.adv_tree.heading("Šarže",   text="Šarže")

        self.adv_tree.column("PK",       width=60,  anchor=tk.CENTER)
        self.adv_tree.column("Název",    width=160)
        self.adv_tree.column("Množství", width=90,  anchor=tk.E)
        self.adv_tree.column("Datum",    width=90,  anchor=tk.CENTER)
        self.adv_tree.column("Čas",      width=70,  anchor=tk.CENTER)
        self.adv_tree.column("Ventily",  width=110)
        self.adv_tree.column("Šarže",    width=180)

        scrollbar = ttk.Scrollbar(inner_result, orient=tk.VERTICAL, command=self.adv_tree.yview)
        self.adv_tree.configure(yscroll=scrollbar.set)
        self.adv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.adv_tree.bind('<Double-1>', self.show_advanced_recipe_detail)

        ttk.Label(result_frame, text="Tip: Dvojklikem na recept zobrazíte přehledný detail",
                  font=self.font_ui_sm, foreground="gray").pack(pady=5)

    def browse_file(self):
        """Otevřít dialog pro výběr XML souboru a načíst databázi."""
        filename = filedialog.askopenfilename(
            title="Vyberte XML soubor",
            filetypes=[("XML soubory", "*.xml *.XML"), ("Všechny soubory", "*.*")]
        )
        if filename:
            self.load_database(filename)

    def load_database(self, filepath):
        """
        Načíst XML soubor a připravit databázi.

        Po úspěšném načtení zavolá _build_lookup_tables() pro předpočítání
        slovníků ventilů a šarží — to zajistí rychlé pokročilé filtrování.
        """
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
        """
        Předpočítat lookup tabulky jednou při načtení souboru.

        Problém bez tabulek: pokročilé filtrování pro každý recept iteruje
        přes všechny DBLine (1993) a DBBaseColor (22) → O(n²) → ~17 sekund zaseknutí.

        Řešení: projdeme XML jednou a sestavíme slovníky:
          _basecolor_by_pk  — PK → DBBaseColor element          (O(1) lookup)
          _recipe_valves    — recipe_pk → [čísla ventilů]
          _recipe_charges   — recipe_pk → [čísla šarží]

        Filtrování pak trvá ~20ms místo 17 sekund.
        """
        from collections import defaultdict

        # Krok 1: slovník PK → DBBaseColor element pro O(1) přístup
        self._basecolor_by_pk = {}
        for bc in root.iter('DBBaseColor'):
            pk = bc.get('PK')
            if pk:
                self._basecolor_by_pk[pk] = bc

        # Krok 2: pro každý recept sestavit seznam ventilů, šarží, názvů barev a DBLine z DBLine
        recipe_valves  = defaultdict(list)   # recipe_pk -> [číslo ventilu, ...]
        recipe_charges = defaultdict(list)   # recipe_pk -> [šarže, ...]
        recipe_colors  = defaultdict(list)   # recipe_pk -> [název barvy, ...]
        lines_by_recipe = defaultdict(list)  # recipe_pk -> [DBLine element, ...]

        for line in root.iter('DBLine'):
            recipe_ref = line.find('.//Recipe[@CLASS="DBRef"]')
            if recipe_ref is None:
                continue
            r_pk = recipe_ref.get('PK')
            if not r_pk:
                continue

            lines_by_recipe[r_pk].append(line)

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

            name_elem = bc.find('.//Name[@CLASS="String"]')
            if name_elem is not None:
                color_name = name_elem.get('VAL', '')
                if color_name and color_name not in recipe_colors[r_pk]:
                    recipe_colors[r_pk].append(color_name)

        self._recipe_valves    = dict(recipe_valves)
        self._recipe_charges   = dict(recipe_charges)
        self._recipe_colors    = dict(recipe_colors)
        self._lines_by_recipe  = dict(lines_by_recipe)

    def search_barcode(self):
        """
        Zpracovat vstup z pole skeneru a spustit vyhledávání.

        Po vyhledání vymaže vstupní pole a vrátí focus — připraveno
        pro okamžité naskenování dalšího kódu.
        """
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
        """
        Normalizovat naskenovaný čárový kód na čistý kód receptu.

        Formát skeneru: "286.........#00012979"
          - část za '#' = PK míchání (DBStatRecipe) → "00012979"
        Pokud '#' není, bereme část před první tečkou.
        """
        if '#' in barcode:
            code = barcode.split('#', 1)[1].strip()
            if code:
                return code
        if '.' in barcode:
            code = barcode.split('.')[0].strip()
            if code:
                return code
        return barcode

    def search_by_code(self, code):
        """
        Vyhledat recept podle kódu (PK nebo název DBRecipe, nebo PK DBStatRecipe).

        Vrací seznam tuplů (recipe_elem, stat_elem_nebo_None).
        Pokud kód odpovídá PK záznamu DBStatRecipe, vrátí recept + konkrétní míchání.
        """
        # Nejdřív zkusit najít DBStatRecipe podle PK (naskenované číslo za #)
        code_stripped = code.lstrip('0') or '0'
        for stat in self.db['root'].iter('DBStatRecipe'):
            stat_pk = stat.get('PK', '')
            if stat_pk == code or stat_pk == code_stripped:
                recipe_ref = stat.find('.//Recipe[@CLASS="DBRef"]')
                if recipe_ref is not None:
                    recipe_pk = recipe_ref.get('PK')
                    for recipe in self.db['root'].iter('DBRecipe'):
                        if recipe.get('PK') == recipe_pk:
                            return [(recipe, stat)]

        # Standardní hledání v DBRecipe podle PK nebo názvu
        candidates = []
        for elem in self.db['root'].iter('DBRecipe'):
            pk = elem.get('PK', '')
            name_elem = elem.find('.//Name[@CLASS="String"]')
            name = name_elem.get('VAL', '') if name_elem is not None else ''
            if code == pk or code.lower() == name.lower() or code in name:
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

        exact_pk = [c for c in candidates if c[0].get('PK', '') == code]
        if exact_pk:
            return [(exact_pk[0][0], None)]

        from collections import defaultdict
        by_name = defaultdict(list)
        for elem, name, date in candidates:
            by_name[name].append((elem, date))

        results = []
        for name, versions in by_name.items():
            versions.sort(key=lambda x: x[1] if x[1] else datetime.min, reverse=True)
            results.append((versions[0][0], None))

        return results

    def display_results(self, results, search_code):
        """Zobrazit seznam nalezených receptů v textové oblasti."""
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
        for i, item in enumerate(results, 1):
            if i > 1:
                self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
            # item je tuple (recipe_elem, stat_elem_nebo_None)
            if isinstance(item, tuple):
                recipe_elem, stat_elem = item
            else:
                recipe_elem, stat_elem = item, None
            self.display_recipe(recipe_elem, stat_elem)

    def display_recipe(self, recipe_elem, stat_elem=None):
        """
        Vypsat detail receptu ve formátu:
          RECEPT: název  [míchání #pk]
          Datum míchání: ...
          ────────────────────────────
          1. Název barvy
             -čas nadávkování: HH:MM:SS
             -ventil:          X
             -šarže:           XXXXXX
             -skutečná hmotnost: XXXX g
          2. ...
        """
        pk = recipe_elem.get('PK', 'N/A')
        name_elem = recipe_elem.find('.//Name[@CLASS="String"]')
        name = name_elem.get('VAL', 'Bez názvu') if name_elem is not None else 'Bez názvu'
        amount_elem = recipe_elem.find('.//BezugsMenge[@CLASS="Double"]')
        amount = amount_elem.get('VAL', 'N/A') if amount_elem is not None else 'N/A'
        recipe_pk = recipe_elem.get('PK')

        # Záhlaví
        if stat_elem is not None:
            stat_pk = stat_elem.get('PK', 'N/A')
            mix_date_elem = stat_elem.find('.//MixDate[@CLASS="DBDate"]')
            date_time = 'N/A'
            if mix_date_elem is not None:
                ts = mix_date_elem.get('TIME')
                if ts:
                    try:
                        date_time = datetime.fromtimestamp(int(ts) / 1000.0).strftime('%d.%m.%Y %H:%M:%S')
                    except:
                        pass
            self.result_text.insert(tk.END, f"RECEPT: {name}  [míchání #{stat_pk}]\n", "header")
        else:
            date_elem = recipe_elem.find('.//DazeitC[@CLASS="DBDate"]')
            date_time = 'N/A'
            if date_elem is not None:
                ts = date_elem.get('TIME')
                if ts:
                    try:
                        date_time = datetime.fromtimestamp(int(ts) / 1000.0).strftime('%d.%m.%Y %H:%M:%S')
                    except:
                        pass
            self.result_text.insert(tk.END, f"RECEPT: {name}\n", "header")

        self.result_text.insert(tk.END, f"{'─' * 60}\n")
        self.result_text.insert(tk.END, f"PK: {pk}   |   Ref. množství: {amount} g   |   Datum: {date_time}\n")
        self.result_text.insert(tk.END, f"{'─' * 60}\n\n")

        labels_data = []
        values_data = []
        colors_data = []
        total = 0

        if stat_elem is not None:
            # Složení z DBStatLine — skutečné míchání
            stat_pk = stat_elem.get('PK')
            lines = [l for l in self.db['root'].iter('DBStatLine')
                     if (sr := l.find('.//StatRecipe[@CLASS="DBRef"]')) is not None
                     and sr.get('PK') == stat_pk]

            for i, line in enumerate(lines, 1):
                bc_name_elem = line.find('.//BCName[@CLASS="String"]')
                bc_name = bc_name_elem.get('VAL', '?') if bc_name_elem is not None else '?'

                valve_elem = line.find('.//ValveNr[@CLASS="Integer"]')
                bc_valve = valve_elem.get('VAL', '—') if valve_elem is not None else '—'

                real_val_elem = line.find('.//Real_Value[@CLASS="Integer"]')
                value = int(real_val_elem.get('VAL', '0')) if real_val_elem is not None else 0
                total += value

                charge_elem = line.find('.//Charge[@CLASS="String"]')
                bc_charge = charge_elem.get('VAL', '—') if charge_elem is not None else '—'

                mix_date_elem = line.find('.//MixDate[@CLASS="DBDate"]')
                mix_time = '—'
                if mix_date_elem is not None:
                    ts = mix_date_elem.get('TIME')
                    if ts:
                        try:
                            mix_time = datetime.fromtimestamp(int(ts) / 1000.0).strftime('%d.%m.%Y %H:%M:%S')
                        except:
                            pass

                labels_data.append(bc_name)
                values_data.append(value)
                colors_data.append(self.get_color_for_name(bc_name))

                self.result_text.insert(tk.END, f"{i}. {bc_name}\n", "ing_name")
                self.result_text.insert(tk.END, f"   -čas nadávkování:    {mix_time}\n", "ing_detail")
                self.result_text.insert(tk.END, f"   -ventil:             {bc_valve}\n", "ing_detail")
                self.result_text.insert(tk.END, f"   -šarže:              {bc_charge}\n", "ing_detail")
                self.result_text.insert(tk.END, f"   -skutečná hmotnost:  {value / 1000:.3f} kg\n\n", "ing_detail")

        else:
            # Složení ze statického receptu (DBLine) — použij lookup tabulku
            lines = self._lines_by_recipe.get(recipe_pk, [])

            for i, line in enumerate(lines, 1):
                value_elem = line.find('.//Value[@CLASS="Integer"]')
                value = int(value_elem.get('VAL', '0')) if value_elem is not None else 0
                total += value

                basecolor_ref = line.find('.//BaseColor[@CLASS="DBRef"]')
                if basecolor_ref is None:
                    continue
                bc = self.find_basecolor(basecolor_ref.get('PK'))
                if bc is None:
                    continue

                bc_name_elem = bc.find('.//Name[@CLASS="String"]')
                bc_name = bc_name_elem.get('VAL', '?') if bc_name_elem is not None else '?'

                bc_valve_elem = bc.find('.//ValveNr[@CLASS="Integer"]')
                bc_valve = bc_valve_elem.get('VAL', '—') if bc_valve_elem is not None else '—'

                bc_charge_elem = bc.find('.//Charge[@CLASS="String"]')
                bc_charge = bc_charge_elem.get('VAL', '—') if bc_charge_elem is not None else '—'

                labels_data.append(bc_name)
                values_data.append(value)
                colors_data.append(self.get_color_for_name(bc_name))

                self.result_text.insert(tk.END, f"{i}. {bc_name}\n", "ing_name")
                self.result_text.insert(tk.END, f"   -ventil:             {bc_valve}\n", "ing_detail")
                self.result_text.insert(tk.END, f"   -šarže:              {bc_charge}\n", "ing_detail")
                self.result_text.insert(tk.END, f"   -ref. hmotnost:      {value / 1000:.3f} kg\n\n", "ing_detail")

        if lines:
            self.result_text.insert(tk.END, f"{'─' * 60}\n")
            self.result_text.insert(tk.END, f"CELKEM: {total / 1000:.3f} kg\n\n", "total")

        self.display_recipe_history(recipe_pk, name)

        if MATPLOTLIB_AVAILABLE and values_data:
            self.draw_pie_chart(labels_data, values_data, colors_data, name)

        # Tagy
        self.result_text.tag_config("header",     font=(self.font_mono[0], 15, "bold"), foreground="#1a5276")
        self.result_text.tag_config("ing_name",   font=(self.font_mono[0], 12, "bold"))
        self.result_text.tag_config("ing_detail", font=self.font_mono)
        self.result_text.tag_config("total",      font=(self.font_mono[0], 12, "bold"), foreground="green")
        self.result_text.tag_config("subheader",  font=(self.font_mono[0], 13, "bold"))
        self.result_text.tag_config("ingredient", font=self.font_mono)
        self.result_text.tag_config("history_header", font=(self.font_mono[0], 13, "bold"), foreground="purple")
        self.result_text.tag_config("history_item",   font=self.font_mono_sm, foreground="#555")

    def display_recipe_history(self, recipe_pk, recipe_name):
        """
        Zobrazit historii míchání receptu z tabulky DBStatRecipe.

        Seřadí záznamy od nejnovějšího a zobrazí max. 10 položek
        s relativním časem (Dnes / Včera / Před X dny...).
        """
        history_items = []  # seznam datetime objektů — kdy byl recept namíchán
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
        """
        Přiřadit barvu pro koláčový graf podle názvu složky.

        Jednoduché mapování klíčových slov (anglicky i česky) na hex barvy.
        Pokud název neodpovídá žádnému klíčovému slovu, vrátí šedou.
        """
        name_lower = name.lower()  # převést na malá písmena pro porovnání
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
        """
        Vykreslit koláčový graf složení receptu.

        Popisky obsahují název složky a procento. Uvnitř výseče je
        zobrazeno skutečné množství v gramech (přepočítáno z procent).
        """
        self.figure.clear()  # vymazat předchozí graf
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
        """
        Filtrovat recepty podle rozsahu data vytvoření (záložka „Filtrování podle data").

        Datum se čte z elementu DazeitC (Unix timestamp v milisekundách).
        Výsledky jsou seřazeny od nejnovějšího.
        """
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
        """Vymazat výsledky v záložce filtrování podle data."""
        for item in self.date_tree.get_children():
            self.date_tree.delete(item)
        self.status_bar.config(text="Připraveno")

    def show_recipe_detail(self, event):
        """Dvojklik v tabulce filtrování podle data — přepnout na detail receptu."""
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
        """
        Pokročilé filtrování — kombinuje datum+čas, ventil a barvu.
        Výsledky zobrazí v tabulce, dvojklik otevře přehledný detail.
        Rychlost zajišťují předpočítané lookup tabulky — žádné O(n²).
        """
        if not self.db:
            messagebox.showwarning("Upozornění", "Nejprve načtěte XML soubor!")
            return

        start_date_str = self.adv_start_date.get().strip()
        end_date_str   = self.adv_end_date.get().strip()
        start_time_str = self.adv_start_time.get().strip()
        end_time_str   = self.adv_end_time.get().strip()
        valve_str      = self.adv_valve.get().strip()
        color_str      = self.adv_color.get().strip().lower()

        try:
            start_datetime = None
            end_datetime   = None
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

            # Filtr ventilu — O(1) lookup
            if valve_str:
                if valve_str not in self._recipe_valves.get(recipe_pk, []):
                    continue

            # Filtr barvy — O(1) lookup
            if color_str:
                colors = self._recipe_colors.get(recipe_pk, [])
                if not any(color_str in c.lower() for c in colors):
                    continue

            results.append((recipe, recipe_datetime))

        results.sort(key=lambda x: x[1], reverse=True)

        for recipe, recipe_datetime in results:
            pk        = recipe.get('PK', 'N/A')
            name_elem = recipe.find('.//Name[@CLASS="String"]')
            name      = name_elem.get('VAL', 'Bez názvu') if name_elem is not None else 'Bez názvu'
            amount_elem = recipe.find('.//BezugsMenge[@CLASS="Double"]')
            amount    = amount_elem.get('VAL', 'N/A') if amount_elem is not None else 'N/A'
            date_str  = recipe_datetime.strftime('%d.%m.%Y')
            time_str  = recipe_datetime.strftime('%H:%M:%S')
            valves    = self._recipe_valves.get(pk, [])
            charges   = self._recipe_charges.get(pk, [])
            self.adv_tree.insert('', tk.END,
                values=(pk, name, amount, date_str, time_str,
                        ', '.join(sorted(valves)), ', '.join(charges)),
                tags=(pk,))

        self.status_bar.config(text=f"✓ Nalezeno {len(results)} receptů")

    def get_recipe_valves(self, recipe_pk):
        """Vrátit seřazený seznam čísel ventilů pro daný recept (z lookup tabulky)."""
        return sorted(self._recipe_valves.get(recipe_pk, []))

    def get_recipe_charges(self, recipe_pk):
        """Vrátit seznam šarží všech složek daného receptu (z lookup tabulky)."""
        return self._recipe_charges.get(recipe_pk, [])

    def find_basecolor(self, pk):
        """Vrátit DBBaseColor element podle PK (z lookup tabulky, O(1))."""
        return self._basecolor_by_pk.get(pk)

    def clear_advanced_filter(self):
        """Vymazat výsledky v záložce pokročilého filtrování."""
        for item in self.adv_tree.get_children():
            self.adv_tree.delete(item)
        self.status_bar.config(text="Připraveno")

    def show_advanced_recipe_detail(self, event):
        """Dvojklik v tabulce pokročilého filtrování — přepnout na přehledný detail receptu."""
        selection = self.adv_tree.selection()
        if not selection:
            return
        item = self.adv_tree.item(selection[0])
        pk = str(item['values'][0])
        for recipe in self.db['root'].iter('DBRecipe'):
            if recipe.get('PK') == pk:
                self.notebook.select(0)
                self.result_text.delete(1.0, tk.END)
                self.display_recipe(recipe, None)
                break

    def export_results(self, source):
        """
        Exportovat aktuálně zobrazené výsledky do souboru.

        source: 'search' = záložka Vyhledávání (text)
                'date'   = záložka Filtrování podle data (Treeview)
                'advanced' = záložka Pokročilé filtrování (Treeview)
        """
        # Ověřit, že jsou data k exportu
        if source == 'search':
            has_data = bool(self.result_text.get(1.0, tk.END).strip())
        elif source == 'date':
            has_data = bool(self.date_tree.get_children())
        else:
            has_data = bool(self.adv_tree.get_children())

        if not has_data:
            messagebox.showwarning("Export",
                "Nejsou zadna data k exportu.\n"
                "Nejprve provedte vyhledavani nebo filtrovani.")
            return

        # Dialog pro výběr formátu
        fmt_win = tk.Toplevel(self.root)
        fmt_win.title("Exportovat jako...")
        fmt_win.geometry("320x180")
        fmt_win.resizable(False, False)
        fmt_win.grab_set()
        fmt_win.transient(self.root)

        frame = ttk.Frame(fmt_win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Vyberte format exportu:", font=self.font_ui_bold).pack(pady=(0, 15))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack()

        def do_export(fmt):
            fmt_win.destroy()
            self._do_export(fmt, source)

        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(btn_frame, text="TXT", command=lambda: do_export('txt'),
                       bootstyle="secondary", width=10).pack(side=tk.LEFT, padx=8)
            ttk.Button(btn_frame, text="CSV", command=lambda: do_export('csv'),
                       bootstyle="info", width=10).pack(side=tk.LEFT, padx=8)
            pdf_btn = ttk.Button(btn_frame, text="PDF", command=lambda: do_export('pdf'),
                                 bootstyle="danger", width=10)
        else:
            ttk.Button(btn_frame, text="TXT", command=lambda: do_export('txt'),
                       width=10).pack(side=tk.LEFT, padx=8)
            ttk.Button(btn_frame, text="CSV", command=lambda: do_export('csv'),
                       width=10).pack(side=tk.LEFT, padx=8)
            pdf_btn = ttk.Button(btn_frame, text="PDF", command=lambda: do_export('pdf'), width=10)

        pdf_btn.pack(side=tk.LEFT, padx=8)
        if not REPORTLAB_AVAILABLE:
            pdf_btn.config(state='disabled')
            ttk.Label(frame, text="PDF: pip install reportlab",
                      font=self.font_ui_sm, foreground="gray").pack(pady=(10, 0))

    def _do_export(self, fmt, source):
        """Provést samotný export do zvoleného formátu."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"export_{timestamp}"

        # Určit zdroj dat a záhlaví sloupců
        if source == 'search':
            # Záložka Vyhledávání — exportuje text z result_text
            tree = None
            headers = []
            text_content = self.result_text.get(1.0, tk.END).strip()
        elif source == 'date':
            tree = self.date_tree
            headers = ["PK", "Nazev", "Mnozstvi (g)", "Datum"]
            text_content = None
        else:  # advanced
            tree = self.adv_tree
            headers = ["PK", "Nazev", "Mnozstvi (g)", "Datum", "Cas", "Ventily", "Sarze"]
            text_content = None

        try:
            if fmt == 'txt':
                filepath = filedialog.asksaveasfilename(
                    title="Ulozit jako TXT",
                    defaultextension=".txt",
                    initialfile=default_name + ".txt",
                    filetypes=[("Textove soubory", "*.txt"), ("Vsechny soubory", "*.*")]
                )
                if not filepath:
                    return
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("Databaze barev - Model Obaly Hostinne\n")
                    f.write(f"Export: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                    f.write("=" * 70 + "\n\n")
                    if tree is not None:
                        f.write(self._treeview_to_text(tree))
                    else:
                        f.write(text_content)
                messagebox.showinfo("Export", f"Soubor ulozen:\n{filepath}")

            elif fmt == 'csv':
                filepath = filedialog.asksaveasfilename(
                    title="Ulozit jako CSV",
                    defaultextension=".csv",
                    initialfile=default_name + ".csv",
                    filetypes=[("CSV soubory", "*.csv"), ("Vsechny soubory", "*.*")]
                )
                if not filepath:
                    return
                if tree is not None:
                    rows = self._treeview_to_csv_rows(tree)
                else:
                    rows = self._parse_content_to_rows(text_content, source)
                    headers = ["Recept", "PK", "Datum", "Slozka", "Ventil", "Sarze", "Mnozstvi (g)"]
                # utf-8-sig = BOM, Excel na Windows ho spravne otevře
                with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(headers)
                    for row in rows:
                        writer.writerow(row)
                messagebox.showinfo("Export",
                    f"Soubor ulozen:\n{filepath}\n\nRadku dat: {len(rows)}")

            elif fmt == 'pdf':
                if not REPORTLAB_AVAILABLE:
                    messagebox.showerror("PDF nedostupne",
                        "Knihovna reportlab neni nainstalovana.\n"
                        "Spustte: pip install reportlab")
                    return
                filepath = filedialog.asksaveasfilename(
                    title="Ulozit jako PDF",
                    defaultextension=".pdf",
                    initialfile=default_name + ".pdf",
                    filetypes=[("PDF soubory", "*.pdf"), ("Vsechny soubory", "*.*")]
                )
                if not filepath:
                    return
                if tree is not None:
                    pdf_content = self._treeview_to_text(tree)
                else:
                    pdf_content = text_content
                self._export_pdf(pdf_content, filepath)
                messagebox.showinfo("Export", f"Soubor ulozen:\n{filepath}")

        except PermissionError:
            messagebox.showerror("Chyba exportu",
                "Nelze zapsat soubor.\n"
                "Soubor je pravdepodobne otevreny v jinem programu.\n"
                "Zavrte soubor a zkuste znovu.")
        except Exception as e:
            messagebox.showerror("Chyba exportu", f"Export selhal:\n{type(e).__name__}: {e}")

    def _treeview_to_csv_rows(self, tree):
        """Převést všechny řádky Treeview na seznam seznamů pro CSV."""
        rows = []
        for item_id in tree.get_children():
            values = tree.item(item_id, 'values')
            rows.append(list(values))
        return rows

    def _treeview_to_text(self, tree):
        """Převést Treeview na čitelný textový výstup pro TXT/PDF export."""
        lines = []
        # Záhlaví sloupců
        cols = tree['columns']
        headers = [tree.heading(c)['text'] for c in cols]
        widths = [tree.column(c)['width'] for c in cols]

        # Záhlaví tabulky
        header_line = '  '.join(h.ljust(max(w // 7, len(h))) for h, w in zip(headers, widths))
        lines.append(header_line)
        lines.append('-' * len(header_line))

        for item_id in tree.get_children():
            values = tree.item(item_id, 'values')
            row_line = '  '.join(str(v).ljust(max(w // 7, len(h)))
                                 for v, w, h in zip(values, widths, headers))
            lines.append(row_line)

        lines.append('')
        lines.append(f"Celkem záznamů: {len(tree.get_children())}")
        return '\n'.join(lines)

    def _parse_content_to_rows(self, content, source):
        """
        Převést textový obsah na řádky pro CSV export.
        Parsuje strukturu výstupu a vrátí seznam řádků
        [recept, pk, datum, složka, ventil, šarže, množství].
        """
        rows = []
        current_recipe = ''
        current_pk = ''
        current_date = ''

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('─') or line.startswith('='):
                continue

            # Záhlaví receptu — "1.  286  (PK: 18)" nebo "RECEPT: 286"
            if line.startswith('RECEPT:') or (line and line[0].isdigit() and '.  ' in line):
                if 'PK:' in line:
                    # formát pokročilého filtrování: "1.  286  (PK: 18)"
                    parts = line.split('(PK:')
                    current_recipe = parts[0].split('.', 1)[-1].strip() if '.' in parts[0] else parts[0].strip()
                    current_pk = parts[1].replace(')', '').strip() if len(parts) > 1 else ''
                else:
                    # formát vyhledávání: "RECEPT: 286  [míchání #12979]"
                    current_recipe = line.replace('RECEPT:', '').split('[')[0].strip()
                    current_pk = ''
                current_date = ''

            # Datum
            elif 'Datum' in line or '📅' in line:
                current_date = line.split(':', 1)[-1].strip() if ':' in line else ''

            # Složka — "• Blue 17" nebo "  • Blue 17"
            elif line.startswith('•'):
                ingredient = line.lstrip('• ').strip()
                rows.append([current_recipe, current_pk, current_date, ingredient, '', '', ''])

            # Detail složky — "Ventil: 14   |   Šarže: 2BADSL0782   |   Množství: 800025 g"
            elif 'Ventil:' in line and rows:
                parts = [p.strip() for p in line.split('|')]
                ventil = ''
                sarze = ''
                mnozstvi = ''
                for p in parts:
                    if p.startswith('Ventil:'):
                        ventil = p.replace('Ventil:', '').strip()
                    elif p.startswith('Šarže:'):
                        sarze = p.replace('Šarže:', '').strip()
                    elif p.startswith('Množství:'):
                        mnozstvi = p.replace('Množství:', '').replace('g', '').strip()
                # Doplnit do posledního řádku
                rows[-1][4] = ventil
                rows[-1][5] = sarze
                rows[-1][6] = mnozstvi

        return rows

    def _export_pdf(self, content, filepath):
        """Exportovat obsah do PDF pomocí reportlab s podporou české diakritiky."""
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Zaregistrovat DejaVuSans — podporuje českou diakritiku.
        # Font je přibalen ve složce fonts/ vedle gui.py (funguje i v EXE).
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_regular = os.path.join(base_dir, 'fonts', 'DejaVuSans.ttf')
        font_bold    = os.path.join(base_dir, 'fonts', 'DejaVuSans-Bold.ttf')

        # Fallback: systémová umístění na Linuxu a Windows
        if not os.path.exists(font_regular):
            candidates = [
                # Linux
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/TTF/DejaVuSans.ttf',
                # Windows
                r'C:\Windows\Fonts\DejaVuSans.ttf',
                r'C:\Windows\Fonts\arial.ttf',
            ]
            for candidate in candidates:
                if os.path.exists(candidate):
                    font_regular = candidate
                    # Zkusit najít bold variantu vedle regular
                    bold_candidate = candidate.replace('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf') \
                                              .replace('arial.ttf', 'arialbd.ttf')
                    font_bold = bold_candidate if os.path.exists(bold_candidate) else candidate
                    break

        fn      = 'Helvetica'
        fn_bold = 'Helvetica-Bold'
        if os.path.exists(font_regular):
            try:
                pdfmetrics.registerFont(TTFont('DejaVu',      font_regular))
                pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_bold))
                fn      = 'DejaVu'
                fn_bold = 'DejaVu-Bold'
            except Exception:
                pass  # fallback na Helvetica (bez diakritiky, ale aspoň PDF vznikne)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=20*mm, rightMargin=20*mm,
            topMargin=20*mm, bottomMargin=20*mm
        )

        style_title = ParagraphStyle('title',
            fontSize=14, fontName=fn_bold,
            textColor=rl_colors.HexColor('#1a5276'), spaceAfter=4)
        style_subtitle = ParagraphStyle('subtitle',
            fontSize=9, fontName=fn,
            textColor=rl_colors.HexColor('#555555'), spaceAfter=10)
        style_recipe = ParagraphStyle('recipe',
            fontSize=12, fontName=fn_bold,
            textColor=rl_colors.HexColor('#1a5276'), spaceBefore=10, spaceAfter=3)
        style_date = ParagraphStyle('date',
            fontSize=9, fontName=fn,
            textColor=rl_colors.HexColor('#555555'), spaceAfter=4)
        style_ingredient = ParagraphStyle('ingredient',
            fontSize=10, fontName=fn_bold,
            leftIndent=10, spaceBefore=4, spaceAfter=1)
        style_detail = ParagraphStyle('detail',
            fontSize=9, fontName=fn,
            textColor=rl_colors.HexColor('#333333'),
            leftIndent=20, spaceAfter=2)
        style_normal = ParagraphStyle('normal',
            fontSize=9, fontName=fn,
            textColor=rl_colors.HexColor('#333333'), spaceAfter=2)

        story = []

        # Hlavička
        story.append(Paragraph("Databaze barev - Model Obaly Hostinne", style_title))
        story.append(Paragraph(f"Export: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", style_subtitle))
        story.append(HRFlowable(width="100%", thickness=1, color=rl_colors.HexColor('#1a5276')))
        story.append(Spacer(1, 6*mm))

        def clean(text):
            """Odstranit znaky které reportlab neumí zobrazit (emoji, surrogates)."""
            result = []
            for ch in text:
                cp = ord(ch)
                # Přeskočit surrogáty a emoji bloky
                if 0xD800 <= cp <= 0xDFFF:
                    continue
                if cp > 0xFFFF and fn == 'Helvetica':
                    continue  # Helvetica nezvládne mimo BMP
                # Přeskočit emoji (různé bloky)
                if (0x1F300 <= cp <= 0x1FAFF) or (0x2600 <= cp <= 0x27BF):
                    continue
                result.append(ch)
            return ''.join(result)

        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 2*mm))
                continue
            if stripped.startswith('─') or stripped.startswith('=') or stripped.startswith('-' * 5):
                story.append(HRFlowable(width="100%", thickness=0.5,
                                        color=rl_colors.HexColor('#cccccc')))
                continue
            cleaned = clean(stripped)
            if not cleaned:
                continue
            if stripped.startswith('RECEPT:') or (stripped and stripped[0].isdigit() and '.  ' in stripped):
                story.append(Paragraph(cleaned, style_recipe))
            elif 'Datum' in stripped or stripped.startswith('PK:'):
                story.append(Paragraph(cleaned, style_date))
            elif len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in '.':
                story.append(Paragraph(cleaned, style_ingredient))
            elif stripped.startswith('-'):
                story.append(Paragraph(cleaned, style_detail))
            else:
                story.append(Paragraph(cleaned, style_normal))

        doc.build(story)

    def clear_search(self):
        """Vymazat vstupní pole vyhledávání a vrátit focus."""
        self.search_entry.delete(0, tk.END)
        self.search_entry.focus()

    def _show_about(self):
        """Zobrazit okno O aplikaci s brandingem Model Group."""
        about = tk.Toplevel(self.root)
        about.title("O aplikaci")
        about.geometry("420x300")
        about.resizable(False, False)
        about.grab_set()  # modální okno

        frame = ttk.Frame(about, padding=25)
        frame.pack(fill=tk.BOTH, expand=True)

        # Logo v dialogu
        if self._logo_image:
            ttk.Label(frame, image=self._logo_image).pack(pady=(0, 10))

        ttk.Label(frame, text="🎨 Databáze barev",
                  font=(self.font_ui[0], 16, "bold")).pack(pady=(0, 4))
        ttk.Label(frame, text="Nástroj pro správu tiskových inkoustů",
                  font=self.font_ui).pack()

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=15)

        ttk.Label(frame, text="Model Obaly a.s. — závod Hostinné",
                  font=self.font_ui_bold).pack()
        ttk.Label(frame, text="Model Group  |  modelgroup.com",
                  font=self.font_ui, foreground="gray").pack(pady=2)

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=15)

        ttk.Label(frame, text="Verze 1.0  |  2024",
                  font=self.font_ui_sm, foreground="gray").pack()
        ttk.Label(frame, text="Vytvořil: Filip Pavelec",
                  font=self.font_ui_sm, foreground="gray").pack(pady=(2, 0))

        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(frame, text="Zavřít", command=about.destroy,
                       bootstyle="secondary", width=12).pack(pady=(15, 0))
        else:
            ttk.Button(frame, text="Zavřít", command=about.destroy,
                       width=12).pack(pady=(15, 0))


def main():
    """Vstupní bod aplikace — vytvoří okno a spustí hlavní smyčku."""
    if TTKBOOTSTRAP_AVAILABLE:
        root = ttk.Window(themename="cosmo")
    else:
        root = tk.Tk()

    app = ColorDatabaseGUI(root)

    # Přidat menu lištu s brandingem
    menubar = tk.Menu(root)
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="O aplikaci", command=app._show_about)
    help_menu.add_separator()
    help_menu.add_command(label="Model Group — modelgroup.com",
                          command=lambda: __import__('webbrowser').open('https://www.modelgroup.com'))
    menubar.add_cascade(label="Nápověda", menu=help_menu)
    root.config(menu=menubar)

    root.mainloop()


if __name__ == "__main__":
    main()
