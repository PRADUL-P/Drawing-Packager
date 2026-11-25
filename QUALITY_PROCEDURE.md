# 📘 LUDARP Drawing Packager — Simple User Guide

Welcome to **LUDARP Drawing Packager**! This simple guide explains **every button, every field, and every feature** in plain language so anyone in your team can use it in seconds.

---

## 💡 What Does This App Do in 10 Seconds?

In civil and structural drafting, when you dispatch a drawing, you usually need to send:
1. **Client Files** (clean files named with the client's name and date, with no internal revision tags).
2. **Project Files** (internal archive files named with project code or drawing number).

Instead of manually renaming, copying, and zipping 6 separate files one by one, **this app does all 6 files in 1 single click!**

---

## 🎯 What Are the 6 Output Files Created?

Whenever you package a drawing, the app creates a folder named `output_files/` containing:

| # | File Name | What is it? |
|---|---|---|
| **1** | `[Client]_[Date].pdf` | The official PDF sheet for the client. |
| **2** | `[Client]_[Date].dwg` | The AutoCAD drawing file for the client. |
| **3** | `[Client]_[Date].zip` | A compressed zip folder with client-named files inside. |
| **4** | `[Project].pdf` | The PDF sheet for your internal server archive. |
| **5** | `[Project].dwg` | The CAD drawing for your internal server archive. |
| **6** | `[Project].zip` | The complete project model archive for internal records. |

---

## 🖥️ Screen Guide: Every Field & Button Explained

### 1. Top Header Bar

* **`🌙 Dark` / `☀️ Light` (Theme Switch):**  
  Click to instantly switch between dark mode (easy on the eyes) and bright light mode. The app remembers your choice next time you open it.
* **`📄 Generate info.txt`:**  
  Click this button to save a little configuration file (`info.txt`) with client and project names inside any folder.
* **`⚡ Auto-Pack on Drop` (Switch):**  
  - When **ON (Recommended)**: If you drop a folder that already contains an `info.txt`, the app automatically packages all 6 files **immediately with 0 clicks!**
  - When **OFF**: Dropping a folder loads the names and files, but waits for you to review and click the Generate button.

---

### 2. Left Panel: Dispatch Details

* **`CLIENT NAME` Field:**  
  Type the client or contractor name here (e.g. `Acme Corp` or `MR. SMITH`).  
  - This name is **strictly used for client files**.
  - Internal revision tags will **never** be attached to client files.
* **`Paste` Button (next to Client):**  
  Click to paste text copied from your clipboard into the Client field.
* **`PROJECT NAME` Field:**  
  Type the internal project number or drawing title (e.g. `VILLA_402` or `METRO_TERMINAL_B101`).  
  - *Tip: If you leave this blank, the app will automatically use the name of the drawing file!*
* **`Paste` Button (next to Project):**  
  Click to paste text copied from your clipboard into the Project field.
* **`Include Date on Client Package` (Toggle):**  
  - **ON**: Appends today's date (e.g. `_25-11-2026`) to the client files so you know exactly when it was sent.
  - **OFF**: Uses only the client name without any date.
* **Calendar Date Picker:**  
  Click to change the dispatch date if you are preparing drawings for a future or past date.
* **`💾 Save Current Names as info.txt`:**  
  Saves whatever you typed in Client and Project as an `info.txt` file in your selected folder.
* **`🎯 TARGET OUTPUT MANIFEST (6 FILES)` Preview Box:**  
  A live preview that updates in real-time as you type, showing the exact 6 filenames that will be generated before you even click package.

---

### 3. Right Panel: Drop Zone & File Slots

* **Large Drop Zone (`📂 ⬆️ DRAG & DROP`):**  
  Drag and drop any folder or drawing files directly here from your computer.  
  - Works with folders with spaces in their names (e.g. `E:\Drawing packer\00share`).
  - Automatically searches the folder for matching `.dwg`, `.pdf`, `.zip`, and `info.txt` files!
* **`📁 Choose Folder...` Button:**  
  If you prefer not to drag and drop, click this button to open a file browser and pick your project folder.
* **Visual File Slots (PDF, CAD, ZIP):**
  - 🔴 **`PDF SHEET` Card:** Shows your loaded `.pdf` filename and file size (e.g. `Foundation_Plan.pdf (2.4 MB)`). Turns green when loaded.
  - 🔵 **`CAD DRAWING` Card:** Shows your loaded `.dwg` AutoCAD drawing filename and file size.
  - 🟡 **`ZIP ARCHIVE` Card:** Shows any reference zip file (like survey data or background models). This slot is optional.
  - **`Browse` Button (on each card):** Click to pick a specific file manually if you want to replace one.
* **`Packaging Mode` Dropdown:**
  - **`CAD + PDF`**: Packages CAD drawing and PDF sheet together.
  - **`ZIP + PDF`**: Packages reference ZIP and PDF sheet together.
  - **`All in One (CAD+PDF+ZIP)`**: Packages all 3 files together into the zip. (Auto-selected if a ZIP file is found).
* **`⚡ GENERATE ALL 6 PACKAGE FILES` (Big Green Button):**  
  Click this button (or press the **`<Enter>`** key on your keyboard) to create all 6 files instantly!
* **`📂 Open Output Folder` Button:**  
  Opens Windows File Explorer directly inside `output_files/` so you can view, attach, or send your 6 finished files.
* **`🔄 Reset All` Button:**  
  Clears the inputs and resets the file slots back to clean state.
* **Status Label:**  
  Shows helpful live status messages like `Ready`, `Loaded: PDF, DWG`, `Packaging 6 files...`, or `Done! ✅`.

---

## 🚀 How to Use It (Choose Your Way)

### Method 1: The "0-Click" Way (Fastest for Daily Work)

1. Put a simple text file named `info.txt` in your drawing folder with two lines:
   ```text
   Client: ACME_INFRASTRUCTURE
   Project: METRO_TERMINAL_B101
   ```
2. Open **LUDARP Drawing Packager**.
3. **Drag and drop the folder into the app window.**
4. **Done!** The app automatically reads the names, packs all 6 files into `output_files/`, and pops open the folder in Windows Explorer. You didn't even have to click a single button!

---

### Method 2: The "3-Step Manual" Way

1. Open the app and type the **Client Name** and **Project Name** (or click **Paste**).
2. **Drag and drop** your drawing folder or files into the drop zone.
3. Click the big green button: **`⚡ GENERATE ALL 6 PACKAGE FILES`** (or hit `<Enter>`).
4. Windows Explorer will open up automatically showing your 6 ready-to-send files!

---

## 🔍 Simple Quality Check Before Sending

Before sending files to your client or uploading to a portal, do a quick 10-second check:

1. **Count the files:** Are there 6 files in the `output_files/` folder? (3 client files + 3 project files).
2. **Check client names:** Do the client files have the correct client name and date?
3. **Check project names:** Do the project files have your internal drawing number?
4. **Test the files:** Open the PDF to make sure sheets look good, and open the ZIP to confirm the inner files are present.

---

## ❓ Common Questions & Quick Fixes

* **Q: It says "PDF Required"?**  
  *A:* Every package must have at least a PDF drawing sheet. Export your PDF from CAD or Revit and drop it in.
* **Q: It says "Client Name Required"?**  
  *A:* Make sure you typed a Client Name in the left box, or provided an `info.txt` file.
* **Q: Can I run this without installing Python?**  
  *A:* **Yes!** Just download and double-click **`LUDARP.Drawing.Packager.exe`**. It works on any Windows 10 or 11 PC without needing Python installed.
* **Q: Where are the output files saved?**  
  *A:* In a folder named `output_files/` inside the same folder where your drawings are located. The app also opens this folder automatically as soon as it finishes.
