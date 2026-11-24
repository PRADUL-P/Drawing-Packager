# 📋 LUDARP Drawing Packaging & Dispatch Quality Procedure (SOP)

**Document Code:** SOP-CAD-PKG-001  
**Version:** 2.0  
**Effective Date:** 2026-11-24  
**Scope:** Civil, Structural, Architectural & BIM Drawing Transmittals  

---

## 1. Objective & Purpose

This Standard Operating Procedure (SOP) defines the mandatory engineering quality procedure for preparing, validating, and generating standardized 6-file drawing packages using the **LUDARP Drawing Packager**.

The objective is to eliminate human error, guarantee 100% naming compliance across client and internal project archives, prevent revision corruption, and automate drawing bundle distribution in civil engineering workflows.

---

## 2. The 6-File Dispatch Architecture

Every drawing issue must generate **exactly 6 verified output files** divided into two distinct sets:

```text
📁 output_files/
│
├── 🔹 CLIENT SUBMISSION SET (3 Files - For External Issuance)
│   ├── [CLIENT_NAME]_[DD-MM-YYYY].pdf   (High-resolution vector PDF sheet)
│   ├── [CLIENT_NAME]_[DD-MM-YYYY].dwg   (Clean AutoCAD drawing file)
│   └── [CLIENT_NAME]_[DD-MM-YYYY].zip   (Compressed bundle with inner named files)
│
└── 🔸 PROJECT ARCHIVE SET (3 Files - For Internal Project Records)
    ├── [PROJECT_NAME].pdf               (Permanent project sheet archive)
    ├── [PROJECT_NAME].dwg               (Permanent project CAD drawing archive)
    └── [PROJECT_NAME].zip               (Full project model & background archive)
```

> [!IMPORTANT]
> **Strict Naming Isolation:**
> - **Client Files** are named strictly after the Client/Contractor with optional issuance date. **No internal revision numbers** appear on client files unless explicitly specified.
> - **Project Files** are named strictly after the Project/Drawing Code (e.g. `METRO_TERMINAL_B101` or `C-101_REV02`).

---

## 3. Pre-Packaging File Requirements & Checks

Before launching the packager, the Drafting / BIM team must ensure the following three core files are prepared:

| File Type | Mandatory? | Requirements & Quality Standard |
|---|---|---|
| **PDF Sheet (`.pdf`)** | **YES (Mandatory)** | Vector-exported, correct title block, approved stamps/signatures, scale verified. |
| **CAD Drawing (`.dwg`)** | Recommended | Purged (`PURGE`), audited (`AUDIT`), xrefs bound/relative, Layer 0 standard. |
| **ZIP Archive (`.zip`)** | Optional | Contains reference surveys, BIM models, point clouds, or background assets. |
| **Metadata File (`info.txt`)** | Optional (for Auto-Pack) | Text file with `Client: [Name]` and `Project: [Name]`. |

---

## 4. Standard Operating Procedures (Two Workflows)

### Workflow A: Zero-Click Auto-Packaging (Recommended for High Volume)

1. **Place `info.txt` in the source folder** (e.g. `00share/` or drawing folder) containing:
   ```text
   Client: ACME_INFRASTRUCTURE_CORP
   Project: METRO_TERMINAL_B101
   ```
   *(Tip: Use the **"💾 Save Current Names as info.txt"** button in the app if you want to generate this file automatically).*
2. **Launch `LUDARP Drawing Packager`** (via `.exe` or `python app.py`).
3. Ensure **`⚡ Auto-Pack on Drop`** toggle is **ON** in the top navigation bar.
4. **Drag and drop** the entire folder into the application window.
5. **Result:** The system instantly reads `info.txt`, detects CAD, PDF, and ZIP files, generates all 6 files in `output_files/`, and automatically opens Windows Explorer for immediate transmittal.

---

### Workflow B: Manual Quality Review Packaging

1. **Launch `LUDARP Drawing Packager`**.
2. **Input Client Name:** Enter client / contractor name (or use **Paste** button).
3. **Input Project Name:** Enter project code / drawing number (or leave blank to auto-inherit drawing name).
4. **Configure Date:**
   - Check **"Include Date on Client Package"** (Default: ON).
   - Verify date in calendar picker (`DD-MM-YYYY`).
5. **Drop Files or Folder:** Drag & drop the drawing folder or click **"📁 Choose Folder..."**.
6. **Verify Visual File Status Cards:**
   - 🔴 **PDF Sheet**: Must show file name and file size in green border.
   - 🔵 **CAD Drawing**: Shows file name and size.
   - 🟡 **ZIP Archive**: Shows archive name (or optional status).
7. **Verify Target Manifest:** Inspect the live preview box under **"TARGET OUTPUT MANIFEST"** to confirm all 6 filenames match client contract specifications.
8. **Select Packaging Mode:**
   - `CAD + PDF`: Standard 2-format transmittal.
   - `ZIP + PDF`: Model archive + sheet.
   - `All in One (CAD+PDF+ZIP)`: Full submission package.
9. **Click `⚡ GENERATE ALL 6 PACKAGE FILES`** (or press `<Enter>`).
10. The output folder opens automatically.

---

## 5. QA/QC Verification Checklist

Before emailing or uploading packages to the Client Portal / CDE (Common Data Environment), the Lead Engineer or Document Controller must perform this checklist:

```markdown
[ ] 1. All 6 files exist in the `output_files` directory.
[ ] 2. Client files match the exact legal client name.
[ ] 3. Project files match the drawing/BIM register number.
[ ] 4. PDF files open cleanly and text is selectable (vector).
[ ] 5. DWG files open in AutoCAD/Civil 3D without proxy/missing xref alerts.
[ ] 6. ZIP files open cleanly and test without CRC/corruption errors.
[ ] 7. Inner filenames inside the `.zip` archive match contract requirements.
[ ] 8. Date stamped on client files matches the official transmittal date.
```

---

## 6. Archival & Transmittal Protocol

1. **External Transmittal:**
   - Send the **Client Set** (`.pdf`, `.dwg`, `.zip`) attached to the formal Transmittal Sheet (`DOC-TR-XXXX`).
2. **Internal Server Archival:**
   - Move the **Project Set** (`.pdf`, `.dwg`, `.zip`) into the permanent internal project directory under `X:\Projects\[PROJECT_CODE]\Dispatched\`.
3. **Audit Log:**
   - The packager remembers the last 15 clients and projects automatically in `~/.ludarp_packager_config.json` for rapid repeat issues.

---

## 7. Troubleshooting & Exception Handling

| Issue / Alert | Root Cause | Corrective Action |
|---|---|---|
| **"PDF Required" popup** | No `.pdf` detected in the folder or dropped selection. | Export PDF from AutoCAD/Revit sheet layout and re-drop. |
| **"Client Name Required"** | Client input field is empty and no `info.txt` was found. | Type Client name or generate `info.txt` using the top button. |
| **DWG shows "Missing DWG"** | Drawing is stored in a subfolder or has an unsupported extension. | Click **Browse** on the CAD card to manually select the `.dwg`. |
| **File locked / Permission denied** | A file is open in AutoCAD, Acrobat, or 7-Zip. | Save and close the drawing in AutoCAD/Acrobat, then re-click Generate. |
| **Spaces in folder path** | Directory names have special characters or spaces. | LUDARP v2.0 natively parses paths with spaces. Ensure read/write access. |

---

**Approved by:** Engineering Quality & Document Control Team  
**System:** LUDARP Drawing Packager v2.0
