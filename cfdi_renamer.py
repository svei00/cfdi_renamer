#!/usr/bin/env python3
"""
CFDI PDF/XML Renamer
Renames Mexican payroll PDF and XML files based on RFC and payment date.

Naming convention (month-anchored, auto-detected from the XML):
    RFC-YYYY-MM[-<suffix>].extension

The period suffix is derived from nomina12:Receptor/@PeriodicidadPago
(the SAT c_PeriodicidadPago catalog) and the day of FechaPago:

    04 Quincenal  -> Q1 (day 1-15) / Q2 (day 16-31)
    02 Semanal    -> S1..S5         ceil(day/7)
    03 Catorcenal -> C1..C3         ceil(day/14)
    10 Decenal    -> D1..D3         ceil(day/10)
    01 Diario     -> J01..J31       day of month (J = Jornal)
    05 Mensual    -> (no suffix)    RFC-YYYY-MM
    06 Bimestral  -> B              RFC-YYYY-MM-B
    99 / unknown  -> falls back to Q1/Q2 by day, logs a warning
"""

import os
import re
import sys
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from tkinter import Tk, Button, Label, filedialog, Text, Scrollbar, Frame
from tkinter import ttk
import tkinter as tk

# SAT c_PeriodicidadPago code -> internal period type
PERIODICIDAD = {
    '01': 'diario',
    '02': 'semanal',
    '03': 'catorcenal',
    '04': 'quincenal',
    '05': 'mensual',
    '06': 'bimestral',
    '10': 'decenal',
}

# Regex fragment matching any suffix this app produces (used for idempotency)
SUFFIX_RE = r'(Q[12]|S[1-5]|C[1-3]|D[1-3]|J\d{2}|B)'


def get_config_path():
    """Per-user config file, robust whether run as script or frozen exe."""
    base = os.environ.get('APPDATA') or str(Path.home())
    cfg_dir = Path(base) / 'CFDI_Renamer'
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir / 'config.json'


