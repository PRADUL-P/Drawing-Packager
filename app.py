import os
import sys
import shutil
import zipfile
import json
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkcalendar import DateEntry

# ================= CONFIG & THEME =================
APP_NAME = "LUDARP Drawing Packager"
APP_VERSION = "v2.0"

# Modern Slate / Linear Dark Palette
BG = "#0d1117"             # Outer window background
CARD = "#161b22"           # Main container cards
CARD_SECONDARY = "#21262d"    # Inner slots / item cards
INPUT_BG = "#0d1117"       # Input background
TEXT_MAIN = "#f0f6fc"      # High contrast main text
TEXT_MUTED = "#8b949e"     # Subtle labels
ACCENT = "#238636"         # Success / Action green
ACCENT_BLUE = "#1f6feb"    # Focus / Primary blue
ACCENT_HOVER = "#2ea043"   # Button hover
ACCENT_WARN = "#d29922"    # Warning gold
BORDER = "#30363d"         # Subtle divider borders
BTN_BG = "#21262d"
BTN_HOVER = "#30363d"

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ludarp_packager_config.json")

# ================= UTILITIES =================

def resource_path(relative_path):
    """Resolve resource path for dev and frozen PyInstaller standalone."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def load_config():
    default_config = {
        "recent_clients": [],
        "recent_projects": [],
        "separator": "_",
        "include_date": True,
        "include_rev": False,
        "auto_pack_on_drop": True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                default_config.update(json.load(f))
        except Exception:
            pass
    return default_config


def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
    except Exception:
        pass


def add_to_recent(key, value):
    """Store recent values without duplicates, max 15 entries."""
    if not value or not value.strip():
        return
    value = value.strip()
    config = load_config()
    items = config.get(key, [])
    if value in items:
        items.remove(value)
    items.insert(0, value)
    config[key] = items[:15]
    save_config(config)


def sanitize_filename(name):
    if not name:
        return ""
    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        name = name.replace(ch, '')
    return name.strip()


def format_size(bytes_size):
    if not bytes_size:
        return "0 B"
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def safe_open_folder(path):
    if path and os.path.exists(path):
        try:
            os.startfile(path)
        except Exception:
            pass


def parse_dnd_paths(data):
    """Robust parser for TkinterDnD data that handles paths with spaces (e.g. 'Drawing packer')."""
    if not data:
        return []

    # If entire string points to an existing file/folder, return it
    clean_full = data.strip('{}').strip()
    if os.path.exists(clean_full):
        return [os.path.normpath(clean_full)]

    paths = []
    # Match braced paths like {E:/Drawing packer/file.dwg} OR non-whitespace
    matches = re.findall(r'\{([^}]+)\}|(\S+)', data)
    for m in matches:
        p = m[0] if m[0] else m[1]
        p = p.strip('{}').strip()
        if p and os.path.exists(p):
            paths.append(os.path.normpath(p))

    # Fallback check
    if not paths and os.path.exists(data.strip()):
        return [os.path.normpath(data.strip())]

    return paths


# ================= METADATA & FILE DETECTOR =================

class FileDetector:
    """Scans and detects .zip, .pdf, .dwg and info.txt reliably."""

    @staticmethod
    def parse_txt_metadata(folder_or_files):
        folder = None
        candidates = []

        if isinstance(folder_or_files, list):
            for p in folder_or_files:
                if p.lower().endswith(".txt") and os.path.isfile(p):
                    candidates.append(p)
                elif os.path.isfile(p):
                    folder = os.path.dirname(p)
                elif os.path.isdir(p):
                    folder = p
        elif os.path.isdir(folder_or_files):
            folder = folder_or_files
        elif os.path.isfile(folder_or_files):
            folder = os.path.dirname(folder_or_files)

        if folder and os.path.isdir(folder):
            for f in os.listdir(folder):
                if f.lower().endswith(".txt"):
                    candidates.append(os.path.join(folder, f))

        preferred = ["info.txt", "client.txt", "project.txt", "naming.txt", "00share.txt", "config.txt"]
        chosen = None
        for pref in preferred:
            for c in candidates:
                if os.path.basename(c).lower() == pref:
                    chosen = c
                    break
            if chosen:
                break
        if not chosen and candidates:
            chosen = candidates[0]

        if chosen and os.path.exists(chosen):
            try:
                with open(chosen, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip() and not l.strip().startswith("#")]
                meta = {}
                for l in lines:
                    if ":" in l:
                        k, v = l.split(":", 1)
                        meta[k.strip().lower()] = v.strip()
                    elif "=" in l:
                        k, v = l.split("=", 1)
                        meta[k.strip().lower()] = v.strip()

                if "client" not in meta and len(lines) >= 1:
                    meta["client"] = lines[0]
                if "project" not in meta and len(lines) >= 2:
                    meta["project"] = lines[1]

                client = meta.get("client") or meta.get("client_name") or meta.get("client name") or ""
                project = meta.get("project") or meta.get("project_name") or meta.get("project name") or ""
                return {"client": client, "project": project}, chosen
            except Exception:
                pass

        return {}, None

    @staticmethod
    def scan_files(target):
        """Finds any DWG, PDF, and ZIP files in the target folder or list."""
        all_paths = []
        if isinstance(target, list):
            for item in target:
                if os.path.isdir(item):
                    all_paths.extend([os.path.join(item, f) for f in os.listdir(item) if os.path.isfile(os.path.join(item, f))])
                elif os.path.isfile(item):
                    all_paths.append(item)
        elif os.path.isdir(target):
            all_paths = [os.path.join(target, f) for f in os.listdir(target) if os.path.isfile(os.path.join(target, f))]
        elif os.path.isfile(target):
            all_paths = [target]

        zip_file = None
        pdf_file = None
        dwg_file = None

        for p in all_paths:
            ext = os.path.splitext(p)[1].lower()
            if ext == ".zip" and not zip_file:
                zip_file = p
            elif ext == ".pdf" and not pdf_file:
                pdf_file = p
            elif ext == ".dwg" and not dwg_file:
                dwg_file = p

        return zip_file, pdf_file, dwg_file


# ================= GORGEOUS MINIMALIST GUI =================

class DrawingPackagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("880x560")
        self.root.minsize(820, 520)
        self.root.configure(bg=BG)

        icon_path = resource_path("zip-folder.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.config = load_config()
        self.files = {"zip": None, "pdf": None, "dwg": None}
        self.current_folder = ""

        self.build_ui()
        self.bind_events()
        self.update_preview()

        # Fade in
        self.root.attributes("-alpha", 0)
        self.fade_in(0)

    def fade_in(self, alpha=0):
        alpha += 0.08
        if alpha <= 1.0:
            self.root.attributes("-alpha", alpha)
            self.root.after(16, self.fade_in, alpha)
        else:
            self.root.attributes("-alpha", 1.0)

    def build_ui(self):
        # Register full-window drag & drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.handle_drop)

        # ================= TOP HEADER BAR =================
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=18, pady=(12, 6))

        # Title & Badges
        title_box = tk.Frame(header, bg=BG)
        title_box.pack(side="left")

        tk.Label(title_box, text="🧩 LUDARP Drawing Packager", font=("Segoe UI", 13, "bold"),
                 bg=BG, fg=TEXT_MAIN).pack(side="left")
        tk.Label(title_box, text=f" {APP_VERSION} ", font=("Segoe UI", 8, "bold"),
                 bg=ACCENT_BLUE, fg="white", padx=4, pady=1).pack(side="left", padx=8)

        # Right Action Toggle
        right_header = tk.Frame(header, bg=BG)
        right_header.pack(side="right")

        self.auto_pack_var = tk.BooleanVar(value=self.config.get("auto_pack_on_drop", True))
        chk_autopack = tk.Checkbutton(
            right_header,
            text="⚡ Auto-Pack on Drop",
            variable=self.auto_pack_var,
            font=("Segoe UI", 9, "bold"),
            bg=BG, fg=ACCENT, selectcolor=CARD,
            activebackground=BG,
            command=self.save_preferences
        )
        chk_autopack.pack(side="right")

        # ================= MAIN TWO-COLUMN BODY =================
        main_body = tk.Frame(self.root, bg=BG)
        main_body.pack(fill="both", expand=True, padx=14, pady=4)
        main_body.grid_columnconfigure(0, weight=1, minsize=380)
        main_body.grid_columnconfigure(1, weight=1, minsize=400)
        main_body.grid_rowconfigure(0, weight=1)

        # ----------------- LEFT PANEL: METADATA & NAMING -----------------
        left = tk.Frame(main_body, bg=CARD, relief="flat", padx=16, pady=16, highlightbackground=BORDER, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(4, 6), pady=4)

        # Client Name (Strictly for Client files)
        tk.Label(left, text="CLIENT NAME", font=("Segoe UI", 8, "bold"),
                 bg=CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 0))
        client_box = tk.Frame(left, bg=CARD)
        client_box.pack(fill="x", pady=(2, 10))

        self.client_var = tk.StringVar(value=self.config.get("recent_clients", [""])[0] if self.config.get("recent_clients") else "")
        self.client_entry = tk.Entry(client_box, textvariable=self.client_var, bg=INPUT_BG,
                                     fg=TEXT_MAIN, relief="flat", insertbackground="white",
                                     highlightbackground=BORDER, highlightthickness=1)
        self.client_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.client_var.trace_add("write", lambda *args: self.update_preview())

        btn_paste_c = tk.Button(client_box, text="Paste", font=("Segoe UI", 8),
                                bg=BTN_BG, fg=TEXT_MAIN, relief="flat", padx=10,
                                command=lambda: self.paste_var(self.client_var))
        btn_paste_c.pack(side="right", padx=(6, 0))
        self.add_hover(btn_paste_c, BTN_BG, BTN_HOVER)

        # Project Name (Strictly for Project files)
        tk.Label(left, text="PROJECT NAME", font=("Segoe UI", 8, "bold"),
                 bg=CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 0))
        proj_box = tk.Frame(left, bg=CARD)
        proj_box.pack(fill="x", pady=(2, 10))

        self.project_var = tk.StringVar(value=self.config.get("recent_projects", [""])[0] if self.config.get("recent_projects") else "")
        self.project_entry = tk.Entry(proj_box, textvariable=self.project_var, bg=INPUT_BG,
                                      fg=TEXT_MAIN, relief="flat", insertbackground="white",
                                      highlightbackground=BORDER, highlightthickness=1)
        self.project_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.project_var.trace_add("write", lambda *args: self.update_preview())

        btn_paste_p = tk.Button(proj_box, text="Paste", font=("Segoe UI", 8),
                                bg=BTN_BG, fg=TEXT_MAIN, relief="flat", padx=10,
                                command=lambda: self.paste_var(self.project_var))
        btn_paste_p.pack(side="right", padx=(6, 0))
        self.add_hover(btn_paste_p, BTN_BG, BTN_HOVER)

        # Date Option
        date_bar = tk.Frame(left, bg=CARD)
        date_bar.pack(fill="x", pady=(4, 8))

        self.include_date_var = tk.BooleanVar(value=self.config.get("include_date", True))
        chk_date = tk.Checkbutton(date_bar, text="Add Date to Client files:", variable=self.include_date_var,
                                  font=("Segoe UI", 8), bg=CARD, fg=TEXT_MAIN,
                                  selectcolor=INPUT_BG, activebackground=CARD,
                                  command=self.update_preview)
        chk_date.pack(side="left")

        self.date_picker = DateEntry(date_bar, date_pattern="dd-mm-yyyy",
                                     background=ACCENT_BLUE, foreground="white", borderwidth=0)
        self.date_picker.pack(side="right")
        self.date_picker.bind("<<DateEntrySelected>>", lambda e: self.update_preview())

        # Target 6 Files Live Preview Box
        preview_box = tk.Frame(left, bg=CARD_SECONDARY, relief="flat", padx=12, pady=10, highlightbackground=BORDER, highlightthickness=1)
        preview_box.pack(fill="both", expand=True, pady=(10, 0))

        tk.Label(preview_box, text="OUTPUT TARGET (6 FILES):", font=("Segoe UI", 8, "bold"),
                 bg=CARD_SECONDARY, fg=ACCENT_BLUE).pack(anchor="w")

        self.lbl_client_out = tk.Label(preview_box, text="Client (3): ...", font=("Consolas", 8),
                                       bg=CARD_SECONDARY, fg=TEXT_MAIN, justify="left")
        self.lbl_client_out.pack(anchor="w", pady=(4, 2))

        self.lbl_proj_out = tk.Label(preview_box, text="Project (3): ...", font=("Consolas", 8),
                                     bg=CARD_SECONDARY, fg=TEXT_MAIN, justify="left")
        self.lbl_proj_out.pack(anchor="w", pady=(2, 4))

        # ----------------- RIGHT PANEL: DETECTED FILES & ACTIONS -----------------
        right = tk.Frame(main_body, bg=CARD, relief="flat", padx=16, pady=16, highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 4), pady=4)

        # Big Drag & Drop Slot with Choose Folder Button
        drop_container = tk.Frame(right, bg=INPUT_BG, highlightbackground=BORDER, highlightthickness=1)
        drop_container.pack(fill="x", pady=(0, 8))

        self.drop_slot = tk.Label(
            drop_container,
            text="⬇️ DRAG & DROP FOLDER (e.g. 00share) OR FILES HERE",
            font=("Segoe UI", 9, "bold"), bg=INPUT_BG, fg=TEXT_MAIN,
            pady=8
        )
        self.drop_slot.pack(fill="x")
        self.drop_slot.drop_target_register(DND_FILES)
        self.drop_slot.dnd_bind("<<Drop>>", self.handle_drop)

        btn_choose_folder = tk.Button(
            drop_container, text="📁 Or Select Folder...", font=("Segoe UI", 8, "bold"),
            bg=BTN_BG, fg=ACCENT_BLUE, relief="flat", padx=10, pady=3,
            command=self.browse_folder
        )
        btn_choose_folder.pack(pady=(0, 6))
        self.add_hover(btn_choose_folder, BTN_BG, BTN_HOVER)

        # THREE VISUAL FILE SLOTS (ZIP, CAD, PDF)
        self.zip_card = self.create_file_card(right, "📦 ZIP ARCHIVE", "zip")
        self.dwg_card = self.create_file_card(right, "📐 CAD DRAWING", "dwg")
        self.pdf_card = self.create_file_card(right, "📄 PDF SHEET", "pdf")

        # Packaging Mode Selector
        mode_box = tk.Frame(right, bg=CARD)
        mode_box.pack(fill="x", pady=(6, 6))

        tk.Label(mode_box, text="Mode:", font=("Segoe UI", 8, "bold"), bg=CARD, fg=TEXT_MUTED).pack(side="left")
        self.mode_var = tk.StringVar(value="CAD + PDF")
        self.mode_options = ["CAD + PDF", "ZIP + PDF", "All in One (CAD+PDF+ZIP)"]
        self.mode_menu = tk.OptionMenu(mode_box, self.mode_var, *self.mode_options)
        self.mode_menu.config(bg=CARD_SECONDARY, fg=TEXT_MAIN, relief="flat", highlightthickness=0)
        self.mode_menu["menu"].config(bg=CARD_SECONDARY, fg=TEXT_MAIN)
        self.mode_menu.pack(side="right", fill="x", expand=True, padx=(8, 0))

        # Big Action Button
        self.btn_generate = tk.Button(
            right, text="⚡ Generate All 6 Package Files", font=("Segoe UI", 10, "bold"),
            bg=ACCENT, fg="white", relief="flat", pady=8,
            command=self.run_packaging
        )
        self.btn_generate.pack(fill="x", pady=(6, 4))
        self.add_hover(self.btn_generate, ACCENT, ACCENT_HOVER)

        # Sub-buttons: Open folder & Reset
        action_row = tk.Frame(right, bg=CARD)
        action_row.pack(fill="x")

        btn_open = tk.Button(action_row, text="📂 Open Output Folder", font=("Segoe UI", 8),
                             bg=BTN_BG, fg=TEXT_MAIN, relief="flat", pady=4,
                             command=self.open_output)
        btn_open.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self.add_hover(btn_open, BTN_BG, BTN_HOVER)

        btn_reset = tk.Button(action_row, text="🔄 Reset", font=("Segoe UI", 8),
                              bg=BTN_BG, fg=TEXT_MAIN, relief="flat", pady=4,
                              command=self.reset_all)
        btn_reset.pack(side="right", fill="x", expand=True, padx=(3, 0))
        self.add_hover(btn_reset, BTN_BG, BTN_HOVER)

        # Status text
        self.status_lbl = tk.Label(right, text="Ready. Drop folder or files.", font=("Segoe UI", 8),
                                   bg=CARD, fg=TEXT_MUTED)
        self.status_lbl.pack(anchor="w", pady=(6, 0))

        # ================= BOTTOM STATUS FOOTER =================
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=18, pady=(4, 8))

        self.info_status_lbl = tk.Label(footer, text="No info.txt active", font=("Segoe UI", 8),
                                        bg=BG, fg=TEXT_MUTED)
        self.info_status_lbl.pack(side="left")

        tk.Label(footer, text="Press <Enter> to Generate | LUDARP", font=("Segoe UI", 8),
                 bg=BG, fg=TEXT_MUTED).pack(side="right")

    def create_file_card(self, parent, title, ftype):
        """Creates a modern visual status slot for ZIP, CAD, or PDF."""
        card = tk.Frame(parent, bg=CARD_SECONDARY, relief="flat", padx=8, pady=5, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=2)

        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), bg=CARD_SECONDARY, fg=TEXT_MUTED, width=14, anchor="w")
        lbl_title.pack(side="left")

        lbl_name = tk.Label(card, text="— No file loaded —", font=("Segoe UI", 8), bg=CARD_SECONDARY, fg=TEXT_MUTED, anchor="w")
        lbl_name.pack(side="left", fill="x", expand=True, padx=4)

        btn_browse = tk.Button(card, text="Browse", font=("Segoe UI", 7), bg=BTN_BG, fg=TEXT_MAIN, relief="flat", padx=6,
                               command=lambda t=ftype: self.manual_browse_file(t))
        btn_browse.pack(side="right")
        self.add_hover(btn_browse, BTN_BG, BTN_HOVER)

        return {"frame": card, "title": lbl_title, "label": lbl_name, "btn": btn_browse}

    def add_hover(self, widget, normal, hover):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal))

    def bind_events(self):
        self.include_date_var.trace_add("write", lambda *args: self.update_preview())
        self.root.bind("<Return>", lambda e: self.run_packaging())

    def save_preferences(self):
        conf = load_config()
        conf["auto_pack_on_drop"] = self.auto_pack_var.get()
        conf["include_date"] = self.include_date_var.get()
        save_config(conf)

    def paste_var(self, str_var):
        try:
            val = self.root.clipboard_get()
            if val:
                str_var.set(val.strip())
                self.update_preview()
        except Exception:
            pass

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Project / Dispatch Folder")
        if folder:
            self.load_target([folder])

    def manual_browse_file(self, ftype):
        ext_map = {"zip": [("ZIP Archive", "*.zip")], "dwg": [("AutoCAD Drawing", "*.dwg")], "pdf": [("PDF Sheet", "*.pdf")]}
        path = filedialog.askopenfilename(filetypes=ext_map.get(ftype, [("All files", "*.*")]))
        if path:
            self.files[ftype] = os.path.normpath(path)
            if not self.current_folder:
                self.current_folder = os.path.dirname(path)
            self.update_file_cards()
            self.update_preview()

    def update_file_cards(self):
        """Updates the visual cards for ZIP, CAD, and PDF."""
        # 1. ZIP
        if self.files["zip"] and os.path.exists(self.files["zip"]):
            sz = format_size(os.path.getsize(self.files["zip"]))
            self.zip_card["label"].config(text=f"✓ {os.path.basename(self.files['zip'])} ({sz})", fg=ACCENT)
        else:
            self.zip_card["label"].config(text="— None (optional) —", fg=TEXT_MUTED)

        # 2. DWG
        if self.files["dwg"] and os.path.exists(self.files["dwg"]):
            sz = format_size(os.path.getsize(self.files["dwg"]))
            self.dwg_card["label"].config(text=f"✓ {os.path.basename(self.files['dwg'])} ({sz})", fg=ACCENT)
        else:
            self.dwg_card["label"].config(text="— Missing DWG —", fg=ACCENT_WARN)

        # 3. PDF
        if self.files["pdf"] and os.path.exists(self.files["pdf"]):
            sz = format_size(os.path.getsize(self.files["pdf"]))
            self.pdf_card["label"].config(text=f"✓ {os.path.basename(self.files['pdf'])} ({sz})", fg=ACCENT)
        else:
            self.pdf_card["label"].config(text="— Missing PDF —", fg=ACCENT_WARN)

        # Auto-adjust mode based on zip existence
        if self.files["zip"]:
            self.mode_var.set("All in One (CAD+PDF+ZIP)")
        else:
            self.mode_var.set("CAD + PDF")

    def get_client_base(self):
        c = sanitize_filename(self.client_var.get().strip()) or "CLIENT"
        if self.include_date_var.get():
            try:
                d = self.date_picker.get_date().strftime("%d-%m-%Y")
            except Exception:
                d = datetime.now().strftime("%d-%m-%Y")
            return f"{c}_{d}"
        return c

    def get_project_base(self):
        p = sanitize_filename(self.project_var.get().strip())
        if not p:
            if self.files["pdf"]:
                p = os.path.splitext(os.path.basename(self.files["pdf"]))[0]
            elif self.files["dwg"]:
                p = os.path.splitext(os.path.basename(self.files["dwg"]))[0]
            else:
                p = "PROJECT"
        return p

    def update_preview(self):
        c_base = self.get_client_base()
        p_base = self.get_project_base()
        self.lbl_client_out.config(text=f"Client (3):  {c_base}.(pdf/dwg/zip)")
        self.lbl_proj_out.config(text=f"Project (3): {p_base}.(pdf/dwg/zip)")

    # ================= DRAG & DROP HANDLER =================

    def handle_drop(self, event):
        clean_paths = parse_dnd_paths(event.data)
        if not clean_paths:
            return
        self.load_target(clean_paths)

    def load_target(self, clean_paths):
        # Determine folder context
        if len(clean_paths) == 1 and os.path.isdir(clean_paths[0]):
            self.current_folder = clean_paths[0]
            target = clean_paths[0]
        else:
            self.current_folder = os.path.dirname(clean_paths[0])
            target = clean_paths

        # 1. Parse info.txt from folder if present
        meta, txt_path = FileDetector.parse_txt_metadata(target)
        if meta and (meta.get("client") or meta.get("project")):
            if meta.get("client"):
                self.client_var.set(meta["client"])
            if meta.get("project"):
                self.project_var.set(meta["project"])
            self.info_status_lbl.config(
                text=f"✓ Config loaded from: {os.path.basename(txt_path)}",
                fg=ACCENT
            )
        else:
            self.info_status_lbl.config(
                text="No info.txt detected (using manual entries)",
                fg=TEXT_MUTED
            )

        # 2. Detect ZIP, PDF, DWG
        z, p, d = FileDetector.scan_files(target)
        if z:
            self.files["zip"] = z
        if p:
            self.files["pdf"] = p
        if d:
            self.files["dwg"] = d

        self.update_file_cards()
        self.update_preview()

        loaded = [k.upper() for k, v in self.files.items() if v]
        self.status_lbl.config(text=f"Loaded: {', '.join(loaded) if loaded else 'None'}", fg=ACCENT)

        # ⚡ ZERO-CLICK AUTO-PACK: if enabled and client + drawing are present
        if self.auto_pack_var.get() and self.client_var.get().strip() and self.files["pdf"]:
            self.root.update_idletasks()
            self.run_packaging()

    # ================= PACKAGING ENGINE =================

    def get_output_directory(self):
        if self.current_folder and os.path.exists(self.current_folder):
            return os.path.join(self.current_folder, "output_files")
        if self.files["pdf"]:
            return os.path.join(os.path.dirname(self.files["pdf"]), "output_files")
        return os.path.join(os.getcwd(), "output_files")

    def open_output(self):
        out_dir = self.get_output_directory()
        if os.path.exists(out_dir):
            safe_open_folder(out_dir)
        else:
            messagebox.showinfo("Output", f"Output folder does not exist yet:\n{out_dir}\nRun 'Generate All 6 Package Files' first.")

    def reset_all(self):
        self.client_var.set("")
        self.project_var.set("")
        self.files = {"zip": None, "pdf": None, "dwg": None}
        self.update_file_cards()
        self.update_preview()
        self.status_lbl.config(text="Reset done.", fg=TEXT_MUTED)

    def run_packaging(self):
        client = sanitize_filename(self.client_var.get().strip())
        project = self.get_project_base()

        if not client:
            messagebox.showerror("Client Name Required", "Please enter a Client Name (or provide info.txt).")
            return

        if not self.files["pdf"]:
            messagebox.showerror("PDF Required", "A PDF sheet is required for packaging.")
            return

        out_dir = self.get_output_directory()
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not create output folder:\n{e}")
            return

        # Save to history
        add_to_recent("recent_clients", client)
        if project:
            add_to_recent("recent_projects", project)

        mode = self.mode_var.get()
        c_base = self.get_client_base()
        p_base = project

        self.btn_generate.config(state="disabled")
        self.status_lbl.config(text="Creating 6 package files...", fg=ACCENT_BLUE)
        self.root.update_idletasks()

        try:
            # 1. CLIENT SET (3 files: pdf, dwg, zip)
            self.create_bundle(out_dir, c_base, self.files["pdf"], self.files["dwg"], self.files["zip"], mode, inner_label=client)

            # 2. PROJECT SET (3 files: pdf, dwg, zip)
            if p_base != c_base:
                self.create_bundle(out_dir, p_base, self.files["pdf"], self.files["dwg"], self.files["zip"], mode, inner_label=p_base)

            self.status_lbl.config(text="Done! Created all 6 files ✅", fg=ACCENT)
            safe_open_folder(out_dir)

        except Exception as err:
            messagebox.showerror("Error", f"Failed to package files:\n{str(err)}")
            self.status_lbl.config(text=f"Error: {err}", fg=ACCENT_WARN)
        finally:
            self.btn_generate.config(state="normal")

    def create_bundle(self, dest_folder, bundle_name, pdf_src, dwg_src, zip_src, mode, inner_label=None):
        inner = inner_label or bundle_name
        pdf_dest = os.path.join(dest_folder, f"{bundle_name}.pdf")
        dwg_dest = os.path.join(dest_folder, f"{bundle_name}.dwg")
        zip_dest = os.path.join(dest_folder, f"{bundle_name}.zip")

        if pdf_src and os.path.exists(pdf_src):
            shutil.copy2(pdf_src, pdf_dest)

        if dwg_src and os.path.exists(dwg_src):
            shutil.copy2(dwg_src, dwg_dest)

        with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as z:
            if pdf_src and os.path.exists(pdf_dest):
                z.write(pdf_dest, f"{inner}.pdf")

            if mode in ["CAD + PDF", "All in One (CAD+PDF+ZIP)"] and dwg_src and os.path.exists(dwg_dest):
                z.write(dwg_dest, f"{inner}.dwg")

            if mode in ["ZIP + PDF", "All in One (CAD+PDF+ZIP)"] and zip_src and os.path.exists(zip_src):
                z.write(zip_src, f"{inner}.zip")


# ================= APPLICATION ENTRY POINT =================

def main():
    root = TkinterDnD.Tk()
    app = DrawingPackagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
