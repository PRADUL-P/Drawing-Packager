import os
import sys
import shutil
import zipfile
import json
import re
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkcalendar import DateEntry
import customtkinter as ctk

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

# ================= DESIGN SYSTEM: MODERN GLASSMORPHISM =================
APP_NAME = "LUDARP Drawing Packager"
APP_VERSION = "v2.0"

# Glassmorphism Color Tokens (Light Mode, Dark Mode)
CANVAS_BG = ("#eef2f6", "#090d16")          # Airy frosted canvas / deep space obsidian
GLASS_CARD = ("#ffffff", "#111827")         # Pure frosted glass card / dark slate glass
GLASS_BORDER = ("#cbd5e1", "#1e293b")       # Subtle anti-aliased glass border
GLASS_SURFACE = ("#f8fafc", "#172033")      # Elevated frosted container
SURFACE_BORDER = ("#e2e8f0", "#24334a")     # Inner border for nested items
INPUT_BG = ("#ffffff", "#0b101b")           # Text input background
INPUT_BORDER = ("#cbd5e1", "#223147")       # Input border

# Typography Tokens (Ultra High-Contrast, crystal clear)
TEXT_HEAD = ("#0f172a", "#f8fafc")          # Jet black / pure white
TEXT_BODY = ("#1e293b", "#e2e8f0")          # High-contrast slate body
TEXT_MUTED = ("#475569", "#94a3b8")         # High-readability secondary
TEXT_ACCENT = ("#0284c7", "#38bdf8")        # Cyan / sky electric blue

# Vibrant Badges & Action Accents
ACCENT_GREEN = ("#059669", "#10b981")       # Emerald primary action
ACCENT_GREEN_HOVER = ("#047857", "#059669")
ACCENT_BLUE = ("#2563eb", "#3b82f6")        # Royal electric blue
ACCENT_BLUE_HOVER = ("#1d4ed8", "#2563eb")
ACCENT_WARN = ("#d97706", "#f59e0b")        # Amber alert
ACCENT_CRIMSON = ("#dc2626", "#ef4444")     # Crimson

# Badge Colors
BADGE_PDF_BG = ("#fee2e2", "#3b171a")
BADGE_PDF_FG = ("#b91c1c", "#f87171")
BADGE_CAD_BG = ("#e0f2fe", "#0c283d")
BADGE_CAD_FG = ("#0369a1", "#38bdf8")
BADGE_ZIP_BG = ("#fef3c7", "#392a10")
BADGE_ZIP_FG = ("#b45309", "#fbbf24")

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ludarp_packager_config.json")


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
        "include_date": True,
        "auto_pack_on_drop": True,
        "theme": "Dark"
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

class DrawingPackagerApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

        self.config = load_config()
        self.current_theme = self.config.get("theme", "Dark")
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("980x640")
        self.minsize(920, 600)
        self.configure(fg_color=CANVAS_BG)

        icon_path = resource_path("zip-folder.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.files = {"zip": None, "pdf": None, "dwg": None}
        self.current_folder = ""

        self.build_ui()
        self.bind_events()
        self.update_preview()

    def build_ui(self):
        # Full-window drag & drop registration
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.handle_drop)

        # ================= TOP HEADER (Glassmorphic Navigation Bar) =================
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(16, 12))

        # Brand Title & Version Badge
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.pack(side="left")

        lbl_logo = ctk.CTkLabel(
            brand_frame, text="🧩", font=ctk.CTkFont(size=22)
        )
        lbl_logo.pack(side="left", padx=(0, 8))

        lbl_title = ctk.CTkLabel(
            brand_frame, text="LUDARP Drawing Packager",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TEXT_HEAD
        )
        lbl_title.pack(side="left")

        ver_badge = ctk.CTkLabel(
            brand_frame, text=f" {APP_VERSION} ",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=ACCENT_BLUE, text_color="#ffffff",
            corner_radius=6, padx=6, pady=2
        )
        ver_badge.pack(side="left", padx=10)

        # Right Navigation Controls: Theme Toggle, Auto-Pack, Generate info.txt
        ctrl_frame = ctk.CTkFrame(header, fg_color="transparent")
        ctrl_frame.pack(side="right")

        # 1. Dark / Light Mode Toggle (Segmented Button for seamless theme switching)
        self.theme_seg = ctk.CTkSegmentedButton(
            ctrl_frame, values=["🌙 Dark", "☀️ Light"],
            command=self.toggle_theme,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=GLASS_SURFACE,
            selected_color=ACCENT_BLUE,
            selected_hover_color=ACCENT_BLUE_HOVER,
            corner_radius=8
        )
        self.theme_seg.set("🌙 Dark" if self.current_theme == "Dark" else "☀️ Light")
        self.theme_seg.pack(side="left", padx=(0, 14))

        # 2. info.txt Quick Generator
        btn_top_txt = ctk.CTkButton(
            ctrl_frame, text="📄 Generate info.txt",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=GLASS_SURFACE, hover_color=SURFACE_BORDER,
            text_color=TEXT_HEAD, border_width=1, border_color=GLASS_BORDER,
            corner_radius=8, height=32,
            command=self.generate_info_txt
        )
        btn_top_txt.pack(side="left", padx=(0, 14))

        # 3. Auto-Pack on Drop Switch
        self.auto_pack_var = ctk.BooleanVar(value=self.config.get("auto_pack_on_drop", True))
        self.switch_autopack = ctk.CTkSwitch(
            ctrl_frame, text="⚡ Auto-Pack on Drop",
            variable=self.auto_pack_var,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_HEAD,
            progress_color=ACCENT_GREEN,
            command=self.save_preferences
        )
        self.switch_autopack.pack(side="left")

        # ================= TWO-COLUMN MASTER WORKSPACE =================
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        workspace.grid_columnconfigure(0, weight=1, minsize=430)
        workspace.grid_columnconfigure(1, weight=1, minsize=460)
        workspace.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT COLUMN: FROSTED GLASS DISPATCH & MANIFEST CARD
        # -------------------------------------------------------------
        left_card = ctk.CTkFrame(
            workspace, fg_color=GLASS_CARD,
            border_color=GLASS_BORDER, border_width=1.5,
            corner_radius=14
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Left Card Padding Frame
        left_inner = ctk.CTkFrame(left_card, fg_color="transparent")
        left_inner.pack(fill="both", expand=True, padx=20, pady=18)

        # Header Title
        lbl_disp_title = ctk.CTkLabel(
            left_inner, text="📋  DISPATCH DETAILS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_MUTED
        )
        lbl_disp_title.pack(anchor="w", pady=(0, 8))

        # Client Name Field
        lbl_c_title = ctk.CTkLabel(
            left_inner, text="CLIENT NAME (Used for Client Files)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_HEAD
        )
        lbl_c_title.pack(anchor="w", pady=(0, 4))

        c_box = ctk.CTkFrame(left_inner, fg_color="transparent")
        c_box.pack(fill="x", pady=(0, 12))

        self.client_var = ctk.StringVar(value=self.config.get("recent_clients", [""])[0] if self.config.get("recent_clients") else "")
        self.client_entry = ctk.CTkEntry(
            c_box, textvariable=self.client_var,
            placeholder_text="e.g. Acme Corp / MR. SMITH",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=INPUT_BG, border_color=INPUT_BORDER,
            text_color=TEXT_HEAD, placeholder_text_color=TEXT_MUTED,
            corner_radius=8, height=36
        )
        self.client_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.client_var.trace_add("write", lambda *args: self.update_preview())

        btn_c_paste = ctk.CTkButton(
            c_box, text="Paste", width=60, height=36,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=GLASS_SURFACE, hover_color=SURFACE_BORDER,
            text_color=TEXT_HEAD, border_width=1, border_color=GLASS_BORDER,
            corner_radius=8,
            command=lambda: self.paste_var(self.client_var)
        )
        btn_c_paste.pack(side="right")

        # Project Name Field
        lbl_p_title = ctk.CTkLabel(
            left_inner, text="PROJECT NAME (Used for Project Files)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_HEAD
        )
        lbl_p_title.pack(anchor="w", pady=(0, 4))

        p_box = ctk.CTkFrame(left_inner, fg_color="transparent")
        p_box.pack(fill="x", pady=(0, 12))

        self.project_var = ctk.StringVar(value=self.config.get("recent_projects", [""])[0] if self.config.get("recent_projects") else "")
        self.project_entry = ctk.CTkEntry(
            p_box, textvariable=self.project_var,
            placeholder_text="e.g. VILLA_402 / TOWER_A_REV01",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=INPUT_BG, border_color=INPUT_BORDER,
            text_color=TEXT_HEAD, placeholder_text_color=TEXT_MUTED,
            corner_radius=8, height=36
        )
        self.project_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.project_var.trace_add("write", lambda *args: self.update_preview())

        btn_p_paste = ctk.CTkButton(
            p_box, text="Paste", width=60, height=36,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=GLASS_SURFACE, hover_color=SURFACE_BORDER,
            text_color=TEXT_HEAD, border_width=1, border_color=GLASS_BORDER,
            corner_radius=8,
            command=lambda: self.paste_var(self.project_var)
        )
        btn_p_paste.pack(side="right")

        # Date Bar Option with Glass Frame
        date_bar = ctk.CTkFrame(
            left_inner, fg_color=GLASS_SURFACE,
            border_color=SURFACE_BORDER, border_width=1,
            corner_radius=10, height=44
        )
        date_bar.pack(fill="x", pady=(0, 12))

        self.include_date_var = ctk.BooleanVar(value=self.config.get("include_date", True))
        self.switch_date = ctk.CTkSwitch(
            date_bar, text="Include Date on Client Package",
            variable=self.include_date_var,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_HEAD,
            progress_color=ACCENT_BLUE,
            command=self.update_preview
        )
        self.switch_date.pack(side="left", padx=(12, 10), pady=8)

        # Date picker container
        self.date_picker = DateEntry(
            date_bar, date_pattern="dd-mm-yyyy",
            background="#2563eb", foreground="white", borderwidth=0,
            font=("Segoe UI", 9, "bold")
        )
        self.date_picker.pack(side="right", padx=(0, 12), pady=8)
        self.date_picker.bind("<<DateEntrySelected>>", lambda e: self.update_preview())

        # Save info.txt Button
        btn_gen_info = ctk.CTkButton(
            left_inner, text="💾 Save Current Names as info.txt",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=GLASS_SURFACE, hover_color=SURFACE_BORDER,
            text_color=ACCENT_BLUE, border_width=1, border_color=GLASS_BORDER,
            corner_radius=8, height=34,
            command=self.generate_info_txt
        )
        btn_gen_info.pack(fill="x", pady=(0, 14))

        # Target Output Manifest (Live 6 Files Visual Card)
        preview_card = ctk.CTkFrame(
            left_inner, fg_color=GLASS_SURFACE,
            border_color=SURFACE_BORDER, border_width=1,
            corner_radius=10
        )
        preview_card.pack(fill="both", expand=True)

        lbl_manifest_title = ctk.CTkLabel(
            preview_card, text="🎯 TARGET OUTPUT MANIFEST (6 FILES)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=TEXT_MUTED
        )
        lbl_manifest_title.pack(anchor="w", padx=14, pady=(10, 4))

        # Client 3 files block
        c_disp_frame = ctk.CTkFrame(preview_card, fg_color="transparent")
        c_disp_frame.pack(fill="x", padx=14, pady=(2, 6))

        lbl_c_tag = ctk.CTkLabel(
            c_disp_frame, text="CLIENT SET (3):",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=ACCENT_BLUE
        )
        lbl_c_tag.pack(anchor="w")

        self.lbl_client_out = ctk.CTkLabel(
            c_disp_frame, text="• ...\n• ...\n• ...",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_HEAD, justify="left", anchor="w"
        )
        self.lbl_client_out.pack(fill="x", pady=(1, 0))

        # Project 3 files block
        p_disp_frame = ctk.CTkFrame(preview_card, fg_color="transparent")
        p_disp_frame.pack(fill="x", padx=14, pady=(2, 10))

        lbl_p_tag = ctk.CTkLabel(
            p_disp_frame, text="PROJECT SET (3):",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=ACCENT_GREEN
        )
        lbl_p_tag.pack(anchor="w")

        self.lbl_proj_out = ctk.CTkLabel(
            p_disp_frame, text="• ...\n• ...\n• ...",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_HEAD, justify="left", anchor="w"
        )
        self.lbl_proj_out.pack(fill="x", pady=(1, 0))

        # -------------------------------------------------------------
        # RIGHT COLUMN: DROP ZONE, 3 FILE CARDS & ACTION HUB
        # -------------------------------------------------------------
        right_card = ctk.CTkFrame(
            workspace, fg_color=GLASS_CARD,
            border_color=GLASS_BORDER, border_width=1.5,
            corner_radius=14
        )
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        right_inner = ctk.CTkFrame(right_card, fg_color="transparent")
        right_inner.pack(fill="both", expand=True, padx=20, pady=18)

        # Large Modern Drop Zone Frame
        self.drop_container = ctk.CTkFrame(
            right_inner, fg_color=GLASS_SURFACE,
            border_color=ACCENT_BLUE, border_width=1.5,
            corner_radius=12
        )
        self.drop_container.pack(fill="x", pady=(0, 10))

        self.drop_icon_lbl = ctk.CTkLabel(
            self.drop_container, text="📂 ⬆️",
            font=ctk.CTkFont(size=20)
        )
        self.drop_icon_lbl.pack(pady=(10, 2))

        self.drop_main_lbl = ctk.CTkLabel(
            self.drop_container, text="DRAG & DROP DRAWING FOLDER OR FILES",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_HEAD
        )
        self.drop_main_lbl.pack()

        self.drop_sub_lbl = ctk.CTkLabel(
            self.drop_container, text="Auto-detects matching DWG, PDF and ZIP files + info.txt",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=TEXT_MUTED
        )
        self.drop_sub_lbl.pack(pady=(1, 8))

        btn_browse_folder = ctk.CTkButton(
            self.drop_container, text="📁 Choose Folder...",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=INPUT_BG, hover_color=SURFACE_BORDER,
            text_color=TEXT_HEAD, border_width=1, border_color=GLASS_BORDER,
            corner_radius=8, height=30,
            command=self.browse_folder
        )
        btn_browse_folder.pack(pady=(0, 10))

        # Register drag-and-drop to drop components
        for w in [self.drop_container, self.drop_icon_lbl, self.drop_main_lbl, self.drop_sub_lbl]:
            w.drop_target_register(DND_FILES)
            w.dnd_bind("<<Drop>>", self.handle_drop)

        # 3 DEDICATED VISUAL FILE STATUS SLOTS (PDF, CAD, ZIP)
        self.pdf_card = self.create_visual_slot(right_inner, "PDF SHEET", "PDF", BADGE_PDF_BG, BADGE_PDF_FG, "pdf")
        self.dwg_card = self.create_visual_slot(right_inner, "CAD DRAWING", "DWG", BADGE_CAD_BG, BADGE_CAD_FG, "dwg")
        self.zip_card = self.create_visual_slot(right_inner, "ZIP ARCHIVE", "ZIP", BADGE_ZIP_BG, BADGE_ZIP_FG, "zip")

        # Packaging Mode Selector
        mode_frame = ctk.CTkFrame(right_inner, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(8, 8))

        lbl_mode = ctk.CTkLabel(
            mode_frame, text="Packaging Mode:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_MUTED
        )
        lbl_mode.pack(side="left")

        self.mode_var = ctk.StringVar(value="CAD + PDF")
        self.mode_options = ["CAD + PDF", "ZIP + PDF", "All in One (CAD+PDF+ZIP)"]
        self.mode_menu = ctk.CTkOptionMenu(
            mode_frame, variable=self.mode_var, values=self.mode_options,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=GLASS_SURFACE, text_color=TEXT_HEAD,
            button_color=SURFACE_BORDER, button_hover_color=GLASS_BORDER,
            dropdown_fg_color=GLASS_SURFACE, dropdown_text_color=TEXT_HEAD,
            dropdown_hover_color=SURFACE_BORDER,
            corner_radius=8, height=32
        )
        self.mode_menu.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Grand Primary Action Button
        self.btn_generate = ctk.CTkButton(
            right_inner, text="⚡  GENERATE ALL 6 PACKAGE FILES",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_HOVER,
            text_color="#ffffff", corner_radius=10, height=44,
            command=self.run_packaging
        )
        self.btn_generate.pack(fill="x", pady=(4, 8))

        # Secondary Actions
        action_bar = ctk.CTkFrame(right_inner, fg_color="transparent")
        action_bar.pack(fill="x")

        btn_open = ctk.CTkButton(
            action_bar, text="📂 Open Output Folder",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=GLASS_SURFACE, hover_color=SURFACE_BORDER,
            text_color=TEXT_HEAD, border_width=1, border_color=GLASS_BORDER,
            corner_radius=8, height=34,
            command=self.open_output
        )
        btn_open.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_reset = ctk.CTkButton(
            action_bar, text="🔄 Reset All",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=GLASS_SURFACE, hover_color=SURFACE_BORDER,
            text_color=TEXT_HEAD, border_width=1, border_color=GLASS_BORDER,
            corner_radius=8, height=34,
            command=self.reset_all
        )
        btn_reset.pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Status text
        self.status_lbl = ctk.CTkLabel(
            right_inner, text="Ready. Drop drawing folder or files.",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_MUTED
        )
        self.status_lbl.pack(anchor="w", pady=(8, 0))

        # ================= FOOTER BAR =================
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(0, 10))

        self.info_status_lbl = ctk.CTkLabel(
            footer, text="No info.txt active",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=TEXT_MUTED
        )
        self.info_status_lbl.pack(side="left")

        lbl_hint = ctk.CTkLabel(
            footer, text="Press <Enter> to Generate | LUDARP",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=TEXT_MUTED
        )
        lbl_hint.pack(side="right")

    # ================= VISUAL SLOT HELPER =================

    def create_visual_slot(self, parent, title, badge_text, badge_bg, badge_fg, ftype):
        """Creates a modern visual status slot for PDF, CAD, or ZIP."""
        card = ctk.CTkFrame(
            parent, fg_color=GLASS_SURFACE,
            border_color=SURFACE_BORDER, border_width=1,
            corner_radius=10, height=38
        )
        card.pack(fill="x", pady=2)

        # Colored Badge
        badge = ctk.CTkLabel(
            card, text=f" {badge_text} ",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            fg_color=badge_bg, text_color=badge_fg,
            corner_radius=6, padx=6, pady=2
        )
        badge.pack(side="left", padx=(10, 8), pady=5)

        # File Title & Name
        lbl_name = ctk.CTkLabel(
            card, text="— No file loaded —",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED, anchor="w"
        )
        lbl_name.pack(side="left", fill="x", expand=True, pady=5)

        # Browse action button
        btn_browse = ctk.CTkButton(
            card, text="Browse", width=55, height=26,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=INPUT_BG, hover_color=SURFACE_BORDER,
            text_color=TEXT_HEAD, border_width=1, border_color=GLASS_BORDER,
            corner_radius=6,
            command=lambda t=ftype: self.manual_browse_file(t)
        )
        btn_browse.pack(side="right", padx=(6, 8), pady=5)

        return {"frame": card, "badge": badge, "label": lbl_name, "btn": btn_browse}

    def bind_events(self):
        self.include_date_var.trace_add("write", lambda *args: self.update_preview())
        self.bind("<Return>", lambda e: self.run_packaging())

    def toggle_theme(self, selected_value):
        """Toggles between Dark and Light mode dynamically."""
        if "Dark" in selected_value:
            new_theme = "Dark"
        else:
            new_theme = "Light"

        self.current_theme = new_theme
        ctk.set_appearance_mode(new_theme)

        # Style the embedded DateEntry to match theme
        if new_theme == "Dark":
            self.date_picker.configure(background="#2563eb", foreground="white")
        else:
            self.date_picker.configure(background="#2563eb", foreground="white")

        self.save_preferences()

    def save_preferences(self):
        conf = load_config()
        conf["auto_pack_on_drop"] = self.auto_pack_var.get()
        conf["include_date"] = self.include_date_var.get()
        conf["theme"] = self.current_theme
        save_config(conf)

    def paste_var(self, str_var):
        try:
            val = self.clipboard_get()
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
            self.pdf_card["label"].configure(text=f"{os.path.basename(self.files['pdf'])}  ({sz})", text_color=TEXT_HEAD)
            self.pdf_card["frame"].configure(border_color=ACCENT_GREEN)
        else:
            self.pdf_card["label"].configure(text="— Missing PDF —", text_color=TEXT_MUTED)
            self.pdf_card["frame"].configure(border_color=SURFACE_BORDER)

        # 2. CAD / DWG
        if self.files["dwg"] and os.path.exists(self.files["dwg"]):
            sz = format_size(os.path.getsize(self.files["dwg"]))
            self.dwg_card["label"].configure(text=f"{os.path.basename(self.files['dwg'])}  ({sz})", text_color=TEXT_HEAD)
            self.dwg_card["frame"].configure(border_color=ACCENT_GREEN)
        else:
            self.dwg_card["label"].configure(text="— Missing DWG —", text_color=TEXT_MUTED)
            self.dwg_card["frame"].configure(border_color=SURFACE_BORDER)

        # 3. ZIP
        if self.files["zip"] and os.path.exists(self.files["zip"]):
            sz = format_size(os.path.getsize(self.files["zip"]))
            self.zip_card["label"].configure(text=f"{os.path.basename(self.files['zip'])}  ({sz})", text_color=TEXT_HEAD)
            self.zip_card["frame"].configure(border_color=ACCENT_GREEN)
        else:
            self.zip_card["label"].configure(text="— None (optional) —", text_color=TEXT_MUTED)
            self.zip_card["frame"].configure(border_color=SURFACE_BORDER)

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
        self.lbl_client_out.configure(text=f"• {c_base}.pdf\n• {c_base}.dwg\n• {c_base}.zip")
        self.lbl_proj_out.configure(text=f"• {p_base}.pdf\n• {p_base}.dwg\n• {p_base}.zip")

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
            self.info_status_lbl.configure(
                text=f"✓ Config loaded: {os.path.basename(txt_path)}",
                text_color=ACCENT_GREEN
            )
        else:
            self.info_status_lbl.configure(
                text="No info.txt detected (using manual entries)",
                text_color=TEXT_MUTED
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
        self.status_lbl.configure(text=f"Loaded: {', '.join(loaded) if loaded else 'None'}", text_color=ACCENT_GREEN)

        # ⚡ ZERO-CLICK AUTO-PACK: if enabled and client + drawing are present
        if self.auto_pack_var.get() and self.client_var.get().strip() and self.files["pdf"]:
            self.update_idletasks()
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
                self.info_status_lbl.configure(
                    text=f"✓ info.txt generated in: {os.path.basename(target_dir)}",
                    text_color=ACCENT_GREEN
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
        self.status_lbl.configure(text="Reset complete.", text_color=TEXT_MUTED)

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

        self.btn_generate.configure(state="disabled")
        self.status_lbl.configure(text="Packaging 6 files...", text_color=ACCENT_BLUE)
        self.update_idletasks()

        try:
            # 1. CLIENT SET (3 files: pdf, dwg, zip)
            self.create_bundle(out_dir, c_base, self.files["pdf"], self.files["dwg"], self.files["zip"], mode, inner_label=client)

            # 2. PROJECT SET (3 files: pdf, dwg, zip)
            if p_base != c_base:
                self.create_bundle(out_dir, p_base, self.files["pdf"], self.files["dwg"], self.files["zip"], mode, inner_label=p_base)

            self.status_lbl.configure(text="Done! Created all 6 files in output folder ✅", text_color=ACCENT_GREEN)
            safe_open_folder(out_dir)

        except Exception as err:
            messagebox.showerror("Error", f"Failed to package files:\n{str(err)}")
            self.status_lbl.configure(text=f"Error: {err}", text_color=ACCENT_WARN)
        finally:
            self.btn_generate.configure(state="normal")

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
    app = DrawingPackagerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
