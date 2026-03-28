# 🧩 LUDARP Drawing Packager

![Version](https://img.shields.io/badge/version-v1.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![Status](https://img.shields.io/badge/status-active-success)

A lightweight desktop tool built for civil engineers to automate packaging of drawing files (CAD + PDF + ZIP) with structured naming and fast workflows.

---

## 📸 Preview

<img width="1001" height="639" alt="image" src="https://github.com/user-attachments/assets/c82649ab-c021-466f-b257-667d478bbf08" />



---

## 🚀 Features

* 📁 Auto-detect ZIP, PDF, and DWG files
* 🔄 Smart packaging modes:

  * ZIP + PDF
  * CAD + PDF
* 🧠 Dynamic dropdown based on detected files
* 📌 Client & Project naming system
* 📅 Optional date inclusion (toggle ON/OFF)
* 📋 One-click Paste buttons (fast input)
* 🖱 Drag & Drop file support
* 🗂 Auto output folder creation
* ⚡ Fast and efficient packaging
* 🌙 Clean dark UI (engineer-friendly)

---

## 🛠 Requirements (Without EXE)

### Install Python (3.10+)

https://www.python.org/

---

## 📦 Required Libraries

Install all dependencies:

pip install tkinterdnd2 tkcalendar pillow

---

## ▶️ Run the Application

### Option 1: Run with Python

python app.py

---

### Option 2: Run as Desktop App (.pyw)

Rename:

app.py → app.pyw

✔ Double-click to run
✔ No console window

---

## 🧪 How to Use

1. Enter **Client Name**
2. Enter **Project Name** (optional)
3. Select folder or drag & drop files
4. Choose output folder (optional)
5. Select mode (auto-detected)
6. Toggle date inclusion if needed
7. Click **Generate**

---

## 📦 Create EXE (Standalone App)

### Step 1: Install PyInstaller

pip install pyinstaller

---

### Step 2: Navigate to project

cd path/to/project

---

### Step 3: Build EXE

pyinstaller --onefile --windowed --name "LUDARP Drawing Packager" --icon=zip-folder.ico --hidden-import=tkinterdnd2 --add-data "zip-folder.ico;." app.py

---

### Step 4: Output

dist/
└── LUDARP Drawing Packager.exe

---

## ⚠️ Common Issues

### Icon not showing

* Delete old build:

rmdir /s /q build
rmdir /s /q dist

---

### Drag & Drop not working

* Ensure:

--hidden-import=tkinterdnd2

---

### Calendar issue

pip install tkcalendar

---

### EXE not opening

* Check antivirus
* Run via terminal

---

## 📁 Project Structure

project-folder/
│
├── app.py
├── zip-folder.ico
├── screenshot.png
├── README.md

---

## 🔧 Tech Stack

* Python
* Tkinter
* TkinterDnD2
* tkcalendar
* Pillow
* PyInstaller

---

## 💡 Future Improvements

* Batch processing
* Auto file name detection
* Web version (React)
* Installer setup (.exe wizard)

---

## 👨‍💻 Author

**Pradul P**
Civil Engineer | BIM | Automation

---

## 📌 License

Free to use and modify.
