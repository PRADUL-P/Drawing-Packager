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
from PIL import Image, ImageDraw, ImageTk

# Enable Windows DPI Awareness for crisp fonts and borders
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ================= DESIGN SYSTEM & PALETTE =================
APP_NAME = "LUDARP Drawing Packager"
APP_VERSION = "v2.0"

# Premium Obsidian Slate Palette (Linear / Raycast / Figma aesthetics)
BG = "#0b0f17"              # Deep canvas background
CARD_BG = "#131b26"         # Main container card
CARD_SURFACE = "#182230"    # Elevated item surface
CARD_BORDER = "#223145"     # Refined subtle card borders
INPUT_BG = "#0d131c"        # Input background
INPUT_BORDER = "#26354a"    # Input normal border
INPUT_FOCUS = "#38bdf8"     # Input focus electric blue

# Typography Colors
TEXT_HEAD = "#f8fafc"       # High contrast pure white
TEXT_BODY = "#e2e8f0"       # Body text
TEXT_MUTED = "#8295ab"      # Secondary labels & hints
TEXT_FAINT = "#475569"      # Very subtle text

# Functional & Brand Accents
ACCENT_BLUE = "#2563eb"     # Royal Electric Blue
ACCENT_BLUE_HOVER = "#1d4ed8"
ACCENT_GREEN = "#10b981"    # Emerald action
ACCENT_GREEN_HOVER = "#059669"
ACCENT_WARN = "#f59e0b"     # Amber warning
ACCENT_CRIMSON = "#ef4444"  # Crimson red

# Badge Colors
BADGE_PDF_BG = "#3b171a"
BADGE_PDF_FG = "#f87171"
BADGE_CAD_BG = "#0f2c3f"
BADGE_CAD_FG = "#38bdf8"
BADGE_ZIP_BG = "#38280f"
BADGE_ZIP_FG = "#fbbf24"
BADGE_READY_BG = "#064e3b"
BADGE_READY_FG = "#34d399"

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ludarp_packager_config.json")

# ================= UTILITIES & ASSET RESOLUTION =================

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
    clean_full = data.strip('{}').strip()
    if os.path.exists(clean_full):
        return [os.path.normpath(clean_full)]

    paths = []
    matches = re.findall(r'\{([^}]+)\}|(\S+)', data)
    for m in matches:
        p = m[0] if m[0] else m[1]
        p = p.strip('{}').strip()
        if p and os.path.exists(p):
            paths.append(os.path.normpath(p))

    if not paths and os.path.exists(data.strip()):
        return [os.path.normpath(data.strip())]

    return paths


# ================= CUSTOM MODERN WIDGETS =================

class ModernToggle(tk.Canvas):
    """A sleek iOS/macOS-style smooth pill toggle switch."""
    def __init__(self, parent, variable, command=None, bg=BG, width=42, height=22):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, cursor="hand2")
        self.variable = variable
        self.command = command
        self.w = width
        self.h = height
        self.bind("<Button-1>", self.on_click)
        self.variable.trace_add("write", lambda *args: self.redraw())
        self.redraw()

    def on_click(self, event):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()

    def redraw(self):
        self.delete("all")
        is_on = self.variable.get()
        track_color = ACCENT_GREEN if is_on else "#334155"
        thumb_color = "#ffffff"

        # Draw rounded pill track
        r = self.h // 2
        # Left cap, right cap, center
        self.create_arc((0, 0, self.h, self.h), start=90, extent=180, fill=track_color, outline=track_color)
        self.create_arc((self.w - self.h, 0, self.w, self.h), start=270, extent=180, fill=track_color, outline=track_color)
        self.create_rectangle((r, 0, self.w - r, self.h), fill=track_color, outline=track_color)

        # Draw thumb knob
        pad = 3
        th_dia = self.h - (pad * 2)
        x = (self.w - th_dia - pad) if is_on else pad
        self.create_oval((x, pad, x + th_dia, pad + th_dia), fill=thumb_color, outline=thumb_color)


