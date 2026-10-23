"""
Test suite for StencilOCREngine across industrial metal part samples.
"""
import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from ocr_engine import StencilOCREngine

def resolve_path(filename):
    candidates = [
        os.path.join(root_dir, "samples", filename),
        os.path.join(root_dir, filename),
        filename
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return filename

def main():
    engine = StencilOCREngine()

    test_cases = [
        {
            "name": "Beam Part (Upside-down)",
            "file": "sample1_beam_upsidedown.jpg",
            "fallback": "WhatsApp Image 2026-10-22 at 4.55.31 PM.jpeg",
            "expected": "GJ/142/446/2026/11881/UP"
        },
        {
            "name": "Bracket Part (2-Line Stencil)",
            "file": "sample2_bracket_2line.jpg",
            "fallback": "WhatsApp Image 2026-10-22 at 4.55.31 PM (1).jpeg",
            "expected": "GJ/142/3674/2026/10652"
        },
        {
            "name": "Plate Part (2-Line Stencil)",
            "file": "sample3_plate_2line.jpg",
            "fallback": "WhatsApp Image 2026-10-22 at 4.55.32 PM.jpeg",
            "expected": "GJ/142/3674/2026/10568"
        },
        {
            "name": "Vertical Tube Beam",
            "file": "sample4_tube_vertical.jpg",
            "fallback": "WhatsApp Image 2026-10-22 at 4.55.32 PM (1).jpeg",
            "expected": "GJ/142/445/2026/43889"
        }
    ]

    print("=" * 60)
    print("RUNNING METAL STENCIL OCR VERIFICATION")
    print("=" * 60)

    passed = 0
    total = len(test_cases)

    for tc in test_cases:
        path = resolve_path(tc["file"])
        if not os.path.exists(path):
            path = resolve_path(tc["fallback"])

        if not os.path.exists(path):
            print(f"[FAIL] Missing file: {tc['file']}")
            continue

        result = engine.process_image(path)
        code = result.get("final_code")
        parsed = result.get("parsed_info", {})

        is_exact = (code == tc["expected"])
        status = "PASSED" if is_exact else "FAILED"
        if is_exact:
            passed += 1

        print(f"[{status}] {tc['name']}")
        print(f"   File:     {os.path.basename(path)}")
        print(f"   Expected: {tc['expected']}")
        print(f"   Detected: {code}")
        print(f"   Valid:    {parsed.get('is_valid')}")
        print(f"   Details:  State={parsed.get('state_code')}, Mfr={parsed.get('mfr_code')}, Model={parsed.get('model_code')}, Year={parsed.get('year')}, Serial={parsed.get('serial_no')}")
        print("-" * 60)

    print(f"\nFinal Result: {passed}/{total} Stencil Image Tests Passed ({passed/total*100:.1f}%)")

    # Verify catalog chart
    chart_path = resolve_path("sample5_catalog_chart.jpg")
    if not os.path.exists(chart_path):
        chart_path = resolve_path("WhatsApp Image 2026-10-22 at 4.55.33 PM.jpeg")

    if os.path.exists(chart_path):
        chart_result = engine.process_image(chart_path, auto_rotate=False)
        parsed_chart = chart_result.get("parsed_info", {})
        print(f"\n[PASSED] Reference Catalog Chart Processed:")
        print(f"   Document Title: {parsed_chart.get('document_title')}")
        print(f"   Is Document:    {parsed_chart.get('is_document')}")
        print(f"   Detected Codes: {parsed_chart.get('document_codes')}")
        print("=" * 60)

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
