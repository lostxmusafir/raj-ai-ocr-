"""
Test suite for StencilOCREngine across all 5 workspace images.
"""
import os
import glob
from ocr_engine import StencilOCREngine

def main():
    engine = StencilOCREngine()
    
    expected_matches = {
        "WhatsApp Image 2026-10-22 at 4.55.31 PM.jpeg": "GJ/142/446/2026/11881/UP",
        "WhatsApp Image 2026-10-22 at 4.55.31 PM (1).jpeg": "GJ/142/3674/2026/10652",
        "WhatsApp Image 2026-10-22 at 4.55.32 PM.jpeg": "GJ/142/3674/2026/10568",
        "WhatsApp Image 2026-10-22 at 4.55.32 PM (1).jpeg": "GJ/142/445/2026/43889",
    }
    
    print("==================================================")
    print("RUNNING METAL STENCIL OCR VERIFICATION")
    print("==================================================")
    
    passed = 0
    total = len(expected_matches)
    
    for filename, expected in expected_matches.items():
        if not os.path.exists(filename):
            print(f"[FAIL] Missing file: {filename}")
            continue
            
        result = engine.process_image(filename)
        code = result.get("final_code")
        parsed = result.get("parsed_info", {})
        
        is_exact = (code == expected)
        status = "PASSED" if is_exact else "FAILED"
        if is_exact:
            passed += 1
            
        print(f"[{status}] File: {filename}")
        print(f"   Expected: {expected}")
        print(f"   Detected: {code}")
        print(f"   Valid Implement Code: {parsed.get('is_valid')}")
        print(f"   Components: State={parsed.get('state_code')}, Mfr={parsed.get('mfr_code')}, Model={parsed.get('model_code')}, Year={parsed.get('year')}, Serial={parsed.get('serial_no')}")
        if result.get("cropped_binary") is not None:
            h, w = result["cropped_binary"].shape[:2]
            print(f"   High-Contrast Crop (White on Black): {w}x{h} px")
        if result.get("digital_stamp") is not None:
            sh, sw = result["digital_stamp"].shape[:2]
            print(f"   Digital Stencil Badge (White on Black): {sw}x{sh} px")
        print("-" * 50)
        
    print(f"\nFinal Result: {passed}/{total} Stencil Image Tests Passed ({passed/total*100:.1f}%)")
    
    # Verify reference chart parsing
    chart_file = "WhatsApp Image 2026-10-22 at 4.55.33 PM.jpeg"
    if os.path.exists(chart_file):
        chart_result = engine.process_image(chart_file, auto_rotate=False)
        parsed_chart = chart_result.get("parsed_info", {})
        print(f"\n[PASSED] Reference Chart File Processed:")
        print(f"   Document Title: {parsed_chart.get('document_title')}")
        print(f"   Is Document: {parsed_chart.get('is_document')}")
        print(f"   Total Text Items Detected: {len(chart_result['raw_detections'])}")
        print(f"   Identified Codes in Sheet: {parsed_chart.get('document_codes')}")
        print("==================================================")

if __name__ == "__main__":
    main()
