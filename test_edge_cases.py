"""
Unit tests and edge-case testing for StencilOCREngine
"""
import pytest
import numpy as np
import cv2
import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from ocr_engine import StencilOCREngine, IMPLEMENT_CATALOG, STATE_CODES

@pytest.fixture(scope="module")
def engine():
    return StencilOCREngine()

def test_clean_token(engine):
    assert engine.clean_token("CJ/142") == "GJ/142"
    assert engine.clean_token("Cl/142") == "GJ/142"
    assert engine.clean_token("GU/142") == "GJ/142"
    assert engine.clean_token("  GJ/445  ") == "GJ/445"
    assert engine.clean_token("!GJ/142.") == "GJ/142"
    assert engine.clean_token("2O26") == "2026"
    assert engine.clean_token("2O23") == "2023"

def test_parse_components(engine):
    # Standard 5-part code
    parsed = engine.parse_components("GJ/142/446/2026/11881")
    assert parsed["is_valid"] is True
    assert parsed["state_code"] == "GJ"
    assert parsed["state_name"] == "Gujarat"
    assert parsed["mfr_code"] == "142"
    assert parsed["model_code"] == "446"
    assert parsed["year"] == "2026"
    assert parsed["serial_no"] == "11881"
    assert parsed["suffix"] == ""
    assert parsed["model_info"]["series"] == "Heavy Duty / Semi Series"

    # With suffix
    parsed_up = engine.parse_components("GJ/142/446/2026/11881/UP")
    assert parsed_up["is_valid"] is True
    assert parsed_up["suffix"] == "UP"

    # Different state code (e.g. Maharashtra, Rajasthan)
    parsed_mh = engine.parse_components("MH/105/444/2025/12345")
    assert parsed_mh["is_valid"] is True
    assert parsed_mh["state_code"] == "MH"
    assert parsed_mh["state_name"] == "Maharashtra"

    # Invalid / empty
    parsed_invalid = engine.parse_components("RANDOM_TEXT_HERE")
    assert parsed_invalid["is_valid"] is False

def test_normalize_two_line_stencil(engine):
    # Image 2 case
    code, info = engine.normalize_code_from_lines(["CJ/142/3674", "12026/10652"])
    assert code == "GJ/142/3674/2026/10652"
    assert info["is_valid"] is True

    # Image 3 case: slashes read as 1
    code, info = engine.normalize_code_from_lines(["GJ/14213674", "12026110568"])
    assert code == "GJ/142/3674/2026/10568"
    assert info["is_valid"] is True

    # Reversed order: line 2 before line 1
    code_rev, info_rev = engine.normalize_code_from_lines(["12026110568", "GJ/14213674"])
    assert code_rev == "GJ/142/3674/2026/10568"
    assert info_rev["is_valid"] is True

    # With noise lines
    code_noise, info_noise = engine.normalize_code_from_lines([
        "FACTORY LOGO", "12026/10652", "SECTION 4", "CJ/142/3674", "WELD 01"
    ])
    assert code_noise == "GJ/142/3674/2026/10652"
    assert info_noise["is_valid"] is True

def test_normalize_single_line_stencil(engine):
    # Image 1 case
    code, info = engine.normalize_code_from_lines(["GJ/142/446/2026/11881/UP"])
    assert code == "GJ/142/446/2026/11881/UP"
    assert info["is_valid"] is True

    # Image 4 case
    code, info = engine.normalize_code_from_lines(["GJ/142/445/2026/43889"])
    assert code == "GJ/142/445/2026/43889"
    assert info["is_valid"] is True

    # Embedded code within noise text
    code_emb, info_emb = engine.normalize_code_from_lines(["PART GJ/142/445/2026/43889 LOT 3"])
    assert code_emb == "GJ/142/445/2026/43889"
    assert info_emb["is_valid"] is True

def test_order_points_no_collapse(engine):
    # Rotated quadrilateral at ~45 degrees
    rotated_pts = np.array([[100, 100], [200, 200], [150, 250], [50, 150]], dtype=np.float32)
    ordered = engine._order_points(rotated_pts)
    assert len(ordered) == 4
    # Ensure all 4 vertices are unique (no duplicates)
    unique_rows = np.unique(ordered, axis=0)
    assert len(unique_rows) == 4

def test_digital_stamp_generation(engine):
    parsed = engine.parse_components("GJ/142/446/2026/11881/UP")
    stamp = engine.generate_digital_stamp("GJ/142/446/2026/11881/UP", parsed)
    assert stamp is not None
    assert stamp.shape == (200, 800, 3)
    # Background should be predominantly black
    assert np.mean(stamp[0:5, 0:5]) == 0

def test_reference_document_detection(engine):
    chart_lines = [
        "LIST OF CODES FOR LASER MARKING",
        "SERIES",
        "MATERIAL CODE",
        "MODEL/SIZE",
        "CENTRALIZED IMPLE CODE SIZE",
        "SSUS", "TA147522LM", "7ft SSUS", "GJ/142",
        "REG SMART", "GJ/142/444/2023"
    ]
    assert engine._is_reference_document(chart_lines) is True
    assert engine._is_reference_document(["GJ/142/445/2026/43889"]) is False

def test_empty_and_corrupt_inputs(engine):
    # Blank image
    blank = np.zeros((200, 400, 3), dtype=np.uint8)
    res = engine.process_image(blank, auto_rotate=False)
    assert res["success"] is False or res["final_code"] == ""

    # None input
    res_none = engine.process_image(None)
    assert "error" in res_none

    # Corrupt bytes
    res_corrupt = engine.process_image(b"not_an_image")
    assert "error" in res_corrupt

def test_crop_and_binarize(engine):
    # Create synthetic test image with text
    test_img = np.zeros((100, 300, 3), dtype=np.uint8)
    box = [[10.0, 10.0], [290.0, 10.0], [290.0, 90.0], [10.0, 90.0]]
    cv2.putText(test_img, "GJ/142", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

    warped, thresh = engine.crop_and_binarize(test_img, box)
    assert warped is not None
    assert thresh is not None
    # Check that thresh has 0 and 255 values
    assert np.all(np.isin(thresh, [0, 255]))

def test_real_dataset_images(engine):
    samples = [
        ("sample1_beam_upsidedown.jpg", "WhatsApp Image 2026-10-22 at 4.55.31 PM.jpeg", "GJ/142/446/2026/11881/UP"),
        ("sample2_bracket_2line.jpg", "WhatsApp Image 2026-10-22 at 4.55.31 PM (1).jpeg", "GJ/142/3674/2026/10652"),
        ("sample3_plate_2line.jpg", "WhatsApp Image 2026-10-22 at 4.55.32 PM.jpeg", "GJ/142/3674/2026/10568"),
        ("sample4_tube_vertical.jpg", "WhatsApp Image 2026-10-22 at 4.55.32 PM (1).jpeg", "GJ/142/445/2026/43889"),
    ]
    for clean_name, legacy_name, expected in samples:
        path = os.path.join(root_dir, "samples", clean_name)
        if not os.path.exists(path):
            path = os.path.join(root_dir, legacy_name)
        if os.path.exists(path):
            res = engine.process_image(path)
            assert res["final_code"] == expected, f"Failed on {path}: got {res['final_code']}, expected {expected}"
            assert res["cropped_binary"] is not None
            assert res["digital_stamp"] is not None
