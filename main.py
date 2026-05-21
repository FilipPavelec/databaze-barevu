#!/usr/bin/env python3
"""
Nástroj pro vyhledávání a filtrování XML databáze
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import os


class XMLDatabase:
    def __init__(self, xml_file):
        """Načíst XML databázi ze souboru."""
        self.xml_file = xml_file
        self.tree = None
        self.root = None
        self.load_database()
    
    def load_database(self):
        """Načíst XML soubor."""
        try:
            self.tree = ET.parse(self.xml_file)
            self.root = self.tree.getroot()
            print(f"✓ Načtena XML databáze: {self.xml_file}")
        except FileNotFoundError:
            print(f"✗ Chyba: Soubor '{self.xml_file}' nebyl nalezen")
            sys.exit(1)
        except ET.ParseError as e:
            print(f"✗ Chyba při parsování XML: {e}")
            sys.exit(1)
    
    def search(self, keyword):
        """Vyhledat klíčové slovo ve všech textech."""
        results = []
        for elem in self.root.iter():
            if elem.text and keyword.lower() in elem.text.lower():
                results.append(elem)
            for attr_value in elem.attrib.values():
                if keyword.lower() in str(attr_value).lower():
                    results.append(elem)
                    break
        return results
    
    def search_by_code(self, code):
        """Vyhledat recept podle kódu (Name nebo PK)."""
        results = []
        code = code.strip()
        
        # Hledat v DBRecipe elementech
        for elem in self.root.iter('DBRecipe'):
            # Zkontrolovat PK atribut
            pk = elem.get('PK', '')
            # Zkontrolovat Name element
            name_elem = elem.find('.//Name[@CLASS="String"]')
            name = name_elem.get('VAL', '') if name_elem is not None else ''
            
            # Shoda pokud kód odpovídá PK nebo Name
            if code == pk or code.lower() == name.lower() or code in name:
                results.append(elem)
        
        return results
    
    def filter_by_date(self, start_date=None, end_date=None, date_field='DaZeitC'):
        """Filtrovat záznamy podle datumu."""
        results = []
        
        for elem in self.root.iter():
            # Check for date in attributes or child elements
            date_text = elem.get(date_field)
            
            # Also check child elements with date field
            if not date_text:
                date_elem = elem.find(f".//{date_field}")
                if date_elem is not None:
                    date_text = date_elem.get('TIME')
            
            if date_text:
                try:
                    # Try multiple date formats
                    elem_date = self._parse_date(date_text)
                    
                    if elem_date:
                        if start_date and end_date:
                            if start_date <= elem_date <= end_date:
                                results.append(elem)
                        elif start_date:
                            if elem_date >= start_date:
                                results.append(elem)
                        elif end_date:
                            if elem_date <= end_date:
                                results.append(elem)
                except:
                    continue
        
        return results
    
    def _parse_date(self, date_string):
        """Pokusit se načíst datum z různých formátů včetně timestampů."""
        # Handle Unix timestamp in milliseconds (from TIME attribute)
        try:
            timestamp = int(date_string)
            # Convert milliseconds to seconds
            return datetime.fromtimestamp(timestamp / 1000.0)
        except (ValueError, TypeError):
            pass
        
        # Try standard date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        return None
    
    def display_results(self, results):
        """Zobrazit výsledky vyhledávání."""
        if not results:
            print("\nŽádné výsledky nenalezeny.")
            return
        
        print(f"\n{'='*60}")
        print(f"Nalezeno {len(results)} výsledků")
        print(f"{'='*60}\n")
        
        for i, elem in enumerate(results, 1):
            print(f"Výsledek #{i}:")
            
            if elem.tag == 'DBRecipe':
                self._display_recipe(elem)
            else:
                # Obecné zobrazení pro jiné elementy
                print(f"  Tag: {elem.tag}")
                if elem.attrib:
                    print(f"  Atributy: {elem.attrib}")
                if elem.text and elem.text.strip():
                    print(f"  Text: {elem.text.strip()}")
                
                # Zobrazit podřízené elementy
                for child in elem:
                    if child.text and child.text.strip():
                        print(f"  {child.tag}: {child.text.strip()}")
            print()
    
    def _display_recipe(self, recipe_elem):
        """Zobrazit detaily receptu včetně složení."""
        # Získat základní informace o receptu
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
                    date_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date_time = timestamp
        
        print(f"  Recept PK: {pk}")
        print(f"  Název: {name}")
        print(f"  Množství: {amount} g")
        print(f"  Datum: {date_time}")
        
        # Najít všechny DBLine elementy, které patří k tomuto receptu
        recipe_pk = recipe_elem.get('PK')
        lines = []
        
        for line in self.root.iter('DBLine'):
            recipe_ref = line.find('.//Recipe[@CLASS="DBRef"]')
            if recipe_ref is not None and recipe_ref.get('PK') == recipe_pk:
                lines.append(line)
        
        if lines:
            print(f"\n  Složení ({len(lines)} složek):")
            print(f"  {'-'*56}")
            
            for line in lines:
                # Získat množství
                value_elem = line.find('.//Value[@CLASS="Integer"]')
                value = value_elem.get('VAL', '0') if value_elem is not None else '0'
                
                # Získat odkaz na základní barvu
                basecolor_ref = line.find('.//BaseColor[@CLASS="DBRef"]')
                if basecolor_ref is not None:
                    bc_pk = basecolor_ref.get('PK')
                    
                    # Najít základní barvu podle PK
                    basecolor = self._find_basecolor(bc_pk)
                    if basecolor:
                        bc_name_elem = basecolor.find('.//Name[@CLASS="String"]')
                        bc_name = bc_name_elem.get('VAL', f'Barva PK={bc_pk}') if bc_name_elem is not None else f'Barva PK={bc_pk}'
                        
                        bc_valve_elem = basecolor.find('.//ValveNr[@CLASS="Integer"]')
                        bc_valve = bc_valve_elem.get('VAL', '') if bc_valve_elem is not None else ''
                        
                        if bc_valve:
                            print(f"    • {bc_name} (Ventil {bc_valve}): {value} g")
                        else:
                            print(f"    • {bc_name}: {value} g")
                    else:
                        print(f"    • Barva PK={bc_pk}: {value} g")
    
    def _find_basecolor(self, pk):
        """Najít základní barvu podle PK."""
        for basecolor in self.root.iter('DBBaseColor'):
            if basecolor.get('PK') == pk:
                return basecolor
        return None


def main():
    """Hlavní funkce."""
    print("=" * 60)
    print("Nástroj pro vyhledávání a filtrování XML databáze")
    print("=" * 60)
    
    # Získat cestu k XML souboru
    if len(sys.argv) > 1:
        xml_file = sys.argv[1]
    else:
        xml_file = input("\nZadejte cestu k XML souboru: ").strip()
    
    if not os.path.exists(xml_file):
        print(f"✗ Soubor nenalezen: {xml_file}")
        sys.exit(1)
    
    # Načíst databázi
    db = XMLDatabase(xml_file)
    
    # Hlavní menu
    while True:
        print("\n" + "=" * 60)
        print("Možnosti:")
        print("  1. Vyhledat podle klíčového slova")
        print("  2. Vyhledat podle kódu receptu (Name nebo PK)")
        print("  3. Režim skeneru čárových kódů")
        print("  4. Filtrovat podle data")
        print("  5. Znovu načíst databázi")
        print("  6. Ukončit")
        print("=" * 60)
        
        choice = input("\nVyberte možnost (1-6): ").strip()
        
        if choice == '1':
            keyword = input("Zadejte klíčové slovo: ").strip()
            if keyword:
                results = db.search(keyword)
                db.display_results(results)
        
        elif choice == '2':
            code = input("Zadejte kód receptu (např. 315 nebo 545): ").strip()
            if code:
                results = db.search_by_code(code)
                db.display_results(results)
        
        elif choice == '3':
            scanner_mode(db)
        
        elif choice == '4':
            date_field = input("Zadejte název pole s datem (výchozí: 'DaZeitC'): ").strip() or 'DaZeitC'
            start_str = input("Zadejte počáteční datum (RRRR-MM-DD) nebo nechte prázdné: ").strip()
            end_str = input("Zadejte koncové datum (RRRR-MM-DD) nebo nechte prázdné: ").strip()
            
            start_date = None
            end_date = None
            
            if start_str:
                try:
                    start_date = datetime.strptime(start_str, '%Y-%m-%d')
                except ValueError:
                    print("✗ Neplatný formát počátečního data")
                    continue
            
            if end_str:
                try:
                    end_date = datetime.strptime(end_str, '%Y-%m-%d')
                except ValueError:
                    print("✗ Neplatný formát koncového data")
                    continue
            
            results = db.filter_by_date(start_date, end_date, date_field)
            db.display_results(results)
        
        elif choice == '5':
            db.load_database()
        
        elif choice == '6':
            print("\nNa shledanou!")
            break
        
        else:
            print("✗ Neplatná volba")


def scanner_mode(db):
    """Režim pro čtečku čárových kódů."""
    print("\n" + "=" * 60)
    print("REŽIM SKENERU ČÁROVÝCH KÓDŮ")
    print("=" * 60)
    print("\nNaskenujte čárový kód nebo zadejte kód ručně.")
    print("Pro návrat do hlavního menu zadejte 'q' nebo 'exit'.\n")
    
    while True:
        code = input("Čárový kód: ").strip()
        
        if code.lower() in ['q', 'quit', 'exit', 'konec']:
            print("\nNávrat do hlavního menu...")
            break
        
        if not code:
            continue
        
        # Zpracovat naskenovaný kód
        # Čárový kód může obsahovat různé formáty, zkusíme extrahovat číslo
        processed_code = process_barcode(code)
        
        print(f"\n→ Hledám kód: {processed_code}")
        print("-" * 60)
        
        results = db.search_by_code(processed_code)
        
        if results:
            db.display_results(results)
        else:
            # Zkusit vyhledat jako klíčové slovo
            print("Žádný přesný výsledek, zkouším obecné vyhledávání...")
            results = db.search(processed_code)
            if results:
                db.display_results(results)
            else:
                print("✗ Žádné výsledky nenalezeny.")
        
        print("\n" + "=" * 60)


def process_barcode(barcode):
    """Zpracovat čárový kód a extrahovat relevantní část."""
    # Odstranit bílé znaky
    barcode = barcode.strip()
    
    # Pokud obsahuje tečky, vzít část před tečkami
    if '.' in barcode:
        code = barcode.split('.')[0].strip()
        if code:
            return code
    
    # Pokud obsahuje #, rozdělit a vzít část před #
    if '#' in barcode:
        code = barcode.split('#')[0].strip()
        # Odstranit tečky na konci
        code = code.rstrip('.')
        if code:
            return code
    
    # Odstranit úvodní nuly (pokud to není jen "0")
    if barcode.startswith('0') and len(barcode) > 1:
        barcode = barcode.lstrip('0') or '0'
    
    return barcode


if __name__ == "__main__":
    main()