def load_config():
    try:
        with open(get_config_path(), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    try:
        with open(get_config_path(), 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


class CFDIRenamer:
    def __init__(self):
        self.log_entries = []
        self.stats = {
            'total_checked': 0,
            'renamed': 0,
            'skipped_correct': 0,
            'warnings': 0,
            'errors': 0
        }

    def is_already_renamed(self, filename):
        """Check if file already follows RFC-YYYY-MM[-suffix] pattern"""
        pattern = r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}-\d{4}-\d{2}(-' + SUFFIX_RE + r')?\.(pdf|xml)$'
        return bool(re.match(pattern, filename, re.IGNORECASE))

    def extract_data(self, xml_path):
        """Extract RFC, FechaPago and PeriodicidadPago from a CFDI nomina XML."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            namespaces = {
                'cfdi': 'http://www.sat.gob.mx/cfd/4',
                'nomina12': 'http://www.sat.gob.mx/nomina12'
            }

            rfc = None
            receptor = root.find('.//cfdi:Receptor', namespaces)
            if receptor is not None:
                rfc = receptor.get('Rfc')

            fecha_pago = None
            fecha_final = None
            nomina = root.find('.//nomina12:Nomina', namespaces)
            if nomina is not None:
                fecha_pago = nomina.get('FechaPago')
                fecha_final = nomina.get('FechaFinalPago')

            # PeriodicidadPago lives on the nomina12:Receptor node
            periodicidad_code = None
            nom_receptor = root.find('.//nomina12:Receptor', namespaces)
            if nom_receptor is not None:
                periodicidad_code = nom_receptor.get('PeriodicidadPago')

            if not rfc:
                return None, "RFC not found in XML"
            if not fecha_pago:
                return None, "FechaPago not found in XML"

            # Anchor month/day on the period covered (FechaFinalPago = devengado,
            # the unified accountant criterion). Fall back to FechaPago if absent.
            anchor = fecha_final or fecha_pago

            return {
                'rfc': rfc,
                'fecha_pago': fecha_pago,
                'fecha_final': fecha_final,
                'anchor': anchor,
                'periodicidad_code': periodicidad_code,
                'periodicidad': PERIODICIDAD.get(periodicidad_code),
            }, None

        except ET.ParseError as e:
            return None, f"XML parse error: {str(e)}"
        except Exception as e:
            return None, f"Error reading XML: {str(e)}"

    def determine_suffix(self, anchor_date, periodicidad):
        """
        Return (suffix, warning) for the given anchor date and period type.
        suffix may be '' (monthly). warning is None unless we had to fall back.
        """
        try:
            day = datetime.strptime(anchor_date, '%Y-%m-%d').day
        except Exception:
            return None, None

        if periodicidad == 'quincenal':
            return ('Q1' if 1 <= day <= 15 else 'Q2'), None
        if periodicidad == 'semanal':
            return f'S{math.ceil(day / 7)}', None
        if periodicidad == 'catorcenal':
            return f'C{math.ceil(day / 14)}', None
        if periodicidad == 'decenal':
            return f'D{math.ceil(day / 10)}', None
        if periodicidad == 'diario':
            return f'J{day:02d}', None
        if periodicidad == 'mensual':
            return '', None
        if periodicidad == 'bimestral':
            return 'B', None

        # Unknown / missing periodicity: fall back to quincena by day, warn.
        fallback = 'Q1' if 1 <= day <= 15 else 'Q2'
        return fallback, 'periodicity unknown, defaulted to quincena (Q#)'

    def generate_new_filename(self, data, extension):
        """Generate new filename: RFC-YYYY-MM[-suffix].extension"""
        try:
            date_obj = datetime.strptime(data['anchor'], '%Y-%m-%d')
            year = date_obj.strftime('%Y')
            month = date_obj.strftime('%m')
            suffix, warning = self.determine_suffix(data['anchor'], data['periodicidad'])

            if suffix is None:
                return None, None

            stem = f"{data['rfc']}-{year}-{month}"
            if suffix:
                stem += f"-{suffix}"
            return f"{stem}.{extension}", warning
        except Exception:
            return None, None

    def process_folder(self, folder_path):
        """Process all PDF/XML pairs in the folder"""
        self.log_entries = []
        self.stats = {
            'total_checked': 0,
            'renamed': 0,
            'skipped_correct': 0,
            'warnings': 0,
            'errors': 0
        }

        folder = Path(folder_path)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_entries.append(f"=== CFDI Renaming Log - {timestamp} ===")
        self.log_entries.append(f"Folder: {folder_path}")
        self.log_entries.append("")

        pdf_files = list(folder.glob('*.pdf'))

        for pdf_file in pdf_files:
            self.stats['total_checked'] += 1
            base_name = pdf_file.stem

            if self.is_already_renamed(pdf_file.name):
                self.log_entries.append(f"⏭ SKIPPED: {pdf_file.name} (Already correctly named)")
                self.stats['skipped_correct'] += 1
                continue

            xml_file = folder / f"{base_name}.xml"

            if not xml_file.exists():
                self.log_entries.append(f"⚠ WARNING: {pdf_file.name} - No matching XML found")
                self.stats['warnings'] += 1
                continue

            if self.is_already_renamed(xml_file.name):
                self.log_entries.append(f"⏭ SKIPPED: {xml_file.name} (Already correctly named)")
                self.stats['skipped_correct'] += 1
                continue

            data, error = self.extract_data(xml_file)

            if error:
                self.log_entries.append(f"❌ ERROR: {xml_file.name} - {error}")
                self.stats['errors'] += 1
                continue

            new_pdf_name, warning = self.generate_new_filename(data, 'pdf')
            new_xml_name, _ = self.generate_new_filename(data, 'xml')

            if not new_pdf_name or not new_xml_name:
                self.log_entries.append(f"❌ ERROR: {base_name} - Could not generate new filename")
                self.stats['errors'] += 1
                continue

            if warning:
                self.log_entries.append(f"⚠ WARNING: {xml_file.name} - {warning}")
                self.stats['warnings'] += 1

            new_pdf_path = folder / new_pdf_name
            new_xml_path = folder / new_xml_name

            if new_pdf_path.exists() and new_pdf_path != pdf_file:
                self.log_entries.append(f"⚠ WARNING: {pdf_file.name} - Target {new_pdf_name} already exists")
                self.stats['warnings'] += 1
                continue

            if new_xml_path.exists() and new_xml_path != xml_file:
                self.log_entries.append(f"⚠ WARNING: {xml_file.name} - Target {new_xml_name} already exists")
                self.stats['warnings'] += 1
                continue

            try:
                pdf_file.rename(new_pdf_path)
                xml_file.rename(new_xml_path)
                self.log_entries.append(f"✓ RENAMED: {pdf_file.name} → {new_pdf_name}")
                self.log_entries.append(f"✓ RENAMED: {xml_file.name} → {new_xml_name}")
                self.stats['renamed'] += 2
            except Exception as e:
                self.log_entries.append(f"❌ ERROR: Failed to rename {base_name} - {str(e)}")
                self.stats['errors'] += 1

        self.log_entries.append("")
        self.log_entries.append("=== SUMMARY ===")
        self.log_entries.append(f"Total files checked: {self.stats['total_checked']}")
        self.log_entries.append(f"Successfully renamed: {self.stats['renamed']} files")
        self.log_entries.append(f"Already correct: {self.stats['skipped_correct']}")
        self.log_entries.append(f"Warnings: {self.stats['warnings']}")
        self.log_entries.append(f"Errors: {self.stats['errors']}")

        log_path = folder / f"rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.log_entries))
            self.log_entries.append("")
            self.log_entries.append(f"📄 Log saved to: {log_path.name}")
        except Exception as e:
            self.log_entries.append(f"⚠ Could not save log file: {str(e)}")

        return '\n'.join(self.log_entries)


class RenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CFDI PDF/XML Renamer")
        self.root.geometry("800x600")
        self.renamer = CFDIRenamer()
        self.config = load_config()

        self.create_widgets()

        # Restore last-used folder if it still exists
        last = self.config.get('last_folder')
        if last and os.path.isdir(last):
            self.selected_folder = last
            self.folder_label.config(text=last, fg="black")
            self.process_button.config(state='normal')

    def create_widgets(self):
        title = Label(self.root, text="CFDI PDF/XML Renamer", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        subtitle = Label(self.root, text="Rename payroll files to: RFC-YYYY-MM[-period]", font=("Arial", 10))
        subtitle.pack()

        folder_frame = Frame(self.root)
        folder_frame.pack(pady=20, padx=20, fill='x')

        self.folder_label = Label(folder_frame, text="No folder selected", fg="gray")
        self.folder_label.pack(side='left', padx=10)

        select_button = Button(folder_frame, text="Select Folder", command=self.select_folder,
                               bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        select_button.pack(side='right')

        self.process_button = Button(self.root, text="Process Files", command=self.process_files,
                                     bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
                                     state='disabled', height=2)
        self.process_button.pack(pady=10)

        log_label = Label(self.root, text="Processing Log:", font=("Arial", 10, "bold"))
        log_label.pack(pady=(10, 5))

        log_frame = Frame(self.root)
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)

        scrollbar = Scrollbar(log_frame)
        scrollbar.pack(side='right', fill='y')

        self.log_text = Text(log_frame, wrap='word', yscrollcommand=scrollbar.set,
                             font=("Consolas", 9))
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)

        info = Label(self.root,
                     text="Auto-detected: Q1/Q2 quincena · S1-S5 semana · C1-C3 catorcena · D1-D3 decena · J## diario · monthly = no suffix",
                     font=("Arial", 8), fg="gray")
        info.pack(pady=5)

        self.selected_folder = None

    def select_folder(self):
        initial = self.selected_folder if self.selected_folder and os.path.isdir(self.selected_folder) else None
        folder = filedialog.askdirectory(title="Select folder with PDF and XML files",
                                         initialdir=initial)
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=folder, fg="black")
            self.process_button.config(state='normal')
            self.config['last_folder'] = folder
            save_config(self.config)

    def process_files(self):
        if not self.selected_folder:
            return

        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Processing files...\n\n")
        self.root.update()

        result = self.renamer.process_folder(self.selected_folder)

        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, result)


def main():
    root = Tk()
    app = RenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
