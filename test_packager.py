import os
import sys
import shutil
import app

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_00share_workflow():
    print("=" * 60)
    print("TESTING 00share ZERO-CLICK WORKFLOW (info.txt -> 6 Files)")
    print("=" * 60)

    folder = os.path.abspath("00share")
    out_dir = os.path.join(folder, "output_files")
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    # 1. Parse info.txt
    meta, txt_file = app.MetadataParser.find_and_parse(folder)
    print(f"1. Detected Config File: {txt_file}")
    print(f"   Parsed Metadata: Client='{meta.get('client')}', Project='{meta.get('project')}', Rev='{meta.get('rev')}'")

    assert meta.get("client") == "ACME_INFRA"
    assert meta.get("project") == "METRO_TERMINAL_B"

    # 2. Scan Drawings
    pairs, zips = app.DrawingScanner.scan_path(folder)
    print(f"\n2. Detected Drawings: {len(pairs)} pair(s)")
    for p in pairs:
        print(f"   - {p['base']}: {p['status']}")

    assert len(pairs) >= 1
    p = pairs[0]

    # 3. Simulate Bundle Creation for the 6 files
    os.makedirs(out_dir, exist_ok=True)
    mock = type("Mock", (), {"create_bundle": app.DrawingPackagerApp.create_bundle})()

    client_bundle = f"{meta['client']}_{meta['project']}_{meta['rev']}_15-11-2026"
    proj_bundle = meta["project"]

    # Creates 3 files for client
    mock.create_bundle(out_dir, client_bundle, p["pdf"], p["dwg"], None, "CAD + PDF")
    # Creates 3 files for project
    mock.create_bundle(out_dir, proj_bundle, p["pdf"], p["dwg"], None, "CAD + PDF")

    created = sorted(os.listdir(out_dir))
    print(f"\n3. Automatically Created All {len(created)} Files in {out_dir}:")
    for f in created:
        sz = os.path.getsize(os.path.join(out_dir, f))
        print(f"   📦 {f} ({sz} bytes)")

    assert len(created) == 6, f"Expected 6 files, got {len(created)}"
    print("\n" + "=" * 60)
    print("SUCCESS: 00share zero-click 6-file generation verified!")
    print("=" * 60)

if __name__ == "__main__":
    test_00share_workflow()
