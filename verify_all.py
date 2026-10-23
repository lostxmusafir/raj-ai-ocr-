"""
Comprehensive Verification and Audit Suite
Tests all endpoints, image inputs, response structures, edge cases, and SDK consistency.
"""
import sys
import os
import io
import json
import base64
import time

# Ensure root directory in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from server import app
from ocr_engine import StencilOCREngine, IMPLEMENT_CATALOG, STATE_CODES

def run_audit():
    print("=" * 70)
    print("🚀 STARTING DEEP AUDIT & END-TO-END VERIFICATION")
    print("=" * 70)
    
    client = app.test_client()
    passed_tests = 0
    total_tests = 0
    
    def record(name, condition, details=""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        status = "PASSED" if condition else "FAILED"
        if condition:
            passed_tests += 1
            print(f" [✓] {name}: {status}")
        else:
            print(f" [✗] {name}: {status} -> {details}")
        if details and condition:
            print(f"     Details: {details}")

    # -------------------------------------------------------------
    # 1. Base / Health Endpoints
    # -------------------------------------------------------------
    print("\n--- Phase 1: Base & Health Endpoints ---")
    r_root = client.get('/')
    record("GET /", r_root.status_code == 200, f"Status={r_root.status_code}, Service={r_root.get_json().get('service')}")
    
    r_health = client.get('/health')
    record("GET /health", r_health.status_code == 200 and r_health.get_json().get('status') == "healthy", f"Status={r_health.get_json().get('status')}")

    r_api_health = client.get('/api/health')
    record("GET /api/health", r_api_health.status_code == 200)

    # -------------------------------------------------------------
    # 2. Catalog Endpoint
    # -------------------------------------------------------------
    print("\n--- Phase 2: Catalog Endpoint ---")
    r_cat = client.get('/catalog')
    cat_data = r_cat.get_json() or {}
    record("GET /catalog status", r_cat.status_code == 200)
    record("Catalog contains model 444", "444" in cat_data.get("catalog", {}))
    record("Catalog contains model 445", "445" in cat_data.get("catalog", {}))
    record("Catalog contains model 446", "446" in cat_data.get("catalog", {}))
    record("Catalog contains model 447", "447" in cat_data.get("catalog", {}))
    record("Catalog contains model 3674", "3674" in cat_data.get("catalog", {}))
    record("Catalog contains states", "GJ" in cat_data.get("states", {}) and cat_data["states"]["GJ"] == "Gujarat")

    # -------------------------------------------------------------
    # 3. Real Image Benchmark Dataset Tests
    # -------------------------------------------------------------
    print("\n--- Phase 3: Real Image Benchmark Dataset Tests ---")
    benchmark_dataset = [
        {
            "file": "WhatsApp Image 2026-10-22 at 4.55.31 PM.jpeg",
            "expected_code": "GJ/142/446/2026/11881/UP",
            "expected_state": "GJ",
            "expected_model": "446",
            "expected_year": "2026",
            "expected_serial": "11881",
            "expected_suffix": "UP"
        },
        {
            "file": "WhatsApp Image 2026-10-22 at 4.55.31 PM (1).jpeg",
            "expected_code": "GJ/142/3674/2026/10652",
            "expected_state": "GJ",
            "expected_model": "3674",
            "expected_year": "2026",
            "expected_serial": "10652",
            "expected_suffix": ""
        },
        {
            "file": "WhatsApp Image 2026-10-22 at 4.55.32 PM.jpeg",
            "expected_code": "GJ/142/3674/2026/10568",
            "expected_state": "GJ",
            "expected_model": "3674",
            "expected_year": "2026",
            "expected_serial": "10568",
            "expected_suffix": ""
        },
        {
            "file": "WhatsApp Image 2026-10-22 at 4.55.32 PM (1).jpeg",
            "expected_code": "GJ/142/445/2026/43889",
            "expected_state": "GJ",
            "expected_model": "445",
            "expected_year": "2026",
            "expected_serial": "43889",
            "expected_suffix": ""
        }
    ]

    for item in benchmark_dataset:
        filepath = item["file"]
        if not os.path.exists(filepath):
            record(f"File exists {filepath}", False, "File missing on disk")
            continue
            
        with open(filepath, "rb") as f:
            bytes_data = f.read()

        # 3A: Test with include_images=false (Mobile mode)
        start_t = time.time()
        res_mobile = client.post('/ocr?include_images=false', data={'file': (io.BytesIO(bytes_data), 'part.jpg')})
        duration_ms = round((time.time() - start_t) * 1000, 1)
        
        record(f"POST /ocr mobile [{filepath}] HTTP 200", res_mobile.status_code == 200)
        data = res_mobile.get_json() or {}
        code = data.get("final_code")
        record(f"POST /ocr code accuracy [{filepath}]", code == item["expected_code"], f"Got: '{code}', Expected: '{item['expected_code']}' ({duration_ms}ms)")
        
        # Verify parsed components
        parsed = data.get("parsed_info", {})
        record(f"Parsed isValid [{filepath}]", parsed.get("is_valid") is True)
        record(f"Parsed State [{filepath}]", parsed.get("state_code") == item["expected_state"])
        record(f"Parsed Model [{filepath}]", parsed.get("model_code") == item["expected_model"])
        record(f"Parsed Year [{filepath}]", parsed.get("year") == item["expected_year"])
        record(f"Parsed Serial [{filepath}]", parsed.get("serial_no") == item["expected_serial"])
        if item["expected_suffix"]:
            record(f"Parsed Suffix [{filepath}]", parsed.get("suffix") == item["expected_suffix"])
            
        # Verify base64 exclusion in mobile mode
        record(f"Mobile payload excludes cropped_binary_base64", "cropped_binary_base64" not in data)
        record(f"Mobile payload excludes digital_stamp_base64", "digital_stamp_base64" not in data)

        # 3B: Test with include_images=true
        res_full = client.post('/ocr?include_images=true', data={'file': (io.BytesIO(bytes_data), 'part.jpg')})
        data_full = res_full.get_json() or {}
        record(f"Full payload has cropped_binary_base64 [{filepath}]", bool(data_full.get("cropped_binary_base64")))
        record(f"Full payload has digital_stamp_base64 [{filepath}]", bool(data_full.get("digital_stamp_base64")))

    # -------------------------------------------------------------
    # 4. Form Field Name Flexibility: 'image' vs 'file'
    # -------------------------------------------------------------
    print("\n--- Phase 4: Form Field Name Compatibility ---")
    with open(benchmark_dataset[0]["file"], "rb") as f:
        b = f.read()
    res_field_image = client.post('/ocr', data={'image': (io.BytesIO(b), 'test.jpg')})
    record("Upload using field name 'image'", res_field_image.status_code == 200 and res_field_image.get_json().get("final_code") == benchmark_dataset[0]["expected_code"])

    # -------------------------------------------------------------
    # 5. Base64 JSON Upload Payload (Method B)
    # -------------------------------------------------------------
    print("\n--- Phase 5: Base64 JSON Payload Upload ---")
    b64_str = base64.b64encode(b).decode('utf-8')
    res_json = client.post(
        '/ocr',
        data=json.dumps({"image": f"data:image/jpeg;base64,{b64_str}", "include_images": False}),
        content_type='application/json'
    )
    record("Upload using Base64 JSON payload", res_json.status_code == 200 and res_json.get_json().get("final_code") == benchmark_dataset[0]["expected_code"])

    # -------------------------------------------------------------
    # 6. Reference Specification Sheet Mode
    # -------------------------------------------------------------
    print("\n--- Phase 6: Reference Catalog Sheet ---")
    chart_file = "WhatsApp Image 2026-10-22 at 4.55.33 PM.jpeg"
    if os.path.exists(chart_file):
        with open(chart_file, "rb") as f:
            b_chart = f.read()
        res_chart = client.post('/ocr', data={'file': (io.BytesIO(b_chart), 'chart.jpg')})
        d_chart = res_chart.get_json() or {}
        record("Reference sheet status 200", res_chart.status_code == 200)
        record("Identified as document", d_chart.get("parsed_info", {}).get("is_document") is True)
        record("Extracted codes in sheet", len(d_chart.get("parsed_info", {}).get("document_codes", [])) > 0)

    # -------------------------------------------------------------
    # 7. Error Handling & Edge Cases
    # -------------------------------------------------------------
    print("\n--- Phase 7: Edge Cases & Error Handling ---")
    # Empty request
    r_empty = client.post('/ocr', data={})
    record("Empty payload returns HTTP 400", r_empty.status_code == 400)
    
    # Corrupt base64
    r_bad_b64 = client.post('/ocr', data=json.dumps({"image": "not_valid_base64"}), content_type='application/json')
    record("Corrupt base64 returns HTTP 400", r_bad_b64.status_code == 400)

    # Non-image file upload
    r_text_file = client.post('/ocr', data={'file': (io.BytesIO(b"Hello world, not an image"), 'dummy.txt')})
    record("Corrupt/Non-image file returns HTTP 400", r_text_file.status_code == 400)

    # Alias /api/ocr
    r_alias = client.post('/api/ocr', data={'file': (io.BytesIO(b), 'part.jpg')})
    record("Alias endpoint /api/ocr works identically", r_alias.status_code == 200 and r_alias.get_json().get("final_code") == benchmark_dataset[0]["expected_code"])

    # -------------------------------------------------------------
    # 8. Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"AUDIT COMPLETE: {passed_tests}/{total_tests} Tests Passed ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 70)

    if passed_tests == total_tests:
        print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY WITH 100% ACCURACY!")
        return 0
    else:
        print(f"WARNING: {total_tests - passed_tests} test(s) failed.")
        return 1

if __name__ == "__main__":
    exit_code = run_audit()
    sys.exit(exit_code)
