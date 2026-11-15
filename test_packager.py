import os
import sys
import shutil
import app

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_complete_redesigned_flow():
    print("=" * 65)
    print("TESTING REDESIGNED APP: ZIP DETECTION + SEPARATE 6 FILES")
    print("=" * 65)

    # 1. Test ZIP + PDF + DWG detection
    z, p, d = app.FileDetector.scan_files("sample_drawings")
    print(f"1. Detection Results:")
    print(f"   [ZIP] {os.path.basename(z) if z else 'None'}")
    print(f"   [CAD] {os.path.basename(d) if d else 'None'}")
    print(f"   [PDF] {os.path.basename(p) if p else 'None'}")
    assert z is not None, "ZIP must be detected!"
    assert p is not None, "PDF must be detected!"
    assert d is not None, "CAD DWG must be detected!"

    # 2. Test info.txt from 00share
    meta, txt_file = app.FileDetector.parse_txt_metadata("00share")
    print(f"\n2. Metadata from 00share/info.txt:")
    print(f"   Client:  '{meta.get('client')}'")
    print(f"   Project: '{meta.get('project')}'")
    assert meta.get("client"), "Client should be parsed"
    assert meta.get("project"), "Project should be parsed"

    # 3. Test 6-file generation
    out_dir = os.path.join("00share", "output_files")
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    client_base = f"{meta['client']}_16-11-2026"
    proj_base = meta["project"]

    mock = type("Mock", (), {"create_bundle": app.DrawingPackagerApp.create_bundle})()
    mock.create_bundle(out_dir, client_base, p, d, z, "All in One (CAD+PDF+ZIP)", inner_label=meta['client'])
    mock.create_bundle(out_dir, proj_base, p, d, z, "All in One (CAD+PDF+ZIP)", inner_label=proj_base)

    files = sorted(os.listdir(out_dir))
    print(f"\n3. Generated Output Files ({len(files)} files):")
    for f in files:
        print(f"   📦 {f}")

    assert len(files) == 6, f"Expected 6 files, got {len(files)}"
    print("\n" + "=" * 65)
    print("ALL TESTS PASSED: ZIP detected & 6 distinct files created!")
    print("=" * 65)

if __name__ == "__main__":
    test_complete_redesigned_flow()