class ModernButton(tk.Canvas):
    """A high-end anti-aliased pill button with icon and hover effects."""
    def __init__(self, parent, text, command, bg_color=CARD_SURFACE, hover_color=CARD_BORDER,
                 text_color=TEXT_HEAD, font=("Segoe UI", 9, "bold"), height=36, radius=8,
                 outline_color=None, cursor="hand2", **kwargs):
        super().__init__(parent, height=height, bg=parent["bg"], highlightthickness=0, cursor=cursor, **kwargs)
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.current_bg = bg_color
        self.text_color = text_color
        self.outline_color = outline_color
        self.font = font
        self.h = height
        self.radius = radius

        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def on_enter(self, event):
        self.current_bg = self.hover_color
        self.redraw()

    def on_leave(self, event):
        self.current_bg = self.bg_color
        self.redraw()

    def on_click(self, event):
        if self.command:
            self.command()

    def redraw(self):
        w = self.winfo_width()
        h = self.h
        if w < 10:
            return
        self.delete("all")

        # Smooth polygon approximation for rounded corners
        r = min(self.radius, h // 2)
        points = [
            r, 0,
            w - r, 0,
            w, 0,
            w, r,
            w, h - r,
            w, h,
            w - r, h,
            r, h,
            0, h,
            0, h - r,
            0, r,
            0, 0
        ]
        outline = self.outline_color or self.current_bg
        self.create_polygon(points, smooth=True, fill=self.current_bg, outline=outline, width=1)
        self.create_text(w // 2, h // 2, text=self.text, fill=self.text_color, font=self.font)


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


# ================= THE MASTER APPLICATION =================

class DrawingPackagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("960x600")
        self.root.minsize(900, 560)
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

        self.setup_ttk_styles()
        self.build_ui()
        self.bind_events()
        self.update_preview()

        # Smooth fade-in
        self.root.attributes("-alpha", 0)
        self.fade_in(0)

    def fade_in(self, alpha=0):
        alpha += 0.08
        if alpha <= 1.0:
            self.root.attributes("-alpha", alpha)
            self.root.after(16, self.fade_in, alpha)
        else:
            self.root.attributes("-alpha", 1.0)

    def setup_ttk_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", background=CARD_BG, foreground=TEXT_HEAD, font=("Segoe UI", 9))

    def build_ui(self):
        # Full-window drag & drop registration
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.handle_drop)

        # ================= TOP HEADER (Brand & Controls) =================
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(16, 10))

        # Brand Title & Version Pill
        brand_frame = tk.Frame(header, bg=BG)
        brand_frame.pack(side="left")

        tk.Label(brand_frame, text="🧩 LUDARP Drawing Packager", font=("Segoe UI", 14, "bold"),
                 bg=BG, fg=TEXT_HEAD).pack(side="left")

        ver_pill = tk.Label(brand_frame, text=f" {APP_VERSION} ", font=("Segoe UI", 8, "bold"),
                            bg=ACCENT_BLUE, fg="white", padx=5, pady=1)
        ver_pill.pack(side="left", padx=10)

        # Right Controls: Top Generate info.txt & Modern Auto-Pack Toggle
        ctrl_frame = tk.Frame(header, bg=BG)
        ctrl_frame.pack(side="right")

        btn_top_txt = tk.Button(
            ctrl_frame, text="📄 Generate info.txt", font=("Segoe UI", 8, "bold"),
            bg=CARD_SURFACE, fg=TEXT_HEAD, relief="flat", padx=12, pady=4,
            activebackground=CARD_BORDER, activeforeground="white",
            command=self.generate_info_txt
        )
        btn_top_txt.pack(side="left", padx=(0, 14))
        self.add_hover(btn_top_txt, CARD_SURFACE, CARD_BORDER)

        tk.Label(ctrl_frame, text="⚡ Auto-Pack on Drop:", font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=TEXT_MUTED).pack(side="left", padx=(0, 6))

        self.auto_pack_var = tk.BooleanVar(value=self.config.get("auto_pack_on_drop", True))
        self.toggle_autopack = ModernToggle(ctrl_frame, self.auto_pack_var, command=self.save_preferences, bg=BG)
        self.toggle_autopack.pack(side="left")

        # ================= TWO-COLUMN MASTER WORKSPACE =================
        workspace = tk.Frame(self.root, bg=BG)
        workspace.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        workspace.grid_columnconfigure(0, weight=1, minsize=420)
        workspace.grid_columnconfigure(1, weight=1, minsize=450)
        workspace.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT COLUMN: METADATA, REVISION & CLIENT-PROJECT SETUP
        # -------------------------------------------------------------
        left_card = tk.Frame(workspace, bg=CARD_BG, relief="flat", padx=18, pady=16,
                             highlightbackground=CARD_BORDER, highlightthickness=1)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Header Title
        tk.Label(left_card, text="📋  DISPATCH DETAILS", font=("Segoe UI", 9, "bold"),
                 bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 8))

        # Client Name Field
        tk.Label(left_card, text="CLIENT NAME (Strictly for Client Files)", font=("Segoe UI", 8, "bold"),
                 bg=CARD_BG, fg=TEXT_HEAD).pack(anchor="w")

        c_box = tk.Frame(left_card, bg=CARD_BG)
        c_box.pack(fill="x", pady=(3, 10))

        self.client_var = tk.StringVar(value=self.config.get("recent_clients", [""])[0] if self.config.get("recent_clients") else "")
        self.client_entry = tk.Entry(c_box, textvariable=self.client_var, bg=INPUT_BG,
                                     fg=TEXT_HEAD, relief="flat", insertbackground="white",
                                     font=("Segoe UI", 10), highlightbackground=INPUT_BORDER, highlightthickness=1)
        self.client_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 6))
        self.client_var.trace_add("write", lambda *args: self.update_preview())
        self.bind_input_glow(self.client_entry)

        btn_c_paste = tk.Button(c_box, text="Paste", font=("Segoe UI", 8),
                                bg=CARD_SURFACE, fg=TEXT_HEAD, relief="flat", padx=10, pady=5,
                                command=lambda: self.paste_var(self.client_var))
        btn_c_paste.pack(side="right")
        self.add_hover(btn_c_paste, CARD_SURFACE, CARD_BORDER)

        # Project Name Field
        tk.Label(left_card, text="PROJECT NAME (Strictly for Project Files)", font=("Segoe UI", 8, "bold"),
                 bg=CARD_BG, fg=TEXT_HEAD).pack(anchor="w")

        p_box = tk.Frame(left_card, bg=CARD_BG)
        p_box.pack(fill="x", pady=(3, 10))

        self.project_var = tk.StringVar(value=self.config.get("recent_projects", [""])[0] if self.config.get("recent_projects") else "")
        self.project_entry = tk.Entry(p_box, textvariable=self.project_var, bg=INPUT_BG,
                                      fg=TEXT_HEAD, relief="flat", insertbackground="white",
                                      font=("Segoe UI", 10), highlightbackground=INPUT_BORDER, highlightthickness=1)
        self.project_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 6))
        self.project_var.trace_add("write", lambda *args: self.update_preview())
        self.bind_input_glow(self.project_entry)

        btn_p_paste = tk.Button(p_box, text="Paste", font=("Segoe UI", 8),
                                bg=CARD_SURFACE, fg=TEXT_HEAD, relief="flat", padx=10, pady=5,
                                command=lambda: self.paste_var(self.project_var))
        btn_p_paste.pack(side="right")
        self.add_hover(btn_p_paste, CARD_SURFACE, CARD_BORDER)

        # Date Bar Option with Modern Toggle
        date_bar = tk.Frame(left_card, bg=CARD_SURFACE, padx=10, pady=6, highlightbackground=CARD_BORDER, highlightthickness=1)
        date_bar.pack(fill="x", pady=(0, 10))

        self.include_date_var = tk.BooleanVar(value=self.config.get("include_date", True))
        self.toggle_date = ModernToggle(date_bar, self.include_date_var, command=self.update_preview, bg=CARD_SURFACE)
        self.toggle_date.pack(side="left", padx=(0, 8))

        tk.Label(date_bar, text="Include Date on Client Package", font=("Segoe UI", 8, "bold"),
                 bg=CARD_SURFACE, fg=TEXT_HEAD).pack(side="left")

        self.date_picker = DateEntry(date_bar, date_pattern="dd-mm-yyyy",
                                     background=ACCENT_BLUE, foreground="white", borderwidth=0)
        self.date_picker.pack(side="right")
        self.date_picker.bind("<<DateEntrySelected>>", lambda e: self.update_preview())

        # Generate info.txt Helper Button
        btn_gen_info = tk.Button(
            left_card, text="💾 Save Current Names as info.txt", font=("Segoe UI", 8, "bold"),
            bg=CARD_SURFACE, fg=ACCENT_BLUE, relief="flat", pady=5,
            command=self.generate_info_txt
        )
        btn_gen_info.pack(fill="x", pady=(0, 12))
        self.add_hover(btn_gen_info, CARD_SURFACE, CARD_BORDER)

        # Output Target Manifest (Live 6 Files Visual Card)
        preview_card = tk.Frame(left_card, bg=CARD_SURFACE, padx=12, pady=10, highlightbackground=CARD_BORDER, highlightthickness=1)
        preview_card.pack(fill="both", expand=True)

        tk.Label(preview_card, text="TARGET OUTPUT MANIFEST (6 FILES)", font=("Segoe UI", 8, "bold"),
                 bg=CARD_SURFACE, fg=TEXT_MUTED).pack(anchor="w")

        # Client 3 files block
        c_disp_frame = tk.Frame(preview_card, bg=CARD_SURFACE)
        c_disp_frame.pack(fill="x", pady=(6, 2))
        tk.Label(c_disp_frame, text="CLIENT SET (3):", font=("Segoe UI", 7, "bold"), bg=CARD_SURFACE, fg=ACCENT_BLUE).pack(anchor="w")
        self.lbl_client_out = tk.Label(c_disp_frame, text="...", font=("Consolas", 8),
                                       bg=CARD_SURFACE, fg=TEXT_HEAD, justify="left", anchor="w")
        self.lbl_client_out.pack(fill="x")

        # Project 3 files block
        p_disp_frame = tk.Frame(preview_card, bg=CARD_SURFACE)
        p_disp_frame.pack(fill="x", pady=(4, 2))
        tk.Label(p_disp_frame, text="PROJECT SET (3):", font=("Segoe UI", 7, "bold"), bg=CARD_SURFACE, fg=ACCENT_GREEN).pack(anchor="w")
        self.lbl_proj_out = tk.Label(p_disp_frame, text="...", font=("Consolas", 8),
                                     bg=CARD_SURFACE, fg=TEXT_HEAD, justify="left", anchor="w")
        self.lbl_proj_out.pack(fill="x")

        # -------------------------------------------------------------
        # RIGHT COLUMN: DRAG & DROP, 3 VISUAL FILE SLOTS & ACTIONS
        # -------------------------------------------------------------
        right_card = tk.Frame(workspace, bg=CARD_BG, relief="flat", padx=18, pady=16,
                              highlightbackground=CARD_BORDER, highlightthickness=1)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Large Modern Drop Zone
        self.drop_container = tk.Frame(right_card, bg=CARD_SURFACE, highlightbackground=CARD_BORDER, highlightthickness=1)
        self.drop_container.pack(fill="x", pady=(0, 10))

        self.drop_icon_lbl = tk.Label(self.drop_container, text="📂 ⬆️", font=("Segoe UI", 16),
                                      bg=CARD_SURFACE, fg=ACCENT_BLUE)
        self.drop_icon_lbl.pack(pady=(10, 0))

        self.drop_main_lbl = tk.Label(
            self.drop_container, text="DRAG & DROP DRAWING FOLDER OR FILES",
            font=("Segoe UI", 9, "bold"), bg=CARD_SURFACE, fg=TEXT_HEAD
        )
        self.drop_main_lbl.pack()

        self.drop_sub_lbl = tk.Label(
            self.drop_container, text="Auto-detects matching DWG, PDF and ZIP files + info.txt",
            font=("Segoe UI", 8), bg=CARD_SURFACE, fg=TEXT_MUTED
        )
        self.drop_sub_lbl.pack(pady=(1, 6))

        # Browse Folder button inside Drop area
        btn_browse_folder = tk.Button(
            self.drop_container, text="📁 Choose Folder...", font=("Segoe UI", 8, "bold"),
            bg=INPUT_BG, fg=TEXT_HEAD, relief="flat", padx=12, pady=4,
            command=self.browse_folder
        )
        btn_browse_folder.pack(pady=(0, 10))
        self.add_hover(btn_browse_folder, INPUT_BG, CARD_BORDER)

        # Connect drag-and-drop to all drop components
        for w in [self.drop_container, self.drop_icon_lbl, self.drop_main_lbl, self.drop_sub_lbl]:
            w.drop_target_register(DND_FILES)
            w.dnd_bind("<<Drop>>", self.handle_drop)

        # 3 DEDICATED VISUAL FILE STATUS SLOTS (PDF, CAD, ZIP)
        self.pdf_card = self.create_visual_slot(right_card, "PDF SHEET", "PDF", BADGE_PDF_BG, BADGE_PDF_FG, "pdf")
        self.dwg_card = self.create_visual_slot(right_card, "CAD DRAWING", "DWG", BADGE_CAD_BG, BADGE_CAD_FG, "dwg")
        self.zip_card = self.create_visual_slot(right_card, "ZIP ARCHIVE", "ZIP", BADGE_ZIP_BG, BADGE_ZIP_FG, "zip")

        # Mode Selector
        mode_frame = tk.Frame(right_card, bg=CARD_BG)
        mode_frame.pack(fill="x", pady=(8, 8))

        tk.Label(mode_frame, text="Packaging Mode:", font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(side="left")

        self.mode_var = tk.StringVar(value="CAD + PDF")
        self.mode_options = ["CAD + PDF", "ZIP + PDF", "All in One (CAD+PDF+ZIP)"]
        self.mode_menu = tk.OptionMenu(mode_frame, self.mode_var, *self.mode_options)
        self.mode_menu.config(bg=CARD_SURFACE, fg=TEXT_HEAD, relief="flat", highlightthickness=0, font=("Segoe UI", 8, "bold"))
        self.mode_menu["menu"].config(bg=CARD_SURFACE, fg=TEXT_HEAD, font=("Segoe UI", 8))
        self.mode_menu.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Grand Primary Action Button
        self.btn_generate = tk.Button(
            right_card, text="⚡  GENERATE ALL 6 PACKAGE FILES", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_GREEN, fg="white", relief="flat", pady=10, cursor="hand2",
            activebackground=ACCENT_GREEN_HOVER, activeforeground="white",
            command=self.run_packaging
        )
        self.btn_generate.pack(fill="x", pady=(2, 6))
        self.add_hover(self.btn_generate, ACCENT_GREEN, ACCENT_GREEN_HOVER)

        # Secondary Actions
        action_bar = tk.Frame(right_card, bg=CARD_BG)
        action_bar.pack(fill="x")

        btn_open = tk.Button(action_bar, text="📂 Open Output Folder", font=("Segoe UI", 8, "bold"),
                             bg=CARD_SURFACE, fg=TEXT_HEAD, relief="flat", pady=5,
                             command=self.open_output)
        btn_open.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.add_hover(btn_open, CARD_SURFACE, CARD_BORDER)

        btn_reset = tk.Button(action_bar, text="🔄 Reset All", font=("Segoe UI", 8, "bold"),
                              bg=CARD_SURFACE, fg=TEXT_HEAD, relief="flat", pady=5,
                              command=self.reset_all)
        btn_reset.pack(side="right", fill="x", expand=True, padx=(4, 0))
        self.add_hover(btn_reset, CARD_SURFACE, CARD_BORDER)

        # Status text
        self.status_lbl = tk.Label(right_card, text="Ready. Drop drawing folder or files.",
                                   font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=TEXT_MUTED)
        self.status_lbl.pack(anchor="w", pady=(8, 0))

        # ================= FOOTER BAR =================
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=24, pady=(2, 10))

        self.info_status_lbl = tk.Label(footer, text="No info.txt active", font=("Segoe UI", 8),
                                        bg=BG, fg=TEXT_MUTED)
        self.info_status_lbl.pack(side="left")

        tk.Label(footer, text="Press <Enter> to Generate | LUDARP", font=("Segoe UI", 8),
                 bg=BG, fg=TEXT_FAINT).pack(side="right")

    # ================= VISUAL SLOT HELPER =================

    def create_visual_slot(self, parent, title, badge_text, badge_bg, badge_fg, ftype):
        """Creates a modern visual status slot for PDF, CAD, or ZIP."""
        card = tk.Frame(parent, bg=CARD_SURFACE, relief="flat", padx=10, pady=6,
                        highlightbackground=CARD_BORDER, highlightthickness=1)
        card.pack(fill="x", pady=2)

        # Colored Badge
        badge = tk.Label(card, text=f" {badge_text} ", font=("Segoe UI", 7, "bold"),
                         bg=badge_bg, fg=badge_fg, padx=4, pady=1)
        badge.pack(side="left", padx=(0, 8))

        # File Title & Name
        name_frame = tk.Frame(card, bg=CARD_SURFACE)
        name_frame.pack(side="left", fill="x", expand=True)

        lbl_name = tk.Label(name_frame, text="— No file loaded —", font=("Segoe UI", 8),
                            bg=CARD_SURFACE, fg=TEXT_MUTED, anchor="w")
        lbl_name.pack(fill="x")

        # Browse action button
        btn_browse = tk.Button(card, text="Browse", font=("Segoe UI", 7, "bold"),
                               bg=INPUT_BG, fg=TEXT_HEAD, relief="flat", padx=8, pady=2,
                               command=lambda t=ftype: self.manual_browse_file(t))
        btn_browse.pack(side="right")
        self.add_hover(btn_browse, INPUT_BG, CARD_BORDER)

        return {"frame": card, "badge": badge, "label": lbl_name, "btn": btn_browse}

    def add_hover(self, widget, normal, hover):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal))

    def bind_input_glow(self, entry):
        entry.bind("<FocusIn>", lambda e: entry.config(highlightbackground=INPUT_FOCUS))
        entry.bind("<FocusOut>", lambda e: entry.config(highlightbackground=INPUT_BORDER))

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
        ext_map = {
            "zip": [("ZIP Archive", "*.zip")],
            "dwg": [("AutoCAD Drawing", "*.dwg")],
            "pdf": [("PDF Sheet", "*.pdf")]
        }
        path = filedialog.askopenfilename(filetypes=ext_map.get(ftype, [("All files", "*.*")]))
        if path:
            self.files[ftype] = os.path.normpath(path)
            if not self.current_folder:
                self.current_folder = os.path.dirname(path)
            self.update_file_cards()
            self.update_preview()

    def update_file_cards(self):
        """Updates the visual cards for ZIP, CAD, and PDF."""
        # 1. PDF
        if self.files["pdf"] and os.path.exists(self.files["pdf"]):
            sz = format_size(os.path.getsize(self.files["pdf"]))
            self.pdf_card["label"].config(text=f"{os.path.basename(self.files['pdf'])}  ({sz})", fg=TEXT_HEAD)
            self.pdf_card["frame"].config(highlightbackground=ACCENT_GREEN)
        else:
            self.pdf_card["label"].config(text="— Missing PDF —", fg=TEXT_MUTED)
            self.pdf_card["frame"].config(highlightbackground=CARD_BORDER)

        # 2. CAD / DWG
        if self.files["dwg"] and os.path.exists(self.files["dwg"]):
            sz = format_size(os.path.getsize(self.files["dwg"]))
            self.dwg_card["label"].config(text=f"{os.path.basename(self.files['dwg'])}  ({sz})", fg=TEXT_HEAD)
            self.dwg_card["frame"].config(highlightbackground=ACCENT_GREEN)
        else:
            self.dwg_card["label"].config(text="— Missing DWG —", fg=TEXT_MUTED)
            self.dwg_card["frame"].config(highlightbackground=CARD_BORDER)

        # 3. ZIP
        if self.files["zip"] and os.path.exists(self.files["zip"]):
            sz = format_size(os.path.getsize(self.files["zip"]))
            self.zip_card["label"].config(text=f"{os.path.basename(self.files['zip'])}  ({sz})", fg=TEXT_HEAD)
            self.zip_card["frame"].config(highlightbackground=ACCENT_GREEN)
        else:
            self.zip_card["label"].config(text="— None (optional) —", fg=TEXT_MUTED)
            self.zip_card["frame"].config(highlightbackground=CARD_BORDER)

        # Auto-adjust packaging mode based on ZIP presence
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
        self.lbl_client_out.config(text=f"• {c_base}.pdf\n• {c_base}.dwg\n• {c_base}.zip")
        self.lbl_proj_out.config(text=f"• {p_base}.pdf\n• {p_base}.dwg\n• {p_base}.zip")

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
                text=f"✓ Config loaded: {os.path.basename(txt_path)}",
                fg=ACCENT_GREEN
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
        self.status_lbl.config(text=f"Loaded: {', '.join(loaded) if loaded else 'None'}", fg=ACCENT_GREEN)

        # ⚡ ZERO-CLICK AUTO-PACK: if enabled and client + drawing are present
        if self.auto_pack_var.get() and self.client_var.get().strip() and self.files["pdf"]:
            self.root.update_idletasks()
            self.run_packaging()

    def generate_info_txt(self):
        """Generates an info.txt file with current Client and Project names."""
        client = self.client_var.get().strip()
        project = self.project_var.get().strip()

        if not client and not project:
            messagebox.showinfo("Enter Names", "Please enter at least a Client Name or Project Name before generating info.txt.")
            return

        target_dir = self.current_folder if (self.current_folder and os.path.exists(self.current_folder)) else ""
        if not target_dir:
            target_dir = filedialog.askdirectory(title="Select Folder to Save info.txt (e.g. 00share)")

        if target_dir and os.path.isdir(target_dir):
            txt_path = os.path.join(target_dir, "info.txt")
            content = f"Client: {client}\nProject: {project}\n"
            try:
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.current_folder = target_dir
                self.info_status_lbl.config(
                    text=f"✓ info.txt generated in: {os.path.basename(target_dir)}",
                    fg=ACCENT_GREEN
                )
                if messagebox.askyesno("info.txt Generated", f"Successfully created info.txt in:\n{txt_path}\n\nClient: {client or '(None)'}\nProject: {project or '(None)'}\n\nOpen this file in Notepad?"):
                    safe_open_folder(txt_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create info.txt:\n{e}")

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
        self.status_lbl.config(text="Reset complete.", fg=TEXT_MUTED)

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
        self.status_lbl.config(text="Packaging 6 files...", fg=ACCENT_BLUE)
        self.root.update_idletasks()

        try:
            # 1. CLIENT SET (3 files: pdf, dwg, zip)
            self.create_bundle(out_dir, c_base, self.files["pdf"], self.files["dwg"], self.files["zip"], mode, inner_label=client)

            # 2. PROJECT SET (3 files: pdf, dwg, zip)
            if p_base != c_base:
                self.create_bundle(out_dir, p_base, self.files["pdf"], self.files["dwg"], self.files["zip"], mode, inner_label=p_base)

            self.status_lbl.config(text="Done! Created all 6 files in output folder ✅", fg=ACCENT_GREEN)
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
