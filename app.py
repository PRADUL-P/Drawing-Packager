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

BG = "#0b1220"          # Darkest background
CARD = "#111827"        # Dark card container
CARD_INNER = "#1e293b"  # Inner section card
INPUT_BG = "#1f2937"    # Input fields
TEXT_PRIMARY = "#f9fafb"# High contrast primary text
TEXT_MUTED = "#9ca3af"  # Subtitle/labels
ACCENT = "#3b82f6"      # Primary action blue
ACCENT_HOVER = "#2563eb"
ACCENT_GREEN = "#10b981"# Success status green
ACCENT_WARN = "#f59e0b" # Warning amber
BTN_DARK = "#374151"
BTN_HOVER = "#4b5563"
BORDER_COLOR = "#374151"

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ludarp_packager_config.json")

# ================= UTILITIES =================

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller onefile."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def load_config():
    """Load recent history and preferences from user config."""
    default_config = {
        "recent_clients": [],
        "recent_projects": [],
        "recent_revisions": ["R00", "R01", "R02", "REV-A", "REV-B", "P01", "C01"],
        "naming_pattern": "Client_Project_Rev_Date",
        "separator": "_",
        "date_format": "%d-%m-%Y",
        "include_date": True,
        "include_rev": True,
        "auto_pack_on_drop": True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_config.update(data)
        except Exception:
            pass
    return default_config


def save_config(config_data):
    """Save preferences and recent values."""
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
    """Strip illegal characters for Windows filenames."""
    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        name = name.replace(ch, '')
    return name.strip()


def format_size(bytes_size):
    """Human readable file size."""
    if not bytes_size:
        return "0 B"
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def safe_open_folder(path):
    """Open folder in Windows File Explorer safely."""
    if path and os.path.exists(path):
        os.startfile(path)


# ================= DRAWING SCANNER & TEXT CONFIG PARSER =================

class MetadataParser:
    """Parses client/project format from txt file (e.g. info.txt, client.txt, or lines)."""

    @staticmethod
    def parse_txt_content(content):
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
        meta = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
            elif "=" in line:
                k, v = line.split("=", 1)
                meta[k.strip().lower()] = v.strip()

        # Positional fallback if no key:value found
        if "client" not in meta and "client_name" not in meta and len(lines) >= 1:
            meta["client"] = lines[0]
        if "project" not in meta and "project_name" not in meta and len(lines) >= 2:
            meta["project"] = lines[1]
        if "rev" not in meta and "revision" not in meta and len(lines) >= 3:
            meta["rev"] = lines[2]

        # Standardize keys
        client = meta.get("client") or meta.get("client_name") or meta.get("client name") or ""
        project = meta.get("project") or meta.get("project_name") or meta.get("project name") or ""
        rev = meta.get("rev") or meta.get("revision") or ""
        pattern = meta.get("pattern") or meta.get("format") or ""
        sep = meta.get("separator") or meta.get("sep") or ""

        return {
            "client": client,
            "project": project,
            "rev": rev,
            "pattern": pattern,
            "sep": sep
        }

    @staticmethod
    def find_and_parse(target_path):
        """Scans folder or dropped files for a .txt config file."""
        folder = None
        txt_candidates = []

        if isinstance(target_path, list):
            for p in target_path:
                if p.lower().endswith(".txt") and os.path.isfile(p):
                    txt_candidates.append(p)
                elif os.path.isfile(p):
                    folder = os.path.dirname(p)
                elif os.path.isdir(p):
                    folder = p
        elif os.path.isdir(target_path):
            folder = target_path
        elif os.path.isfile(target_path):
            folder = os.path.dirname(target_path)

        if folder and os.path.isdir(folder):
            for fname in os.listdir(folder):
                if fname.lower().endswith(".txt"):
                    txt_candidates.append(os.path.join(folder, fname))

        # Prioritize preferred names
        preferred = ["info.txt", "client.txt", "project.txt", "naming.txt", "format.txt", "00share.txt", "config.txt"]
        chosen = None
        for pref in preferred:
            for c in txt_candidates:
                if os.path.basename(c).lower() == pref:
                    chosen = c
                    break
            if chosen:
                break

        if not chosen and txt_candidates:
            chosen = txt_candidates[0]

        if chosen and os.path.exists(chosen):
            try:
                with open(chosen, "r", encoding="utf-8") as f:
                    content = f.read()
                return MetadataParser.parse_txt_content(content), chosen
            except Exception:
                pass

        return {}, None


class DrawingScanner:
    """Detects, matches and pairs CAD (.dwg), PDF (.pdf), and archive (.zip) files."""

    @staticmethod
    def scan_path(target_path):
        files = []
        if isinstance(target_path, list):
            files = [p for p in target_path if os.path.isfile(p)]
        elif os.path.isdir(target_path):
            files = [os.path.join(target_path, f) for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]

        zips, pdfs, dwgs = {}, {}, {}
        all_zips = []

        for p in files:
            fname = os.path.basename(p)
            base, ext = os.path.splitext(fname)
            ext = ext.lower()
            norm_key = base.strip().lower()

            if ext == ".zip":
                zips[norm_key] = p
                all_zips.append(p)
            elif ext == ".pdf":
                pdfs[norm_key] = p
            elif ext == ".dwg":
                dwgs[norm_key] = p

        all_keys = sorted(list(set(list(pdfs.keys()) + list(dwgs.keys()))))
        pairs = []

        # If only 1 pdf and 1 dwg with different names, pair them together
        if len(pdfs) == 1 and len(dwgs) == 1 and len(all_keys) > 1:
            p_file = list(pdfs.values())[0]
            d_file = list(dwgs.values())[0]
            base_label = os.path.splitext(os.path.basename(p_file))[0]
            pairs.append({
                "base": base_label,
                "pdf": p_file,
                "dwg": d_file,
                "zip": all_zips[0] if all_zips else None,
                "status": "Matched Pair"
            })
            return pairs, all_zips

        for k in all_keys:
            pdf_path = pdfs.get(k)
            dwg_path = dwgs.get(k)
            zip_path = zips.get(k) or (all_zips[0] if len(all_zips) == 1 else None)

            base_name = os.path.splitext(os.path.basename(pdf_path or dwg_path))[0]
            status = "Complete" if (pdf_path and dwg_path) else ("PDF Only" if pdf_path else "DWG Only")

            pairs.append({
                "base": base_name,
                "pdf": pdf_path,
                "dwg": dwg_path,
                "zip": zip_path,
                "status": status
            })

        return pairs, all_zips


# ================= GUI APPLICATION =================

class DrawingPackagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("980x670")
        self.root.minsize(860, 580)
        self.root.configure(bg=BG)

        # PyInstaller asset icon
        icon_path = resource_path("zip-folder.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.config = load_config()
        self.detected_pairs = []
        self.detected_zips = []
        self.current_txt_file = None

        self.setup_styles()
        self.build_ui()
        self.bind_events()
        self.update_live_preview()

        # Fade in effect
        self.root.attributes("-alpha", 0)
        self.fade_in(0)

    def fade_in(self, alpha=0):
        alpha += 0.08
        if alpha <= 1.0:
            self.root.attributes("-alpha", alpha)
            self.root.after(16, self.fade_in, alpha)
        else:
            self.root.attributes("-alpha", 1.0)

    def setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.style.configure(
            "Packager.Horizontal.TProgressbar",
            troughcolor=INPUT_BG,
            background=ACCENT,
            bordercolor=BG,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            thickness=6
        )

        self.style.configure(
            "Dark.TCombobox",
            fieldbackground=INPUT_BG,
            background=BTN_DARK,
            foreground=TEXT_PRIMARY,
            darkcolor=INPUT_BG,
            lightcolor=INPUT_BG,
            arrowcolor=TEXT_PRIMARY,
            bordercolor=BORDER_COLOR
        )
        self.style.map("Dark.TCombobox", fieldbackground=[("readonly", INPUT_BG)])

    def build_ui(self):
        # Register entire window as a drag & drop target!
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.handle_drop)

        # Top Bar: Auto-Pack Toggle & Quick Info
        top_bar = tk.Frame(self.root, bg=CARD_INNER, padx=12, pady=6)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 4))

        self.auto_pack_var = tk.BooleanVar(value=self.config.get("auto_pack_on_drop", True))
        chk_autopack = tk.Checkbutton(
            top_bar,
            text="⚡ Auto-Pack on Drop (Auto-reads info.txt & creates all 6 files immediately)",
            variable=self.auto_pack_var,
            font=("Segoe UI", 9, "bold"),
            bg=CARD_INNER, fg=ACCENT_GREEN, selectcolor=INPUT_BG,
            activebackground=CARD_INNER,
            command=self.save_autopack_pref
        )
        chk_autopack.pack(side="left")

        btn_new_txt = tk.Button(
            top_bar, text="📄 Create info.txt in Folder", font=("Segoe UI", 8),
            bg=BTN_DARK, fg="white", relief="flat", padx=8, pady=2,
            command=self.create_info_txt_dialog
        )
        btn_new_txt.pack(side="right")
        self.add_hover_effect(btn_new_txt, BTN_DARK, BTN_HOVER)

        # Main Layout: 2 Columns
        self.root.grid_columnconfigure(0, weight=1, minsize=420)
        self.root.grid_columnconfigure(1, weight=1, minsize=460)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)

        # ================= LEFT PANEL: METADATA & NAMING =================
        left_panel = tk.Frame(self.root, bg=CARD, relief="flat", padx=14, pady=12)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(4, 6))

        title_box = tk.Frame(left_panel, bg=CARD)
        title_box.pack(fill="x", pady=(0, 6))

        tk.Label(title_box, text="🧩 LUDARP Drawing Packager", font=("Segoe UI", 13, "bold"),
                 bg=CARD, fg=TEXT_PRIMARY).pack(side="left")
        ver_lbl = tk.Label(title_box, text=f" {APP_VERSION} ", font=("Segoe UI", 9, "bold"),
                           bg=ACCENT, fg="white", padx=4, pady=1)
        ver_lbl.pack(side="left", padx=8)

        self.txt_status_lbl = tk.Label(left_panel, text="Drop a folder with info.txt or drawings to auto-fill",
                                       font=("Segoe UI", 8, "italic"), bg=CARD, fg=TEXT_MUTED)
        self.txt_status_lbl.pack(anchor="w", pady=(0, 8))

        # Client Name Section
        self.create_field_label(left_panel, "Client Name", required=True)
        client_box = tk.Frame(left_panel, bg=CARD)
        client_box.pack(fill="x", pady=(2, 6))

        self.client_var = tk.StringVar(value=self.config.get("recent_clients", [""])[0] if self.config.get("recent_clients") else "")
        recent_clients = self.config.get("recent_clients", [])
        self.client_combo = ttk.Combobox(client_box, textvariable=self.client_var,
                                         values=recent_clients, style="Dark.TCombobox")
        self.client_combo.pack(side="left", fill="x", expand=True, ipady=4)
        self.client_var.trace_add("write", lambda *args: self.update_live_preview())

        btn_paste_client = self.create_button(client_box, "📋 Paste",
                                              lambda: self.paste_to_var(self.client_var), width=7)
        btn_paste_client.pack(side="right", padx=(6, 0))

        # Project Name Section
        self.create_field_label(left_panel, "Project Name", hint="(optional - defaults to drawing name)")
        project_box = tk.Frame(left_panel, bg=CARD)
        project_box.pack(fill="x", pady=(2, 6))

        self.project_var = tk.StringVar(value=self.config.get("recent_projects", [""])[0] if self.config.get("recent_projects") else "")
        recent_projects = self.config.get("recent_projects", [])
        self.project_combo = ttk.Combobox(project_box, textvariable=self.project_var,
                                          values=recent_projects, style="Dark.TCombobox")
        self.project_combo.pack(side="left", fill="x", expand=True, ipady=4)
        self.project_var.trace_add("write", lambda *args: self.update_live_preview())

        btn_paste_proj = self.create_button(project_box, "📋 Paste",
                                            lambda: self.paste_to_var(self.project_var), width=7)
        btn_paste_proj.pack(side="right", padx=(6, 0))

        # Revision Tag Section
        rev_header = tk.Frame(left_panel, bg=CARD)
        rev_header.pack(fill="x", pady=(4, 2))
        tk.Label(rev_header, text="Revision", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=TEXT_MUTED).pack(side="left")

        self.include_rev_var = tk.BooleanVar(value=self.config.get("include_rev", True))
        chk_rev = tk.Checkbutton(rev_header, text="Include Revision", variable=self.include_rev_var,
                                 bg=CARD, fg=TEXT_PRIMARY, selectcolor=INPUT_BG,
                                 activebackground=CARD, command=self.update_live_preview)
        chk_rev.pack(side="right")

        rev_box = tk.Frame(left_panel, bg=CARD)
        rev_box.pack(fill="x", pady=(2, 4))

        self.rev_var = tk.StringVar(value="R01")
        self.rev_combo = ttk.Combobox(rev_box, textvariable=self.rev_var,
                                      values=self.config.get("recent_revisions", []),
                                      style="Dark.TCombobox", width=12)
        self.rev_combo.pack(side="left", ipady=4)
        self.rev_var.trace_add("write", lambda *args: self.update_live_preview())

        preset_frame = tk.Frame(rev_box, bg=CARD)
        preset_frame.pack(side="left", padx=8)
        for preset in ["R00", "R01", "REV-A", "P1", "C1"]:
            btn = tk.Button(preset_frame, text=preset, font=("Segoe UI", 8),
                            bg=CARD_INNER, fg=TEXT_PRIMARY, relief="flat", padx=4, pady=1,
                            command=lambda p=preset: self.set_revision(p))
            btn.pack(side="left", padx=2)
            self.add_hover_effect(btn, CARD_INNER, BTN_HOVER)

        # Date Section
        date_header = tk.Frame(left_panel, bg=CARD)
        date_header.pack(fill="x", pady=(4, 2))
        tk.Label(date_header, text="Date", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=TEXT_MUTED).pack(side="left")

        self.include_date_var = tk.BooleanVar(value=self.config.get("include_date", True))
        chk_date = tk.Checkbutton(date_header, text="Include Date", variable=self.include_date_var,
                                  bg=CARD, fg=TEXT_PRIMARY, selectcolor=INPUT_BG,
                                  activebackground=CARD, command=self.update_live_preview)
        chk_date.pack(side="right")

        date_box = tk.Frame(left_panel, bg=CARD)
        date_box.pack(fill="x", pady=(2, 6))

        self.date_picker = DateEntry(date_box, date_pattern="dd-mm-yyyy",
                                     background=ACCENT, foreground="white", borderwidth=0)
        self.date_picker.pack(side="left", fill="x", expand=True)
        self.date_picker.bind("<<DateEntrySelected>>", lambda e: self.update_live_preview())

        # Naming Pattern
        self.create_field_label(left_panel, "Naming Template")
        pattern_box = tk.Frame(left_panel, bg=CARD)
        pattern_box.pack(fill="x", pady=(2, 4))

        self.pattern_var = tk.StringVar(value=self.config.get("naming_pattern", "Client_Project_Rev_Date"))
        pattern_options = [
            ("Client_Project_Rev_Date", "Client + Project + Rev + Date"),
            ("Client_Rev_Date", "Client + Rev + Date"),
            ("Client_Project", "Client + Project"),
            ("Project_Client_Rev_Date", "Project + Client + Rev + Date")
        ]
        self.pattern_menu = tk.OptionMenu(pattern_box, self.pattern_var,
                                          *[p[0] for p in pattern_options],
                                          command=lambda _: self.update_live_preview())
        self.pattern_menu.config(bg=INPUT_BG, fg=TEXT_PRIMARY, relief="flat", highlightthickness=0)
        self.pattern_menu["menu"].config(bg=INPUT_BG, fg=TEXT_PRIMARY)
        self.pattern_menu.pack(side="left", fill="x", expand=True)

        sep_box = tk.Frame(pattern_box, bg=CARD)
        sep_box.pack(side="right", padx=(8, 0))
        tk.Label(sep_box, text="Sep:", bg=CARD, fg=TEXT_MUTED, font=("Segoe UI", 8)).pack(side="left")
        self.sep_var = tk.StringVar(value=self.config.get("separator", "_"))
        for s in ["_", "-", " "]:
            rb = tk.Radiobutton(sep_box, text=repr(s)[1:-1] if s != " " else "spc",
                                variable=self.sep_var, value=s,
                                bg=CARD, fg=TEXT_PRIMARY, selectcolor=INPUT_BG,
                                activebackground=CARD, font=("Segoe UI", 8),
                                command=self.update_live_preview)
            rb.pack(side="left", padx=1)

        # Live Filename Preview Card
        preview_card = tk.Frame(left_panel, bg=CARD_INNER, relief="flat", padx=10, pady=8)
        preview_card.pack(fill="x", pady=(8, 0))

        tk.Label(preview_card, text="📄 Target 6-File Outputs Preview:", font=("Segoe UI", 8, "bold"),
                 bg=CARD_INNER, fg=ACCENT).pack(anchor="w")

        self.preview_lbl = tk.Label(preview_card, text="...", font=("Segoe UI", 8),
                                    bg=CARD_INNER, fg=TEXT_PRIMARY, justify="left")
        self.preview_lbl.pack(anchor="w", pady=(2, 4))

        btn_copy_name = tk.Button(preview_card, text="📋 Copy Base Name", font=("Segoe UI", 8),
                                  bg=BTN_DARK, fg="white", relief="flat", padx=6, pady=2,
                                  command=self.copy_preview_name)
        btn_copy_name.pack(anchor="e")
        self.add_hover_effect(btn_copy_name, BTN_DARK, BTN_HOVER)

        # ================= RIGHT PANEL: FILES & BATCH PACKAGING =================
        right_panel = tk.Frame(self.root, bg=CARD, relief="flat", padx=14, pady=12)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(4, 6))

        # Folder Paths
        self.create_field_label(right_panel, "Input / Output Folders")
        in_frame = tk.Frame(right_panel, bg=CARD)
        in_frame.pack(fill="x", pady=(2, 4))

        self.input_var = tk.StringVar()
        tk.Entry(in_frame, textvariable=self.input_var, bg=INPUT_BG, fg=TEXT_PRIMARY,
                 relief="flat").pack(side="left", fill="x", expand=True, ipady=3)
        btn_browse_in = self.create_button(in_frame, "Input", self.browse_input, width=6)
        btn_browse_in.pack(side="right", padx=(4, 0))

        out_frame = tk.Frame(right_panel, bg=CARD)
        out_frame.pack(fill="x", pady=(2, 6))

        self.output_var = tk.StringVar()
        tk.Entry(out_frame, textvariable=self.output_var, bg=INPUT_BG, fg=TEXT_PRIMARY,
                 relief="flat").pack(side="left", fill="x", expand=True, ipady=3)
        btn_browse_out = self.create_button(out_frame, "Output", self.browse_output, width=6)
        btn_browse_out.pack(side="right", padx=(4, 0))

        # Big Drag & Drop Zone
        self.drop_area = tk.Label(
            right_panel,
            text="⬇️ DRAG & DROP FOLDER OR DRAWINGS ANYWHERE\nReads info.txt & creates all 6 files automatically",
            font=("Segoe UI", 9, "bold"), bg=INPUT_BG, fg=ACCENT,
            relief="groove", bd=1, pady=12
        )
        self.drop_area.pack(fill="x", pady=(4, 6))
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.handle_drop)

        # Mode Selector
        mode_frame = tk.Frame(right_panel, bg=CARD)
        mode_frame.pack(fill="x", pady=(2, 4))

        tk.Label(mode_frame, text="Packaging Mode:", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=TEXT_MUTED).pack(side="left")

        self.mode_var = tk.StringVar(value="CAD + PDF")
        self.mode_options = ["CAD + PDF", "ZIP + PDF", "All in One (CAD+PDF+ZIP)"]
        self.mode_menu = tk.OptionMenu(mode_frame, self.mode_var, *self.mode_options)
        self.mode_menu.config(bg=INPUT_BG, fg=TEXT_PRIMARY, relief="flat", highlightthickness=0)
        self.mode_menu["menu"].config(bg=INPUT_BG, fg=TEXT_PRIMARY)
        self.mode_menu.pack(side="right", fill="x", expand=True, padx=(8, 0))

        # Detected Drawings Header
        list_header = tk.Frame(right_panel, bg=CARD)
        list_header.pack(fill="x", pady=(4, 2))

        self.detected_summary_lbl = tk.Label(list_header, text="Detected Drawings: 0 pairs",
                                            font=("Segoe UI", 9, "bold"), bg=CARD, fg=TEXT_PRIMARY)
        self.detected_summary_lbl.pack(side="left")

        self.batch_chk_var = tk.BooleanVar(value=True)
        self.chk_batch = tk.Checkbutton(list_header, text="Batch Process All",
                                        variable=self.batch_chk_var,
                                        bg=CARD, fg=TEXT_PRIMARY, selectcolor=INPUT_BG,
                                        activebackground=CARD)
        self.chk_batch.pack(side="right")

        # Treeview / Listbox for detected drawings
        list_container = tk.Frame(right_panel, bg=CARD_INNER, relief="flat")
        list_container.pack(fill="both", expand=True, pady=(2, 6))

        scroll = tk.Scrollbar(list_container, orient="vertical")
        self.pairs_listbox = tk.Listbox(list_container, bg=CARD_INNER, fg=TEXT_PRIMARY,
                                        selectbackground=ACCENT, selectforeground="white",
                                        relief="flat", highlightthickness=0,
                                        yscrollcommand=scroll.set, font=("Consolas", 9))
        scroll.config(command=self.pairs_listbox.yview)
        scroll.pack(side="right", fill="y")
        self.pairs_listbox.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        self.pairs_listbox.bind("<<ListboxSelect>>", self.on_pair_selected)

        # Progress bar
        self.progress_bar = ttk.Progressbar(right_panel, style="Packager.Horizontal.TProgressbar",
                                            mode="determinate")
        self.progress_bar.pack(fill="x", pady=(2, 2))

        # Status text
        self.status_lbl = tk.Label(right_panel, text="Ready. Drag & drop files or folder.",
                                   font=("Segoe UI", 8), bg=CARD, fg=TEXT_MUTED)
        self.status_lbl.pack(anchor="w", pady=(0, 4))

        # Action Buttons
        btn_action_frame = tk.Frame(right_panel, bg=CARD)
        btn_action_frame.pack(fill="x", pady=(2, 0))

        self.btn_run = tk.Button(btn_action_frame, text="⚡ Generate 6 Package Files", font=("Segoe UI", 10, "bold"),
                                 bg=ACCENT, fg="white", relief="flat", pady=6,
                                 activebackground=ACCENT_HOVER, activeforeground="white",
                                 command=self.run_packaging)
        self.btn_run.pack(fill="x", pady=(0, 4))
        self.add_hover_effect(self.btn_run, ACCENT, ACCENT_HOVER)

        sub_btns = tk.Frame(btn_action_frame, bg=CARD)
        sub_btns.pack(fill="x")

        btn_open = tk.Button(sub_btns, text="📂 Open Output Folder", font=("Segoe UI", 8),
                             bg=BTN_DARK, fg="white", relief="flat", pady=4,
                             command=self.open_current_output)
        btn_open.pack(side="left", fill="x", expand=True, padx=(0, 2))
        self.add_hover_effect(btn_open, BTN_DARK, BTN_HOVER)

        btn_reset = tk.Button(sub_btns, text="🔄 Reset", font=("Segoe UI", 8),
                              bg=BTN_DARK, fg="white", relief="flat", pady=4,
                              command=self.reset_all)
        btn_reset.pack(side="right", fill="x", expand=True, padx=(2, 0))
        self.add_hover_effect(btn_reset, BTN_DARK, BTN_HOVER)

        # ================= FOOTER =================
        footer = tk.Frame(self.root, bg=BG)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(2, 6))

        tk.Label(footer, text=f"{APP_NAME} {APP_VERSION} | Drop to Auto-Pack 6 Files | Pradul P",
                 font=("Segoe UI", 8), bg=BG, fg=TEXT_MUTED).pack(side="left")
        tk.Label(footer, text="Press <Enter> to Generate", font=("Segoe UI", 8),
                 bg=BG, fg=TEXT_MUTED).pack(side="right")

    # ================= HELPER UI CREATION =================

    def create_field_label(self, parent, text, required=False, hint=""):
        f = tk.Frame(parent, bg=CARD)
        f.pack(fill="x", pady=(3, 0))
        lbl = tk.Label(f, text=text, font=("Segoe UI", 9, "bold"), bg=CARD, fg=TEXT_MUTED)
        lbl.pack(side="left")
        if required:
            tk.Label(f, text=" *", font=("Segoe UI", 9, "bold"), bg=CARD, fg=ACCENT_WARN).pack(side="left")
        if hint:
            tk.Label(f, text=f" {hint}", font=("Segoe UI", 8), bg=CARD, fg=TEXT_MUTED).pack(side="left")

    def create_button(self, parent, text, command, width=None):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 8),
                        bg=BTN_DARK, fg="white", relief="flat",
                        activebackground=BTN_HOVER, activeforeground="white",
                        command=command, width=width)
        self.add_hover_effect(btn, BTN_DARK, BTN_HOVER)
        return btn

    def add_hover_effect(self, widget, normal, hover):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal))

    def bind_events(self):
        self.sep_var.trace_add("write", lambda *args: self.update_live_preview())
        self.include_rev_var.trace_add("write", lambda *args: self.update_live_preview())
        self.include_date_var.trace_add("write", lambda *args: self.update_live_preview())
        self.root.bind("<Return>", lambda e: self.run_packaging())

    def save_autopack_pref(self):
        conf = load_config()
        conf["auto_pack_on_drop"] = self.auto_pack_var.get()
        save_config(conf)

    # ================= EVENT HANDLERS & LOGIC =================

    def set_revision(self, rev):
        self.rev_var.set(rev)
        self.include_rev_var.set(True)
        self.update_live_preview()

    def paste_to_var(self, str_var):
        try:
            content = self.root.clipboard_get()
            if content:
                str_var.set(content.strip())
                self.update_live_preview()
        except Exception:
            pass

    def copy_preview_name(self):
        preview = self.compute_base_name()
        if preview:
            self.root.clipboard_clear()
            self.root.clipboard_append(preview)
            self.status_lbl.config(text="Copied base name to clipboard! 📋", fg=ACCENT_GREEN)

    def compute_base_name(self, drawing_name=""):
        client = sanitize_filename(self.client_var.get().strip()) or "CLIENT"
        project = sanitize_filename(self.project_var.get().strip()) or (drawing_name or "PROJECT")
        sep = self.sep_var.get()

        date_str = ""
        if self.include_date_var.get():
            try:
                date_str = self.date_picker.get_date().strftime("%d-%m-%Y")
            except Exception:
                date_str = datetime.now().strftime("%d-%m-%Y")

        rev_str = ""
        if self.include_rev_var.get() and self.rev_var.get().strip():
            rev_str = sanitize_filename(self.rev_var.get().strip())

        pattern = self.pattern_var.get()
        if pattern == "Client_Project_Rev_Date":
            tokens = [t for t in [client, project, rev_str, date_str] if t]
        elif pattern == "Client_Rev_Date":
            tokens = [t for t in [client, rev_str, date_str] if t]
        elif pattern == "Client_Project":
            tokens = [t for t in [client, project] if t]
        elif pattern == "Project_Client_Rev_Date":
            tokens = [t for t in [project, client, rev_str, date_str] if t]
        else:
            tokens = [t for t in [client, project, rev_str, date_str] if t]

        return sep.join(tokens)

    def update_live_preview(self):
        example_drawing = self.detected_pairs[0]["base"] if self.detected_pairs else "Drawing"
        client_base = self.compute_base_name(example_drawing)
        proj_base = sanitize_filename(self.project_var.get().strip()) or example_drawing

        self.preview_lbl.config(
            text=f"1-3. Client:  {client_base}.(pdf / dwg / zip)\n4-6. Project: {proj_base}.(pdf / dwg / zip)"
        )

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_var.set(folder)
            self.process_incoming_path(folder, auto_run_if_ready=False)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_var.set(folder)

    def create_info_txt_dialog(self):
        """Prompt to create a template info.txt in the chosen folder."""
        folder = self.input_var.get().strip()
        if not folder or not os.path.exists(folder):
            folder = filedialog.askdirectory(title="Select Project / 00share Folder to Create info.txt")

        if folder and os.path.isdir(folder):
            txt_path = os.path.join(folder, "info.txt")
            client_def = self.client_var.get().strip() or "CLIENT NAME"
            proj_def = self.project_var.get().strip() or "PROJECT NAME"
            rev_def = self.rev_var.get().strip() or "R01"

            sample_content = f"Client: {client_def}\nProject: {proj_def}\nRevision: {rev_def}\nFormat: Client_Project_Rev_Date\n"
            try:
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(sample_content)
                self.txt_status_lbl.config(text=f"Created: {os.path.basename(txt_path)} in {os.path.basename(folder)}", fg=ACCENT_GREEN)
                messagebox.showinfo("Success", f"Created info.txt in:\n{txt_path}\n\nYou can edit this file to configure naming for this folder.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create info.txt:\n{e}")

    def handle_drop(self, event):
        raw_data = event.data
        files = self.root.tk.splitlist(raw_data)
        clean_paths = [f.strip("{}").strip() for f in files if f.strip("{}").strip()]

        if not clean_paths:
            return

        target = clean_paths[0] if (len(clean_paths) == 1 and os.path.isdir(clean_paths[0])) else clean_paths
        if isinstance(target, str) and os.path.isdir(target):
            self.input_var.set(target)
        else:
            first_dir = os.path.dirname(clean_paths[0])
            if not self.input_var.get():
                self.input_var.set(first_dir)

        # Process path and trigger auto-pack if enabled
        self.process_incoming_path(target, auto_run_if_ready=self.auto_pack_var.get())

    def process_incoming_path(self, target, auto_run_if_ready=False):
        # 1. Parse metadata text file if present (e.g. info.txt, 00share.txt, client.txt)
        meta, txt_file = MetadataParser.find_and_parse(target)
        if meta and (meta.get("client") or meta.get("project")):
            self.current_txt_file = txt_file
            if meta.get("client"):
                self.client_var.set(meta["client"])
            if meta.get("project"):
                self.project_var.set(meta["project"])
            if meta.get("rev"):
                self.rev_var.set(meta["rev"])
            if meta.get("pattern"):
                self.pattern_var.set(meta["pattern"])
            if meta.get("sep"):
                self.sep_var.set(meta["sep"])

            self.txt_status_lbl.config(
                text=f"Config loaded from: {os.path.basename(txt_file)} (Client: {meta.get('client', '-')})",
                fg=ACCENT_GREEN
            )
        else:
            self.txt_status_lbl.config(
                text="No info.txt found in folder (using GUI Client & Project settings)",
                fg=TEXT_MUTED
            )

        # 2. Scan drawing pairs
        pairs, zips = DrawingScanner.scan_path(target)
        self.detected_pairs = pairs
        self.detected_zips = zips

        # Populate listbox
        self.pairs_listbox.delete(0, tk.END)
        for i, pair in enumerate(pairs):
            status_icon = "✅" if pair["status"] in ["Complete", "Matched Pair"] else "⚠️"
            dwg_sz = format_size(os.path.getsize(pair["dwg"])) if pair["dwg"] else "Missing"
            pdf_sz = format_size(os.path.getsize(pair["pdf"])) if pair["pdf"] else "Missing"
            item_text = f" {status_icon} [{pair['status']}] {pair['base']} (PDF: {pdf_sz} | DWG: {dwg_sz})"
            self.pairs_listbox.insert(tk.END, item_text)

        self.detected_summary_lbl.config(
            text=f"Detected Drawings: {len(pairs)} item(s) ({sum(1 for p in pairs if p['status'] in ['Complete', 'Matched Pair'])} complete)"
        )

        # Auto-adjust modes based on zip existence
        if zips:
            self.mode_var.set("All in One (CAD+PDF+ZIP)")
        else:
            self.mode_var.set("CAD + PDF")

        if pairs:
            self.status_lbl.config(text=f"Detected {len(pairs)} drawing(s). Ready.", fg=ACCENT_GREEN)
            self.pairs_listbox.selection_set(0)
            self.update_live_preview()

            # ⚡ ZERO-CLICK AUTO-PACK: If enabled and client is present, run immediately!
            if auto_run_if_ready and self.client_var.get().strip():
                self.root.after(100, self.run_packaging)
        else:
            self.status_lbl.config(text="No DWG or PDF drawings found in selection.", fg=ACCENT_WARN)

    def on_pair_selected(self, event):
        selection = self.pairs_listbox.curselection()
        if selection and selection[0] < len(self.detected_pairs):
            self.update_live_preview()

    def get_effective_output_folder(self):
        output_folder = self.output_var.get().strip()
        if output_folder:
            return output_folder

        input_folder = self.input_var.get().strip()
        if input_folder and os.path.exists(input_folder):
            if os.path.isdir(input_folder):
                return os.path.join(input_folder, "output_files")
            else:
                return os.path.join(os.path.dirname(input_folder), "output_files")

        if self.detected_pairs:
            sample_file = self.detected_pairs[0]["pdf"] or self.detected_pairs[0]["dwg"]
            if sample_file:
                return os.path.join(os.path.dirname(sample_file), "output_files")

        return os.path.join(os.getcwd(), "output_files")

    def open_current_output(self):
        folder = self.get_effective_output_folder()
        if os.path.exists(folder):
            safe_open_folder(folder)
        else:
            messagebox.showinfo("Output Folder", f"Output folder does not exist yet:\n{folder}\n\nRun 'Generate 6 Package Files' first.")

    def reset_all(self):
        self.client_var.set("")
        self.project_var.set("")
        self.rev_var.set("R01")
        self.include_rev_var.set(True)
        self.include_date_var.set(True)
        self.input_var.set("")
        self.output_var.set("")
        self.detected_pairs = []
        self.detected_zips = []
        self.pairs_listbox.delete(0, tk.END)
        self.detected_summary_lbl.config(text="Detected Drawings: 0 pairs")
        self.progress_bar["value"] = 0
        self.status_lbl.config(text="Reset complete.", fg=TEXT_MUTED)
        self.txt_status_lbl.config(text="Drop a folder with info.txt or drawings to auto-fill", fg=TEXT_MUTED)
        self.update_live_preview()

    # ================= PACKAGING ENGINE (CREATES ALL 6 FILES) =================

    def run_packaging(self):
        client = self.client_var.get().strip()
        if not client:
            messagebox.showerror("Missing Client", "Client Name is required.\nProvide it in info.txt or type in the Client field.")
            return

        if not self.detected_pairs:
            messagebox.showerror("No Files", "No drawing files detected to package.")
            return

        is_batch = self.batch_chk_var.get()
        pairs_to_process = self.detected_pairs if (is_batch or len(self.detected_pairs) == 1) else [
            self.detected_pairs[self.pairs_listbox.curselection()[0]] if self.pairs_listbox.curselection() else self.detected_pairs[0]
        ]

        valid_pairs = [p for p in pairs_to_process if p["pdf"] and (p["dwg"] or self.mode_var.get() == "ZIP + PDF")]
        if not valid_pairs:
            messagebox.showerror("Invalid Files", "At least one drawing requires a PDF (and DWG for CAD modes).")
            return

        output_dir = self.get_effective_output_folder()
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Folder Error", f"Could not create output directory:\n{e}")
            return

        # Save to history
        add_to_recent("recent_clients", client)
        project_entered = self.project_var.get().strip()
        if project_entered:
            add_to_recent("recent_projects", project_entered)
        if self.include_rev_var.get() and self.rev_var.get().strip():
            add_to_recent("recent_revisions", self.rev_var.get().strip())

        self.client_combo["values"] = load_config().get("recent_clients", [])
        self.project_combo["values"] = load_config().get("recent_projects", [])
        self.rev_combo["values"] = load_config().get("recent_revisions", [])

        # Start Packaging Loop
        mode = self.mode_var.get()
        total = len(valid_pairs)
        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = 0

        self.btn_run.config(state="disabled")
        self.status_lbl.config(text=f"Creating packages ({total} drawing sets)...", fg=ACCENT)
        self.root.update_idletasks()

        success_count = 0
        total_created_files = 0
        try:
            for idx, pair in enumerate(valid_pairs):
                drawing_name = pair["base"]
                client_base = self.compute_base_name(drawing_name)
                project_name = sanitize_filename(self.project_var.get().strip()) or drawing_name

                # 1. Package Client set: creates 3 files (.pdf, .dwg, .zip)
                self.create_bundle(
                    dest_folder=output_dir,
                    bundle_name=client_base,
                    pdf_src=pair["pdf"],
                    dwg_src=pair["dwg"],
                    zip_src=pair["zip"],
                    mode=mode
                )
                total_created_files += 3

                # 2. Package Project set: creates 3 files (.pdf, .dwg, .zip)
                if project_name != client_base:
                    self.create_bundle(
                        dest_folder=output_dir,
                        bundle_name=project_name,
                        pdf_src=pair["pdf"],
                        dwg_src=pair["dwg"],
                        zip_src=pair["zip"],
                        mode=mode
                    )
                    total_created_files += 3

                success_count += 1
                self.progress_bar["value"] = success_count
                self.status_lbl.config(text=f"Packaged ({success_count}/{total}): {drawing_name}")
                self.root.update_idletasks()

            self.status_lbl.config(
                text=f"Done! Created all {total_created_files} files in output folder ✅",
                fg=ACCENT_GREEN
            )
            safe_open_folder(output_dir)

        except Exception as err:
            messagebox.showerror("Packaging Error", f"An error occurred while packaging:\n{str(err)}")
            self.status_lbl.config(text=f"Error: {str(err)}", fg=ACCENT_WARN)
        finally:
            self.btn_run.config(state="normal")

    def create_bundle(self, dest_folder, bundle_name, pdf_src, dwg_src, zip_src, mode):
        """Creates copies of drawings and zips them with the designated bundle name."""
        pdf_dest = os.path.join(dest_folder, f"{bundle_name}.pdf")
        dwg_dest = os.path.join(dest_folder, f"{bundle_name}.dwg")
        zip_dest = os.path.join(dest_folder, f"{bundle_name}.zip")

        if pdf_src and os.path.exists(pdf_src):
            shutil.copy2(pdf_src, pdf_dest)

        if dwg_src and os.path.exists(dwg_src):
            shutil.copy2(dwg_src, dwg_dest)

        with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as z:
            if pdf_src and os.path.exists(pdf_dest):
                z.write(pdf_dest, f"{bundle_name}.pdf")

            if mode in ["CAD + PDF", "All in One (CAD+PDF+ZIP)"] and dwg_src and os.path.exists(dwg_dest):
                z.write(dwg_dest, f"{bundle_name}.dwg")

            if mode in ["ZIP + PDF", "All in One (CAD+PDF+ZIP)"] and zip_src and os.path.exists(zip_src):
                z.write(zip_src, f"{bundle_name}_source.zip")


# ================= APPLICATION ENTRY POINT =================

def main():
    root = TkinterDnD.Tk()
    app = DrawingPackagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
