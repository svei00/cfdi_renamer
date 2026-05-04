# CFDI PDF/XML Renamer

Rename Mexican payroll PDF and XML files based on RFC and payment date.

## What It Does

- Finds PDF/XML file pairs in a folder
- Extracts RFC from `cfdi:Receptor` in XML
- Extracts payment date from `nomina12:Nomina FechaPago` in XML
- Reads the period type from `nomina12:Receptor/@PeriodicidadPago` (SAT catalog) and **auto-detects** the suffix — no mode to pick
- Renames both files to: **RFC-YYYY-MM[-period]** format, month-anchored:

  | Periodicity | Suffix | Rule (day of FechaPago) |
  |---|---|---|
  | Quincenal | `Q1` / `Q2` | 1–15 → Q1, 16–31 → Q2 |
  | Semanal | `S1`–`S5` | `ceil(day/7)` |
  | Catorcenal | `C1`–`C3` | `ceil(day/14)` |
  | Decenal | `D1`–`D3` | `ceil(day/10)` |
  | Diario | `J01`–`J31` | day of month (J = Jornal) |
  | Mensual | *(none)* | `RFC-YYYY-MM` |
  | Bimestral | `B` | `RFC-YYYY-MM-B` |
  | Otra / missing | falls back to `Q1`/`Q2` and logs a warning | |

- Remembers the last folder used (stored in `%APPDATA%\CFDI_Renamer\config.json`)
- Skips files already in correct format (any of the suffixes above)
- Creates detailed log file

## Example

**Before:**
```
RE_2105_Quincenal_2026_3_031_18E.pdf
RE_2105_Quincenal_2026_3_031_18E.xml
```

**After:**
```
ABCD010203347-2026-02-Q1.pdf
ABCD010203347-2026-02-Q1.xml
```

## Requirements

- Python 3.7 or higher (Tkinter included)
- No additional packages needed!

## Installation

### Windows
1. Download Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Download `cfdi_renamer.py`

### Mac/Linux
Python is usually pre-installed. If not:
- Mac: `brew install python3`
- Linux: `sudo apt install python3`

## How to Use

### Option 1: Double-click (Windows)
1. Right-click `cfdi_renamer.py`
2. Select "Open with" → "Python"
3. GUI window opens automatically

### Option 2: Command line
```bash
python cfdi_renamer.py
```

### Option 3: Make it executable (Mac/Linux)
```bash
chmod +x cfdi_renamer.py
./cfdi_renamer.py
```

## Using the GUI

1. **Click "Select Folder"** - Choose the folder with your PDF/XML files
2. **Click "Process Files"** - The script will:
   - Find all PDF/XML pairs
   - Skip already-renamed files
   - Rename files to RFC-YYYY-MM-Q# format
   - Show results in the log window
3. **Check the log** - A text file will be saved in the same folder

## Log File

The script creates a timestamped log file: `rename_log_YYYYMMDD_HHMMSS.txt`

Example log:
```
=== CFDI Renaming Log - 2026-02-16 14:30:25 ===

✓ RENAMED: RE_2105_Quincenal_2026_3_031_18E.pdf → ABCD010203347-2026-02-Q1.pdf
✓ RENAMED: RE_2105_Quincenal_2026_3_031_18E.xml → ABCD010203347-2026-02-Q1.xml

⏭ SKIPPED: XYZW123456789-2026-02-Q2.pdf (Already correctly named)

⚠ WARNING: RE_2105_Quincenal_2026_3_048_8D2.pdf - No matching XML found

=== SUMMARY ===
Total files checked: 150
Successfully renamed: 148 files
Already correct: 50
Warnings: 2
Errors: 0
```

## Important Notes

✅ **Safe to run multiple times** - Already renamed files are skipped
✅ **Both files renamed together** - PDF and XML stay paired
✅ **Original files are renamed** - No copies created
✅ **Same RFC, different periods OK** - Q1 and Q2 files can coexist

## Troubleshooting

**"No module named 'tkinter'"**
- Windows: Reinstall Python, check "tcl/tk" option
- Ubuntu/Debian: `sudo apt install python3-tk`
- Mac: Tkinter should be included

**"Permission denied"**
- Make sure files aren't open in another program
- Check folder permissions

**"RFC not found in XML"**
- Verify XML is valid CFDI format
- Check that `cfdi:Receptor` tag exists

**"FechaPago not found in XML"**
- Verify XML contains `nomina12:Nomina` complement
- Check that `FechaPago` attribute exists

## XML Structure Expected

```xml
<cfdi:Comprobante ...>
    <cfdi:Receptor Rfc="ABCD010203347" Nombre="..." />
    ...
    <cfdi:Complemento>
        <nomina12:Nomina Version="1.2" 
                        FechaPago="2026-02-15" 
                        FechaInicialPago="2026-02-01" 
                        FechaFinalPago="2026-02-15" 
                        ... />
    </cfdi:Complemento>
</cfdi:Comprobante>
```

## Support

If you encounter issues:
1. Check the log file for specific errors
2. Verify your XML files are valid CFDI format
3. Make sure PDF and XML pairs have identical base names

## License

Free to use and modify as needed!