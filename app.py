import os
import shutil
import zipfile
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkcalendar import DateEntry

# ================= CONFIG =================
BG = "#0b1220"
CARD = "#111827"
INPUT = "#1f2937"
TEXT = "#e5e7eb"
ACCENT = "#3b82f6"
ACCENT_HOVER = "#2563eb"
LABEL = "#9ca3af"
BTN_DARK = "#374151"
BTN_HOVER = "#4b5563"

APP_VERSION = "v1.0"

manual_files = {"zip": None, "pdf": None, "dwg": None}

# ================= CORE =================

def detect_files(folder):
    zip_f = pdf_f = dwg_f = None
    for f in os.listdir(folder):
        full = os.path.join(folder, f)
        fname = f.lower()
        if fname.endswith(".zip"):
            zip_f = full
        elif fname.endswith(".pdf"):
            pdf_f = full
        elif fname.endswith(".dwg"):
            dwg_f = full
    return zip_f, pdf_f, dwg_f


def copy_files(src_pdf, src_dwg, dest_pdf, dest_dwg):
    shutil.copy2(src_pdf, dest_pdf)
    shutil.copy2(src_dwg, dest_dwg)


def create_zip(zip_name, zip_path, pdf_file, dwg_file, label, mode):
    with zipfile.ZipFile(zip_name, 'w') as z:
        if mode == "FULL" and zip_path:
            z.write(zip_path, label + ".zip")
        z.write(pdf_file, label + ".pdf")
        if mode == "CADPDF":
            z.write(dwg_file, label + ".dwg")


def safe_open_folder(path):
    if os.path.exists(path):
        os.startfile(path)

# ================= NEW FEATURE =================

def paste_to_entry(entry):
    try:
        text = root.clipboard_get()
        entry.delete(0, tk.END)
        entry.insert(0, text)
    except:
        pass

# ================= UI UPDATE =================

def set_mode(value):
    mode_var.set(value)
    mode_label.config(text=f"Mode: {value}")


def update_ui():
    zip_label.config(text=f"ZIP: {os.path.basename(manual_files['zip']) if manual_files['zip'] else '-'}")
    pdf_label.config(text=f"PDF: {os.path.basename(manual_files['pdf']) if manual_files['pdf'] else '-'}")
    dwg_label.config(text=f"DWG: {os.path.basename(manual_files['dwg']) if manual_files['dwg'] else '-'}")

    menu = mode_menu["menu"]
    menu.delete(0, "end")

    options = []

    if manual_files["zip"]:
        options = ["ZIP + PDF", "CAD + PDF"]
    else:
        options = ["CAD + PDF"]

    for opt in options:
        menu.add_command(label=opt, command=lambda v=opt: set_mode(v))

    mode_var.set(options[0])
    mode_label.config(text=f"Mode: {options[0]}")


def get_mode():
    return "FULL" if mode_var.get() == "ZIP + PDF" else "CADPDF"

# ================= INPUT =================

def browse_input():
    folder = filedialog.askdirectory()
    if folder:
        input_var.set(folder)
        z, p, d = detect_files(folder)
        manual_files.update({"zip": z, "pdf": p, "dwg": d})
        update_ui()


def browse_output():
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)


def drop(event):
    files = root.tk.splitlist(event.data)
    for f in files:
        f = f.strip("{}").strip()
        fname = f.lower()
        if fname.endswith(".zip"):
            manual_files["zip"] = f
        elif fname.endswith(".pdf"):
            manual_files["pdf"] = f
        elif fname.endswith(".dwg"):
            manual_files["dwg"] = f
    update_ui()

# ================= MAIN ACTION =================

def run():
    try:
        client = client_entry.get().strip()
        project = project_entry.get().strip()
        input_folder = input_var.get()
        output_folder = output_var.get() or os.path.join(input_folder, "output_files")

        if not client:
            messagebox.showerror("Error", "Client name required")
            return

        os.makedirs(output_folder, exist_ok=True)

        # 🔥 DATE CONTROL
        date = date_picker.get_date().strftime("%d-%m-%Y") if include_date_var.get() else ""

        zip_path = manual_files["zip"]
        pdf_path = manual_files["pdf"]
        dwg_path = manual_files["dwg"]

        if not pdf_path or not dwg_path:
            messagebox.showerror("Error", "PDF & DWG required")
            return

        if not project:
            project = os.path.splitext(os.path.basename(pdf_path))[0]

        mode = get_mode()
        status_lbl.config(text=f"Processing ({mode})...")

        base = f"{client}_{date}" if date else client

        c_pdf = os.path.join(output_folder, base + ".pdf")
        c_dwg = os.path.join(output_folder, base + ".dwg")

        copy_files(pdf_path, dwg_path, c_pdf, c_dwg)
        create_zip(os.path.join(output_folder, base + ".zip"),
                   zip_path, c_pdf, c_dwg, client, mode)

        p_pdf = os.path.join(output_folder, project + ".pdf")
        p_dwg = os.path.join(output_folder, project + ".dwg")

        copy_files(pdf_path, dwg_path, p_pdf, p_dwg)
        create_zip(os.path.join(output_folder, project + ".zip"),
                   zip_path, p_pdf, p_dwg, project, mode)

        status_lbl.config(text="Done ✅")
        safe_open_folder(output_folder)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def reset():
    client_entry.delete(0, tk.END)
    project_entry.delete(0, tk.END)
    input_var.set("")
    output_var.set("")
    date_picker.set_date(datetime.now())
    include_date_var.set(True)
    manual_files.update({"zip": None, "pdf": None, "dwg": None})
    update_ui()
    status_lbl.config(text="Reset done")

# ================= UI =================

root = TkinterDnD.Tk()
root.title("LUDARP Drawing Packager")

