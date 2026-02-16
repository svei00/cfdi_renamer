# 🚀 CFDI Renamer - Easy Setup Guide

## Choose Your Method:

### ⭐ METHOD 1: DOUBLE-CLICK (Easiest - Requires Python installed)

#### **Windows:**
1. Double-click **`run_renamer.bat`**
   - Done! The GUI opens automatically

#### **Mac/Linux:**
1. Right-click **`run_renamer.sh`** → "Open With" → "Terminal"
   - Or run in terminal: `./run_renamer.sh`
   - First time: `chmod +x run_renamer.sh` (to make it executable)

---

### 🔥 METHOD 2: CREATE .EXE (Windows Only - No Python Needed!)

This creates a **standalone .exe file** that works on ANY Windows computer without Python!

#### Steps:

**1. Install PyInstaller** (one-time setup):
```bash
pip install pyinstaller
```

**2. Build the executable:**
```bash
python build_exe.py
```
OR manually:
```bash
pyinstaller --onefile --windowed --name=CFDI_Renamer cfdi_renamer.py
```

**3. Find your executable:**
- Location: `dist/CFDI_Renamer.exe`
- Size: ~10-15 MB (includes Python + all dependencies)

**4. Use it:**
- ✅ Double-click to run (no Python needed!)
- ✅ Copy to any Windows PC
- ✅ Share with your team
- ✅ Put on USB drive

#### First Run:
- May take 5-10 seconds to extract files
- After that, opens instantly!

---

### 📦 METHOD 3: CREATE .APP (Mac Only)

Create a Mac application bundle:

**1. Install py2app:**
```bash
pip install py2app
```

**2. Create setup file:**
```bash
py2applet --make-setup cfdi_renamer.py
```

**3. Build the app:**
```bash
python setup.py py2app
```

**4. Find your app:**
- Location: `dist/cfdi_renamer.app`
- Double-click to run!

---

## 📋 Quick Comparison:

| Method | Windows | Mac | Linux | Requires Python? | File Size |
|--------|---------|-----|-------|------------------|-----------|
| `.bat` launcher | ✅ | ❌ | ❌ | Yes | 15 KB |
| `.sh` launcher | ❌ | ✅ | ✅ | Yes | 15 KB |
| `.exe` executable | ✅ | ❌ | ❌ | **NO** | ~10-15 MB |
| `.app` bundle | ❌ | ✅ | ❌ | **NO** | ~15-20 MB |

---

## 🎯 Recommended Setup by User:

### For YOU (has Python installed):
**Just use the launcher!**
- Windows: `run_renamer.bat`
- Mac/Linux: `run_renamer.sh`

### For OTHERS (may not have Python):
**Create the executable:**
- Windows: Build `.exe` using PyInstaller
- Mac: Build `.app` using py2app
- Share the single file - no installation needed!

---

## 🔧 Troubleshooting:

### "Python is not installed"
- Download from: https://www.python.org/downloads/
- **Important:** Check "Add Python to PATH" during installation

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### ".bat file shows terminal then closes"
- That's normal if Python isn't found
- Read the error message before it closes
- Or run from Command Prompt to see errors

### ".sh file won't run on Mac"
1. Right-click file → Get Info → Open With → Terminal
2. Or in terminal: `chmod +x run_renamer.sh && ./run_renamer.sh`

### "No module named 'tkinter'"
- Windows: Reinstall Python, check "tcl/tk" option
- Linux: `sudo apt install python3-tk`
- Mac: Should be included

### ".exe is too large"
- Normal! It includes entire Python runtime
- File size: 10-15 MB is expected
- First run extracts files (5-10 sec delay)

---

## 📁 Files Included:

```
cfdi_renamer.py          ← Main Python script
run_renamer.bat          ← Windows launcher (double-click)
run_renamer.sh           ← Mac/Linux launcher (double-click)
build_exe.py             ← Script to create .exe
README.md                ← Full documentation
SETUP.md                 ← This file!
```

---

## 🎁 Bonus: Auto-Start on Computer Startup (Optional)

### Windows:
1. Press `Win + R`
2. Type: `shell:startup`
3. Copy `run_renamer.bat` to this folder
4. Renamer starts automatically when Windows starts

### Mac:
1. System Preferences → Users & Groups → Login Items
2. Click `+` and add `run_renamer.sh`
3. Renamer starts automatically when Mac starts

---

## ✅ Final Checklist:

- [ ] Python installed (for launcher method)
- [ ] Downloaded all files to same folder
- [ ] Tested launcher (`.bat` or `.sh`)
- [ ] (Optional) Created `.exe` for sharing
- [ ] Read README.md for usage instructions

---

## 💡 Tips:

1. **Keep files together** - The launcher expects `cfdi_renamer.py` in same folder
2. **Test first** - Try with a small folder before processing thousands of files
3. **Backup first** - The script renames files directly (no undo!)
4. **Share the .exe** - Easiest way for others to use without Python
5. **Check the log** - Every run creates a detailed log file

---

## 🆘 Still Need Help?

Common issues solved:
- **Won't open:** Right-click → "Run as administrator"
- **Antivirus blocks .exe:** Add exception (PyInstaller .exe files often trigger false positives)
- **Missing files:** Make sure all files are in the same folder
- **Permission denied:** Close any programs using the files

---

Happy renaming! 🇲🇽📄✨