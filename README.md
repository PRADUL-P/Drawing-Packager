# 🧩 LUDARP Drawing Packager

![Version](https://img.shields.io/badge/version-v2.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![Status](https://img.shields.io/badge/status-active-success)

A high-performance desktop application built for civil engineers, structural designers, and BIM professionals to automate drawing package distribution (CAD + PDF + ZIP) with standardized naming and one-click packaging.

---

## 📸 Preview & Video Demo

[![Watch the Demo Video](https://img.youtube.com/vi/OdTz4SFu0KI/maxresdefault.jpg)](https://youtu.be/OdTz4SFu0KI)

▶️ **Click above or watch the full video demonstration:** [https://youtu.be/OdTz4SFu0KI](https://youtu.be/OdTz4SFu0KI)

<img width="1220" height="825" alt="image" src="https://github.com/user-attachments/assets/43bb4d13-8882-43e9-afb7-670daeb20e52" />

---

## 🚀 Key Features in v2.0

* 💎 **Modern Glassmorphism UI / UX**: Clean, frosted glass cards, rounded corners, subtle glows, and crystal-clear high-contrast typography.
* 🌗 **Seamless Dark & Light Mode Toggle**: Switch between Obsidian Slate Dark and Crisp Frosted Light mode in one click with instantaneous theme transitions.
* ⚡ **Zero-Click Auto-Pack (`info.txt`)**: Drop any folder containing an `info.txt` file (e.g. `00share/`), and it automatically extracts naming metadata and generates all 6 package files with 0 clicks!
* 📋 **Strict 6-File Manifest Generation**: Generates 3 Client files (`{client}_{date}.pdf`, `.dwg`, `.zip`) + 3 Project files (`{project}.pdf`, `.dwg`, `.zip`).
* 📁 **Smart Batch & Pair Detection**: Automatically identifies `.dwg`, `.pdf`, and `.zip` files from dropped folders or selection.
* 📦 **Flexible Packaging Modes**: `CAD + PDF`, `ZIP + PDF`, or `All in One (CAD+PDF+ZIP)`.
* 📅 **Custom Date Formatting**: Embedded calendar picker with instant toggle.
* 📄 **Generate info.txt on the fly**: Create or update `info.txt` in any project folder with a single click.

---

## 🛠 Requirements

* **OS**: Windows 10 / 11
* **Python**: 3.10+ (if running from source)

### Install Required Libraries

```bash
pip install customtkinter darkdetect tkinterdnd2 tkcalendar pillow
```

---

## ▶️ Running the Application

### Option 1: Run with Python

```bash
python app.py
```

### Option 2: Run as Desktop App (.pyw)

Rename `app.py` to `app.pyw` for console-less execution:
```bash
pythonw app.py
```

---

## 🧪 How to Use

1. **Enter Client Name**: Type or pick from recent history (required).
2. **Enter Project Name**: Optional — automatically falls back to drawing filename if left blank.
3. **Set Revision & Date**: Select revision tag and toggle date if desired.
4. **Choose Input**: Select an input folder or drag & drop DWG, PDF, and ZIP files into the drop zone.
5. **Review Detected Drawings**: Inspect paired drawings and file sizes in the preview list.
6. **Select Mode & Output**: Choose packaging mode (`CAD + PDF`, `ZIP + PDF`, etc.) and optional destination directory.
7. **Click Generate Packages**: Files are organized, copied, and zipped into clean client and project bundles.

---

## 📦 Building Standalone Executable (.exe)

Compile into a single standalone `.exe` using PyInstaller:

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build using Spec File

```bash
pyinstaller "LUDARP Drawing Packager.spec" --clean
```

Or build manually via command line:

```bash
pyinstaller --onefile --windowed --name "LUDARP Drawing Packager" --icon=zip-folder.ico --hidden-import=tkinterdnd2 --hidden-import=tkcalendar --hidden-import=babel.numbers --add-data "zip-folder.ico;." app.py
```

The resulting standalone executable will be in:
```
dist/LUDARP Drawing Packager.exe
```

---

## 📁 Project Structure

```
Drawing-Packager/
│
├── app.py                      # Main application source code (v2.0)
├── zip-folder.ico              # Application & window icon
├── LUDARP Drawing Packager.spec# PyInstaller build specification
├── .gitignore                  # Git ignore rules (clean repository)
└── README.md                   # Documentation & usage guide
```

---

## 🔧 Tech Stack

* **Language**: Python 3.10+
* **GUI Engine**: CustomTkinter 6.0 (Glassmorphism & Dynamic Themes) & Tkinter
* **Drag & Drop Engine**: TkinterDnD2
* **Date Picker**: tkcalendar
* **Packaging**: PyInstaller

---

## 📜 Version History (Changelog)

### **v2.0 (Latest Release)**
- 💎 **Modern Glassmorphism UI**: Re-engineered UI using CustomTkinter with frosted glass cards, rounded corners, subtle glows, and clean layouts.
- 🌗 **Instant Dark & Light Theme Switcher**: 1-click segmented toggle (`🌙 Dark` / `☀️ Light`) with persistent state across app launches.
- 🎯 **Strict 6-File Manifest**: Generates 3 Client files (`{client}_{date}.pdf`, `.dwg`, `.zip`) + 3 Project files (`{project}.pdf`, `.dwg`, `.zip`) with zero naming collision.
- ⚡ **Zero-Click Auto-Pack (`info.txt`)**: Drag & drop any folder with `info.txt` to instantly auto-pack all 6 files without needing any clicks.
- 🏷️ **Visual File Status Cards**: Dedicated status slots for PDF (Crimson), DWG (Cyan), and ZIP (Amber) showing file names, sizes, and validation states.
- 📄 **On-The-Fly `info.txt` Generator**: Added a 1-click tool to generate or update `info.txt` directly inside destination folders (e.g., `00share`).
- 🧹 **Clean Standalone Distribution**: Single-file `.exe` executable with embedded CustomTkinter themes, fonts, and assets.

### **v1.0 (Initial Release)**
- 📦 Basic drawing pair packaging (`.dwg` and `.pdf`).
- 📁 Standard folder drag & drop.
- 📅 Calendar date selector.
- 🏷️ Revision tag formatting.

---

## 🎥 Video Walkthrough

Watch the full workflow demo on YouTube:

[![Watch Demo Video](https://img.youtube.com/vi/OdTz4SFu0KI/maxresdefault.jpg)](https://youtu.be/OdTz4SFu0KI)

▶️ **Watch the video:** [https://youtu.be/OdTz4SFu0KI](https://youtu.be/OdTz4SFu0KI)

---

## 👨‍💻 Author

**Pradul P**  
Civil Engineer | BIM | Automation

---

## 📌 License

Free to use and modify for engineering teams and civil projects.