base_path = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(base_path, "zip-folder.ico")
try:
    root.iconbitmap(icon_path)
except:
    pass

root.geometry("800x480")
root.configure(bg=BG)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)

def add_hover(widget, normal, hover):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal))

left = tk.Frame(root, bg=CARD)
left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

right = tk.Frame(root, bg=CARD)
right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

def label(parent, text):
    tk.Label(parent, text=text, bg=CARD, fg=LABEL).pack(anchor="w", padx=8, pady=(6, 0))

# ================= UPDATED FIELDS =================

label(left, "Client Name")
client_frame = tk.Frame(left, bg=CARD)
client_frame.pack(fill="x", padx=8, pady=4)

client_entry = tk.Entry(client_frame, bg=INPUT, fg=TEXT, relief="flat")
client_entry.pack(side="left", fill="x", expand=True, ipady=5)

btn_paste_client = tk.Button(client_frame, text="Paste", bg=BTN_DARK, fg="white",
                             command=lambda: paste_to_entry(client_entry))
btn_paste_client.pack(side="right", padx=4)
add_hover(btn_paste_client, BTN_DARK, BTN_HOVER)


label(left, "Project Name")
project_frame = tk.Frame(left, bg=CARD)
project_frame.pack(fill="x", padx=8, pady=4)

project_entry = tk.Entry(project_frame, bg=INPUT, fg=TEXT, relief="flat")
project_entry.pack(side="left", fill="x", expand=True, ipady=5)

btn_paste_project = tk.Button(project_frame, text="Paste", bg=BTN_DARK, fg="white",
                              command=lambda: paste_to_entry(project_entry))
btn_paste_project.pack(side="right", padx=4)
add_hover(btn_paste_project, BTN_DARK, BTN_HOVER)


label(left, "Date")
date_frame = tk.Frame(left, bg=CARD)
date_frame.pack(fill="x", padx=8, pady=4)

date_picker = DateEntry(date_frame, date_pattern="dd-mm-yyyy")
date_picker.pack(side="left", fill="x", expand=True)

include_date_var = tk.BooleanVar(value=True)

chk_date = tk.Checkbutton(date_frame, text="Include Date",
                          variable=include_date_var,
                          bg=CARD, fg=TEXT, selectcolor=INPUT,
                          activebackground=CARD)
chk_date.pack(side="right", padx=6)

# ================= REMAINING UI (UNCHANGED) =================

label(left, "Input Folder")
input_var = tk.StringVar()
tk.Entry(left, textvariable=input_var, bg=INPUT, fg=TEXT).pack(fill="x", padx=8, pady=4)

btn_input = tk.Button(left, text="Select Input Folder", bg=ACCENT, fg="white", command=browse_input)
btn_input.pack(fill="x", padx=8, pady=4)
add_hover(btn_input, ACCENT, ACCENT_HOVER)

label(left, "Output Folder")
output_var = tk.StringVar()
tk.Entry(left, textvariable=output_var, bg=INPUT, fg=TEXT).pack(fill="x", padx=8, pady=4)

btn_output = tk.Button(left, text="Select Output Folder", bg=BTN_DARK, fg="white", command=browse_output)
btn_output.pack(fill="x", padx=8, pady=4)
add_hover(btn_output, BTN_DARK, BTN_HOVER)

drop_area = tk.Label(right, text="Drag & Drop Files", bg=INPUT, fg=TEXT, height=2)
drop_area.pack(fill="x", pady=6)
drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind('<<Drop>>', drop)

zip_label = tk.Label(right, text="ZIP: -", bg=CARD, fg=TEXT)
zip_label.pack(anchor="w", padx=8)

pdf_label = tk.Label(right, text="PDF: -", bg=CARD, fg=TEXT)
pdf_label.pack(anchor="w", padx=8)

dwg_label = tk.Label(right, text="DWG: -", bg=CARD, fg=TEXT)
dwg_label.pack(anchor="w", padx=8)

mode_var = tk.StringVar()
mode_menu = tk.OptionMenu(right, mode_var, "")
mode_menu.config(bg=INPUT, fg=TEXT, highlightthickness=0)
mode_menu.pack(fill="x", padx=8, pady=6)

mode_label = tk.Label(right, text="Mode: -", bg=CARD, fg=ACCENT)
mode_label.pack(anchor="w", padx=8)

btn_run = tk.Button(right, text="Generate", bg=ACCENT, fg="white", command=run)
btn_run.pack(fill="x", padx=8, pady=8)
add_hover(btn_run, ACCENT, ACCENT_HOVER)

btn_open = tk.Button(right, text="Open Output Folder", bg=BTN_DARK, fg="white",
                     command=lambda: safe_open_folder(output_var.get() or os.path.join(input_var.get(), "output_files")))
btn_open.pack(fill="x", padx=8, pady=4)
add_hover(btn_open, BTN_DARK, BTN_HOVER)

btn_reset = tk.Button(right, text="Reset", bg=BTN_DARK, fg="white", command=reset)
btn_reset.pack(fill="x", padx=8, pady=4)
add_hover(btn_reset, BTN_DARK, BTN_HOVER)

status_lbl = tk.Label(right, text="", bg=CARD, fg=ACCENT)
status_lbl.pack(pady=5)

footer = tk.Frame(root, bg=BG)
footer.grid(row=1, column=0, columnspan=2, sticky="ew")

tk.Label(footer, text=f"LUDARP Drawing Packager | Version {APP_VERSION}",
         bg=BG, fg=LABEL).pack(pady=2)

def fade_in(alpha=0):
    alpha += 0.05
    if alpha <= 1:
        root.attributes("-alpha", alpha)
        root.after(20, fade_in, alpha)

root.attributes("-alpha", 0)
fade_in()

update_ui()
root.mainloop()