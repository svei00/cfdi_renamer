#!/bin/bash
# CFDI Renamer Launcher for Mac/Linux
# Double-click this file to run the renamer (may need to make executable first)

echo "Starting CFDI PDF/XML Renamer..."
echo

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo
    echo "Please install Python 3:"
    echo "  Mac: brew install python3"
    echo "  Linux: sudo apt install python3"
    echo
    read -p "Press Enter to close..."
    exit 1
fi

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Tkinter is not installed"
    echo
    echo "Please install tkinter:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Mac: Should be included with Python"
    echo
    read -p "Press Enter to close..."
    exit 1
fi

# Run the renamer script
cd "$SCRIPT_DIR"
python3 cfdi_renamer.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo
    echo "An error occurred. Press Enter to close..."
    read
fi