# 🧩 LUDARP Drawing Packager

![Version](https://img.shields.io/badge/version-v2.0-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-lightgrey?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

A high-performance desktop engineering application built for civil engineers, structural designers, and BIM professionals to automate drawing package distribution (CAD + PDF + ZIP) with standardized naming and one-click packaging.

---

## 🎥 Video Demonstration

[![Watch the Demo Video](https://img.youtube.com/vi/OdTz4SFu0KI/maxresdefault.jpg)](https://youtu.be/OdTz4SFu0KI)

▶️ **Click the image above or open this link to watch the complete workflow demo:**  
👉 **[https://youtu.be/OdTz4SFu0KI](https://youtu.be/OdTz4SFu0KI)**

---

## 🚀 Standalone Windows Executable (.exe) — No Python Needed!

> [!TIP]
> **Zero Setup / Zero Python Required:**  
> Run immediately on any 64-bit Windows 10 or Windows 11 machine without installing Python, Git, or any third-party dependencies! Everything (Python runtime, libraries, themes, and fonts) is 100% bundled inside the `.exe`.

### ⬇️ Download & Quick Start:

[![Download Windows EXE](https://img.shields.io/badge/⚡_DIRECT_DOWNLOAD-LUDARP.Drawing.Packager.exe-2563eb?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/PRADUL-P/Drawing-Packager/releases/download/v2.0/LUDARP.Drawing.Packager.exe)

👉 **[Direct Download (.exe)](https://github.com/PRADUL-P/Drawing-Packager/releases/download/v2.0/LUDARP.Drawing.Packager.exe)** | **[View GitHub Release (v2.0)](https://github.com/PRADUL-P/Drawing-Packager/releases/tag/v2.0)**

1. **Download:** Click the direct download button above to get **`LUDARP.Drawing.Packager.exe`**.
2. **Launch:** Double-click the `.exe` file to open the app directly.
3. **Package:** Drag and drop your drawing folder or files — generate all 6 contract-compliant packages in 1 click!

---

## 🚀 Exhaustive Features Breakdown

### 1. ⚡ Single-Click 6-File Generation Engine
With a single click on **`⚡ GENERATE ALL 6 PACKAGE FILES`** (or pressing `<Enter>`), the application packages, copies, and compresses a complete, contract-compliant 6-file distribution package in seconds:
* **Client Set (3 Files — For External Issuance):**
  * `[Client]_[DD-MM-YYYY].pdf` — Vector drawing sheet for client review.
  * `[Client]_[DD-MM-YYYY].dwg` — AutoCAD drawing formatted for client submission.
  * `[Client]_[DD-MM-YYYY].zip` — Compressed archive containing internally standardized drawing files.
* **Project Set (3 Files — For Internal Project Records):**
  * `[Project].pdf` — Permanent sheet record for company server archives.
  * `[Project].dwg` — Permanent CAD model record.
  * `[Project].zip` — Complete source package containing surveys and models.

### 2. ⚡ Zero-Click Auto-Pack (`info.txt`)
Drop any project folder (e.g. `00share/` or drawing folder) containing an `info.txt` file directly onto the window. If **`Auto-Pack on Drop`** is enabled (default: ON), the application automatically:
1. Reads Client and Project names from `info.txt`.
2. Scans and pairs matching `.dwg`, `.pdf`, and `.zip` files.
3. Packages all 6 output files into an `output_files/` directory.
4. Automatically opens Windows Explorer to the output folder — **zero manual clicks required!**

### 3. 🎯 Strict Client vs. Project Naming Separation
Completely eliminates naming errors and revision leaks:
* **Client Files:** Named strictly with the client's commercial identity and dispatch date. **No internal revision numbers** appear on client files unless explicitly specified.
* **Project Files:** Named strictly with internal project numbering and drawing codes (e.g. `METRO_TERMINAL_B101`).

### 4. 📦 3 Intelligent Packaging Modes
Choose how CAD, PDF, and ZIP files are combined inside the output archives:
* **`CAD + PDF`**: Packages CAD drawing and PDF sheet together.
* **`ZIP + PDF`**: Packages reference survey/model archive and PDF sheet together.
* **`All in One (CAD+PDF+ZIP)`**: Full submission bundle combining DWG, PDF, and source ZIP archive.

### 5. 🔍 Dedicated Visual File Status Cards
Real-time inspection cards for each supported drawing type:
* 🔴 **PDF Sheet (`.pdf`)**: Displays file name, file size badge (e.g. `2.4 MB`), and green confirmation border.
* 🔵 **CAD Drawing (`.dwg`)**: Displays AutoCAD drawing status, file size, and manual browse button.
* 🟡 **ZIP Archive (`.zip`)**: Displays reference ZIP status, size, and auto-switches mode to *All in One*.

### 6. 💎 Modern Glassmorphism UI & Anti-Aliasing
* Crafted with **CustomTkinter** featuring native rounded corners (`corner_radius=14`) and frosted translucent cards.
* High-contrast typography: Jet black (`#0f172a`) in Light Mode and pure crisp white (`#f8fafc`) in Dark Mode.
* High-DPI Windows awareness (`SetProcessDpiAwareness(1)`) for ultra-sharp rendering on 2K/4K displays.

### 7. 🌗 Instant Dynamic Dark & Light Theme Switcher
* Header segmented toggle: **`🌙 Dark`** / **`☀️ Light`**.
* Dynamically and instantly updates all cards, inputs, buttons, badges, borders, and embedded date pickers.
* Automatically saves user theme preference in `~/.ludarp_packager_config.json`.

### 8. 📅 Integrated Calendar Date Picker with One-Click Toggle
* Embedded **`tkcalendar`** dropdown for choosing dispatch dates.
* Quick toggle switch: **"Include Date on Client Package"** to effortlessly turn date stamps on/off.

### 9. 💾 Built-in `info.txt` Metadata Generator
* Enter Client and Project names in the app and click **`💾 Save Current Names as info.txt`**.
* Saves an `info.txt` file into any folder (e.g. `00share`) for future automated zero-click packaging.

### 10. 📋 Quick Clipboard Paste & History Memory
* Instant **Paste** buttons for Client Name and Project Name fields.
* Remembers the last 15 clients and projects in editable dropdowns for rapid re-issuance.

### 11. 📂 Robust Drag & Drop Engine
* Supports drag-and-drop of entire folders or individual files.
* Specially engineered to handle Windows file paths containing spaces (e.g. `E:\Drawing packer\00share`).

---

## 📋 Quality Assurance & Standard Operating Procedure (SOP)

This repository includes a formal engineering **Standard Operating Procedure (SOP)** compliant with civil, structural, and architectural document control protocols:

👉 **Read the full Quality Manual:** [**`QUALITY_PROCEDURE.md`**](QUALITY_PROCEDURE.md)

### Key Quality Checkpoints:
1. Pre-packaging file audits (purged DWGs, vector-exported PDFs).
2. Verification of all 6 generated files.
3. Client vs Project naming isolation check.
4. Internal `.zip` archive integrity testing.

---

## 🛠 Option 2: Running from Source (Python)

If you prefer to run the application using Python:

### 1. Requirements
* Windows 10 / 11
* Python 3.10+

### 2. Install Dependencies
```bash
pip install customtkinter darkdetect tkinterdnd2 tkcalendar pillow
```

### 3. Launch App
```bash
python app.py
```

*(Optional: Run console-less by running `pythonw app.py`).*

---

## 📦 Compiling Standalone Executable (.exe)

To build the single-file `.exe` executable yourself:

```bash
pip install pyinstaller
pyinstaller "LUDARP Drawing Packager.spec" --clean
```

The compiled standalone executable will be generated in `dist/LUDARP Drawing Packager.exe`.

---

## 📁 Clean Repository Structure

```text
Drawing-Packager/
│
├── LUDARP Drawing Packager.exe   # Standalone executable (1-click launch, no Python needed)
├── app.py                        # Main Python application source code (v2.0)
├── zip-folder.ico                # Application & window icon
├── LUDARP Drawing Packager.spec  # PyInstaller build specification
├── QUALITY_PROCEDURE.md          # Quality Procedure & Dispatch SOP Manual
├── README.md                     # Comprehensive documentation & guide
└── .gitignore                    # Clean repository configuration
```

---

## 🔧 Tech Stack

* **Language**: Python 3.10+
* **GUI Engine**: CustomTkinter 6.0 (Glassmorphism & Dynamic Themes) & Tkinter
* **Drag & Drop Engine**: TkinterDnD2
* **Date Picker**: tkcalendar
* **Compiler / Bundler**: PyInstaller 6.x

---

## 📜 Version History (Changelog)

### **v2.0 (Latest Release)**
- 💎 **Modern Glassmorphism UI**: Re-engineered UI using CustomTkinter with frosted glass cards, rounded corners, subtle glows, and clean layouts.
- 🌗 **Instant Dark & Light Theme Switcher**: 1-click segmented toggle (`🌙 Dark` / `☀️ Light`) with persistent state across app launches.
- 🎯 **Strict 6-File Manifest**: Generates 3 Client files (`{client}_{date}.pdf`, `.dwg`, `.zip`) + 3 Project files (`{project}.pdf`, `.dwg`, `.zip`) with zero naming collision.
- ⚡ **Zero-Click Auto-Pack (`info.txt`)**: Drag & drop any folder with `info.txt` to instantly auto-pack all 6 files without needing any clicks.
- 🏷️ **Visual File Status Cards**: Dedicated status slots for PDF (Crimson), DWG (Cyan), and ZIP (Amber) showing file names, sizes, and validation states.
- 📄 **On-The-Fly `info.txt` Generator**: Added a 1-click tool to generate or update `info.txt` directly inside destination folders.
- 🧹 **Clean Standalone Distribution**: Single-file `.exe` executable with embedded CustomTkinter themes, fonts, and assets.

### **v1.0 (Initial Release)**
- 📦 Basic drawing pair packaging (`.dwg` and `.pdf`).
- 📁 Standard folder drag & drop.
- 📅 Calendar date selector.
- 🏷️ Revision tag formatting.

---

## 👨‍💻 Author

**Pradul P**  
Civil Engineer | BIM | Automation  
GitHub: [@PRADUL-P](https://github.com/PRADUL-P)

---

## 📌 License

Distributed under the MIT License. Free to use and modify for engineering teams, drafting departments, and civil projects.
