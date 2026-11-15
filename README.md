# 🧩 LUDARP Drawing Packager

![Version](https://img.shields.io/badge/version-v2.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![Status](https://img.shields.io/badge/status-active-success)

A high-performance desktop application built for civil engineers, structural designers, and BIM professionals to automate drawing package distribution (CAD + PDF + ZIP) with standardized naming and one-click packaging.

---

## 📸 Preview

<img width="1001" height="639" alt="image" src="https://github.com/user-attachments/assets/c82649ab-c021-466f-b257-667d478bbf08" />

---

## 🚀 Key Features in v2.0

* 📁 **Smart Batch & Pair Detection**: Automatically identifies and matches corresponding `.dwg` and `.pdf` drawing pairs in folders or dropped files.
* 📦 **Flexible Packaging Modes**:
  * **CAD + PDF**: Standard drawing bundle (`.dwg` + `.pdf`).
  * **ZIP + PDF**: Source model / background archive + sheet drawing.
  * **All in One**: Full package (`.dwg` + `.pdf` + source `.zip`).
* 🏷️ **Civil Engineering Revision Tags**:
  * Quick-select presets (`R00`, `R01`, `REV-A`, `P1`, `C1`).
  * Customizable revision numbers with toggle ON/OFF.
* 📅 **Custom Date Formatting**:
  * Integrated calendar picker (`tkcalendar`).
  * Optional date inclusion in package filenames.
* 🔤 **Flexible Naming Templates**:
  * Choose between multiple industry naming templates (`Client_Project_Rev_Date`, `Client_Rev_Date`, etc.).
  * Customizable separators (`_`, `-`, or spaces).
* 📄 **Live Filename Preview**:
  * Real-time preview of the target filename as you type.
  * One-click **Copy Generated Name** button for transmittals and email logs.
* 💾 **Recent Clients & Projects History**:
  * Remembers previous clients and projects in editable dropdowns for lightning-fast workflows.
  * One-click clipboard **Paste** buttons for fast input.
* 🖱️ **Drag & Drop Support**: Drop folders or multiple drawing files directly into the window.
* 📊 **File Status & Size Inspector**: Shows file sizes and status indicators for paired drawings.
* ⚡ **Progress Bar & Explorer Integration**: Visual progress indicator and auto-opens output folder upon completion.
* 🌙 **Modern Dark Theme**: Engineer-friendly dark slate interface designed for long drafting sessions.

---

## 🛠 Requirements

* **OS**: Windows 10 / 11
* **Python**: 3.10+ (if running from source)

### Install Required Libraries

```bash
pip install tkinterdnd2 tkcalendar pillow
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

* **Language**: Python 3
* **GUI Engine**: Tkinter
* **Drag & Drop**: TkinterDnD2
* **Date Picker**: tkcalendar
* **Packaging**: PyInstaller

---

## ▶️ Demo Video

Watch the video walkthrough:
[YouTube Demo Playlist](https://www.youtube.com/watch?v=XTDXAKkgGdE&list=PLBip7ccT-VcsgEbjz1ObwGUfuJRN8R7LB)

---

## 👨‍💻 Author

**Pradul P**  
Civil Engineer | BIM | Automation

---

## 📌 License

Free to use and modify for engineering teams and civil projects.
