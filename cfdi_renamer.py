#!/usr/bin/env python3
"""
CFDI PDF/XML Renamer
Renames Mexican payroll PDF and XML files based on RFC and payment date.
Format: RFC-YYYY-MM-Q#.extension (Q1 = days 1-15, Q2 = days 16-31)
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from tkinter import Tk, Button, Label, filedialog, Text, Scrollbar, Frame
from tkinter import ttk
import tkinter as tk

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
        """Check if file already follows RFC-YYYY-MM-Q# pattern"""
        # Pattern: RFC (13 chars) - YYYY - MM - Q1 or Q2
        pattern = r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}-\d{4}-\d{2}-Q[12]\.(pdf|xml)$'
        return bool(re.match(pattern, filename, re.IGNORECASE))
    
    def extract_rfc_and_date(self, xml_path):
        """Extract RFC and FechaPago from XML file"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Define namespaces for CFDI
            namespaces = {
                'cfdi': 'http://www.sat.gob.mx/cfd/4',
                'nomina12': 'http://www.sat.gob.mx/nomina12'
            }
            
            # Extract RFC from Receptor
            rfc = None
            receptor = root.find('.//cfdi:Receptor', namespaces)
            if receptor is not None:
                rfc = receptor.get('Rfc')
            
            # Extract FechaPago from Nomina complement
            fecha_pago = None
            nomina = root.find('.//nomina12:Nomina', namespaces)
            if nomina is not None:
                fecha_pago = nomina.get('FechaPago')
            
            if not rfc:
                return None, None, "RFC not found in XML"
            if not fecha_pago:
                return None, None, "FechaPago not found in XML"
            
            return rfc, fecha_pago, None
            
        except ET.ParseError as e:
            return None, None, f"XML parse error: {str(e)}"
        except Exception as e:
            return None, None, f"Error reading XML: {str(e)}"
    
    def determine_period(self, fecha_pago):
        """Determine Q1 (1-15) or Q2 (16-31) based on day"""
        try:
            # Parse date (format: YYYY-MM-DD)
            date_obj = datetime.strptime(fecha_pago, '%Y-%m-%d')
            day = date_obj.day
            
            if 1 <= day <= 15:
                return 'Q1'
            else:
                return 'Q2'
        except Exception as e:
            return None
    
    def generate_new_filename(self, rfc, fecha_pago, extension):
        """Generate new filename: RFC-YYYY-MM-Q#.extension"""
        try:
            date_obj = datetime.strptime(fecha_pago, '%Y-%m-%d')
            year = date_obj.strftime('%Y')
            month = date_obj.strftime('%m')
            period = self.determine_period(fecha_pago)
            
            if not period:
                return None
            
            return f"{rfc}-{year}-{month}-{period}.{extension}"
        except Exception:
            return None
    
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
        
        # Add header to log
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_entries.append(f"=== CFDI Renaming Log - {timestamp} ===")
        self.log_entries.append(f"Folder: {folder_path}")
        self.log_entries.append("")
        
        # Find all PDF files
        pdf_files = list(folder.glob('*.pdf'))
        
        for pdf_file in pdf_files:
            self.stats['total_checked'] += 1
            base_name = pdf_file.stem
            
            # Check if already renamed
            if self.is_already_renamed(pdf_file.name):
                self.log_entries.append(f"⏭ SKIPPED: {pdf_file.name} (Already correctly named)")
                self.stats['skipped_correct'] += 1
                continue
            
            # Look for matching XML
            xml_file = folder / f"{base_name}.xml"
            
            if not xml_file.exists():
                self.log_entries.append(f"⚠ WARNING: {pdf_file.name} - No matching XML found")
                self.stats['warnings'] += 1
                continue
            
            # Check if XML is already renamed
            if self.is_already_renamed(xml_file.name):
                self.log_entries.append(f"⏭ SKIPPED: {xml_file.name} (Already correctly named)")
                self.stats['skipped_correct'] += 1
                continue
            
            # Extract RFC and date from XML
            rfc, fecha_pago, error = self.extract_rfc_and_date(xml_file)
            
            if error:
                self.log_entries.append(f"❌ ERROR: {xml_file.name} - {error}")
                self.stats['errors'] += 1
                continue
            
            # Generate new filenames
            new_pdf_name = self.generate_new_filename(rfc, fecha_pago, 'pdf')
            new_xml_name = self.generate_new_filename(rfc, fecha_pago, 'xml')
            
            if not new_pdf_name or not new_xml_name:
                self.log_entries.append(f"❌ ERROR: {base_name} - Could not generate new filename")
                self.stats['errors'] += 1
                continue
            
            # Check if target files already exist
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
            
            # Rename files
            try:
                pdf_file.rename(new_pdf_path)
                xml_file.rename(new_xml_path)
                self.log_entries.append(f"✓ RENAMED: {pdf_file.name} → {new_pdf_name}")
                self.log_entries.append(f"✓ RENAMED: {xml_file.name} → {new_xml_name}")
                self.stats['renamed'] += 2
            except Exception as e:
                self.log_entries.append(f"❌ ERROR: Failed to rename {base_name} - {str(e)}")
                self.stats['errors'] += 1
        
        # Add summary
        self.log_entries.append("")
        self.log_entries.append("=== SUMMARY ===")
        self.log_entries.append(f"Total files checked: {self.stats['total_checked']}")
        self.log_entries.append(f"Successfully renamed: {self.stats['renamed']} files")
        self.log_entries.append(f"Already correct: {self.stats['skipped_correct']}")
        self.log_entries.append(f"Warnings: {self.stats['warnings']}")
        self.log_entries.append(f"Errors: {self.stats['errors']}")
        
        # Save log file
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
        
        # Create GUI elements
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title = Label(self.root, text="CFDI PDF/XML Renamer", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        subtitle = Label(self.root, text="Rename payroll files to: RFC-YYYY-MM-Q#", font=("Arial", 10))
        subtitle.pack()
        
        # Folder selection frame
        folder_frame = Frame(self.root)
        folder_frame.pack(pady=20, padx=20, fill='x')
        
        self.folder_label = Label(folder_frame, text="No folder selected", fg="gray")
        self.folder_label.pack(side='left', padx=10)
        
        select_button = Button(folder_frame, text="Select Folder", command=self.select_folder, 
                              bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        select_button.pack(side='right')
        
        # Process button
        self.process_button = Button(self.root, text="Process Files", command=self.process_files,
                                     bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
                                     state='disabled', height=2)
        self.process_button.pack(pady=10)
        
        # Log display
        log_label = Label(self.root, text="Processing Log:", font=("Arial", 10, "bold"))
        log_label.pack(pady=(10, 5))
        
        # Text widget with scrollbar
        log_frame = Frame(self.root)
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        scrollbar = Scrollbar(log_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.log_text = Text(log_frame, wrap='word', yscrollcommand=scrollbar.set,
                            font=("Consolas", 9))
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Info label
        info = Label(self.root, text="Q1 = Days 1-15 | Q2 = Days 16-31", 
                    font=("Arial", 8), fg="gray")
        info.pack(pady=5)
        
        self.selected_folder = None
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select folder with PDF and XML files")
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=folder, fg="black")
            self.process_button.config(state='normal')
    
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