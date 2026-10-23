"""
Laser Cut Metal Stencil OCR Engine
Specialized in detecting, segmenting, and extracting laser-cut stencil codes from metal parts.
Handles arbitrary orientations (horizontal, vertical, 180 deg upside-down),
1-line and 2-line formats, and stencil-font bridge artifacts.
"""

import cv2
import numpy as np
import re
from typing import List, Dict, Any, Tuple, Optional
from rapidocr_onnxruntime import RapidOCR

# Reference implement catalog based on manufacturer specifications
IMPLEMENT_CATALOG = {
    "444": {"name": "REG SMART / REG", "series": "Regular Series", "sizes": ["5ft", "5.5ft", "6.5ft"]},
    "445": {"name": "REG V1 / SEMI MSS", "series": "Regular / Semi Series", "sizes": ["5ft", "5.5ft", "1.55m"]},
    "446": {"name": "TUSKER / SEMI HSS / SEMI CHA", "series": "Heavy Duty / Semi Series", "sizes": ["5ft", "6ft", "1.65m"]},
    "447": {"name": "VICTOR / 8ft SPM", "series": "Special Purpose Heavy Series", "sizes": ["7ft", "8ft", "2.0m"]},
    "3528": {"name": "REGULAR IMPLEMENT", "series": "Standard Centralized Implement", "sizes": ["Various"]},
    "3674": {"name": "BRACKET / STRUCTURAL MOUNT", "series": "Implement Bracket Sub-Assembly", "sizes": ["Standard"]},
}

STATE_CODES = {
    "GJ": "Gujarat",
    "MH": "Maharashtra",
    "MP": "Madhya Pradesh",
    "RJ": "Rajasthan",
    "PB": "Punjab",
    "HR": "Haryana",
    "UP": "Uttar Pradesh",
    "KA": "Karnataka",
    "TN": "Tamil Nadu",
    "AP": "Andhra Pradesh",
    "TS": "Telangana",
    "DL": "Delhi",
    "UK": "Uttarakhand",
    "BR": "Bihar",
    "JH": "Jharkhand",
    "OD": "Odisha",
    "WB": "West Bengal",
}

class StencilOCREngine:
    def __init__(self):
        # Initialize RapidOCR engine
        self.ocr = RapidOCR()

    def clean_token(self, text: str) -> str:
        """
        Clean OCR artifact noise and leading/trailing punctuation.
        Normalizes stencil cut bridges (slit in G/J, letter O in year, slashes as pipe/1).
        """
        t = text.strip()
        # Remove exterior stray symbols
        t = re.sub(r'^[^\w/|]+|[^\w/|]+$', '', t)

        # Normalize common stencil cut misrecognitions for State prefix
        # G often has a slit bridge making it look like C, Cl, Q, etc.
        # J top-bar bridge makes it look like I, 1, l, |, ]
        t = re.sub(r'^[CcQq][JjIil1|]/', 'GJ/', t)
        t = re.sub(r'^[Gg][JjIil1|]/', 'GJ/', t)
        t = re.sub(r'^[Gg][Uu]/', 'GJ/', t)
        t = re.sub(r'^[CcQq][JjIil1|]1', 'GJ/', t)
        t = re.sub(r'^[Gg][JjIil1|]1', 'GJ/', t)

        # Normalize year letter O: 2O23 / 2O26 -> 2023 / 2026
        t = re.sub(r'2[Oo](\d\d)', r'20\1', t)
        
        # Normalize internal pipe/backslash to slash
        t = re.sub(r'[\\|]+', '/', t)
        return t

    def parse_components(self, code: str) -> Dict[str, Any]:
        """
        Parse centralized implement code into semantic components:
        State / Manufacturer / Model / Year / Serial [/ Suffix]
        """
        parts = [p.strip() for p in code.split('/') if p.strip()]
        result = {
            "full_code": code,
            "state_code": "",
            "state_name": "",
            "mfr_code": "",
            "model_code": "",
            "model_info": None,
            "year": "",
            "serial_no": "",
            "suffix": "",
            "is_valid": False
        }

        if len(parts) >= 2 and parts[0] in STATE_CODES:
            result["state_code"] = parts[0]
            result["state_name"] = STATE_CODES.get(parts[0], "Central Implement Authority")
            result["mfr_code"] = parts[1] if len(parts) > 1 else ""

            if len(parts) >= 5:
                # Standard 5-part: GJ/142/446/2026/11881
                result["model_code"] = parts[2]
                result["year"] = parts[3]
                result["serial_no"] = parts[4]
                if len(parts) >= 6:
                    result["suffix"] = "/".join(parts[5:])
                result["is_valid"] = True
            elif len(parts) == 4:
                # Could be GJ/142/3674/2026 or GJ/142/2026/11881
                if len(parts[2]) == 4 and parts[2].startswith("20"):
                    result["year"] = parts[2]
                    result["serial_no"] = parts[3]
                else:
                    result["model_code"] = parts[2]
                    result["serial_no"] = parts[3]
                result["is_valid"] = True
            elif len(parts) == 3:
                result["model_code"] = parts[2]

            if result["model_code"] in IMPLEMENT_CATALOG:
                result["model_info"] = IMPLEMENT_CATALOG[result["model_code"]]

        return result

    def _extract_single_line_code(self, raw_text: str) -> Optional[str]:
        """
        Attempts to extract a 1-line implement code from a text line.
        Handles slashes misread as 1 or pipe, and embedded codes.
        """
        t = self.clean_token(raw_text)
        state_pat = '|'.join(STATE_CODES.keys())

        # Direct standard format with slashes: e.g. GJ/142/446/2026/11881/UP
        m1 = re.search(r'(' + state_pat + r')/(\d{2,4})/(\d{3,4})/(20\d\d)/(\d{4,6})(?:/([A-Za-z0-9]+))?', t)
        if m1:
            res = f"{m1.group(1)}/{m1.group(2)}/{m1.group(3)}/{m1.group(4)}/{m1.group(5)}"
            if m1.group(6):
                res += f"/{m1.group(6)}"
            return res

        # Slashes misread as 1 or | between digit segments: e.g. GJ/142144512026143889
        m2 = re.search(r'(' + state_pat + r')[/1|](\d{2,4})[1/|](\d{3,4})[1/|](20\d\d)[1/|](\d{4,6})(?:[1/|]([A-Za-z0-9]+))?', t)
        if m2:
            res = f"{m2.group(1)}/{m2.group(2)}/{m2.group(3)}/{m2.group(4)}/{m2.group(5)}"
            if m2.group(6):
                res += f"/{m2.group(6)}"
            return res

        # 4-part code without serial (e.g. catalog format GJ/142/447/2023)
        m3 = re.search(r'(' + state_pat + r')[/1|](\d{2,4})[1/|](\d{3,4})[1/|](20\d\d)', t)
        if m3:
            return f"{m3.group(1)}/{m3.group(2)}/{m3.group(3)}/{m3.group(4)}"

        return None

    def _extract_two_line_code(self, raw_detections: List[Dict[str, Any]]) -> Optional[Tuple[str, List[int]]]:
        """
        Searches all pairs of detected lines to locate and merge 2-line codes.
        Line A has State/Mfr[/Model] (e.g. GJ/142/3674 or CJ/142/3674 or GJ/14213674)
        Line B has Year/Serial (e.g. /2026/10652 or 12026/10652 or 12026110568)
        Returns (merged_code, [idx_a, idx_b]) if found, or None.
        """
        state_pat = '|'.join(STATE_CODES.keys())
        prefix_cands = []
        suffix_cands = []

        for idx, det in enumerate(raw_detections):
            raw = det["text"]
            t = self.clean_token(raw)

            # Check for prefix (State + Mfr + Model or State + Mfr)
            m_pref = re.search(r'(' + state_pat + r')[/1|](\d{2,4})[/1|](\d{3,4})', t)
            if m_pref:
                pref_code = f"{m_pref.group(1)}/{m_pref.group(2)}/{m_pref.group(3)}"
                prefix_cands.append((idx, pref_code))
                continue

            m_pref_short = re.search(r'(' + state_pat + r')[/1|](\d{2,4})', t)
            if m_pref_short:
                pref_code = f"{m_pref_short.group(1)}/{m_pref_short.group(2)}"
                prefix_cands.append((idx, pref_code))
                continue

            # Check for suffix (Year + Serial)
            t_year = re.sub(r'2[Oo](\d\d)', r'20\1', t)
            m_suf = re.search(r'[/1|Il]?(20\d\d)[/1|Il](\d{4,6})(?:[/1|Il]([A-Za-z0-9]+))?', t_year)
            if m_suf:
                suf_code = f"/{m_suf.group(1)}/{m_suf.group(2)}"
                if m_suf.group(3):
                    suf_code += f"/{m_suf.group(3)}"
                suffix_cands.append((idx, suf_code))

        # Pair candidates
        for idx_p, p_code in prefix_cands:
            for idx_s, s_code in suffix_cands:
                if idx_p != idx_s:
                    merged = p_code.rstrip('/') + s_code
                    return merged, [idx_p, idx_s]

        return None

    def normalize_code_from_detections(self, raw_detections: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any], List[List[float]]]:
        """
        Normalize detected OCR tokens into a validated Centralized Implement Code.
        Returns:
            (final_code, parsed_info, matched_boxes)
        """
        if not raw_detections:
            return "", {"full_code": "", "is_valid": False}, []

        # 1. First test each line for 1-line code
        for det in raw_detections:
            code = self._extract_single_line_code(det["text"])
            if code:
                parsed = self.parse_components(code)
                if parsed["is_valid"]:
                    return code, parsed, [det["box"]]

        # 2. Test for 2-line code combination across detections
        two_line_res = self._extract_two_line_code(raw_detections)
        if two_line_res:
            code, indices = two_line_res
            parsed = self.parse_components(code)
            if parsed["is_valid"]:
                matched_boxes = [raw_detections[i]["box"] for i in indices]
                return code, parsed, matched_boxes

        # 3. Fallback: check if any line starts with a state code
        for det in raw_detections:
            cleaned = self.clean_token(det["text"])
            parsed = self.parse_components(cleaned)
            if parsed["is_valid"]:
                return cleaned, parsed, [det["box"]]

        # 4. If none valid, return cleanest first detection
        best_text = self.clean_token(raw_detections[0]["text"])
        return best_text, self.parse_components(best_text), [raw_detections[0]["box"]]

    def normalize_code_from_lines(self, lines: List[str]) -> Tuple[str, Dict[str, Any]]:
        """
        Convenience method to normalize a list of raw text strings into a code.
        """
        if not lines:
            return "", {"full_code": "", "is_valid": False}
        fake_dets = [{"box": [[0, 0], [10, 0], [10, 10], [0, 10]], "text": l, "score": 1.0} for l in lines]
        code, parsed, _ = self.normalize_code_from_detections(fake_dets)
        return code, parsed

    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """
        Robustly order 4 quadrilateral points in clockwise sequence:
        top-left, top-right, bottom-right, bottom-left.
        Prevents vertex coordinate collapse.
        """
        pts = np.array(pts, dtype=np.float32)
        # Sort points by y-coordinate
        y_sorted = pts[np.argsort(pts[:, 1])]

        # Top two points
        top = y_sorted[:2]
        # Bottom two points
        bottom = y_sorted[2:]

        # Top-left has smaller x, top-right has larger x
        tl, tr = top[np.argsort(top[:, 0])]

        # Bottom-left has smaller x, bottom-right has larger x
        bl, br = bottom[np.argsort(bottom[:, 0])]

        return np.array([tl, tr, br, bl], dtype=np.float32)

    def crop_and_binarize(self, img: np.ndarray, box: List[List[float]], invert: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        """
        Crop text region with perspective correction and produce high-contrast
        White text on Black background (or inverted if requested).
        """
        pts = np.array(box, dtype=np.float32)
        h_img, w_img = img.shape[:2]

        # Expand box slightly (padding) for better contrast border
        center = np.mean(pts, axis=0)
        expanded_pts = []
        for p in pts:
            vec = p - center
            np_p = center + vec * 1.08
            np_p[0] = np.clip(np_p[0], 0, w_img - 1)
            np_p[1] = np.clip(np_p[1], 0, h_img - 1)
            expanded_pts.append(np_p)
        pts = np.array(expanded_pts, dtype=np.float32)

        # Order points
        ordered_pts = self._order_points(pts)

        # Calculate bounding dimensions
        width_a = np.linalg.norm(ordered_pts[0] - ordered_pts[1])
        width_b = np.linalg.norm(ordered_pts[2] - ordered_pts[3])
        max_w = max(int(width_a), int(width_b), 16)

        height_a = np.linalg.norm(ordered_pts[1] - ordered_pts[2])
        height_b = np.linalg.norm(ordered_pts[0] - ordered_pts[3])
        max_h = max(int(height_a), int(height_b), 16)

        # Perspective transform destination
        dst = np.array([
            [0, 0],
            [max_w - 1, 0],
            [max_w - 1, max_h - 1],
            [0, max_h - 1]
        ], dtype=np.float32)

        M = cv2.getPerspectiveTransform(ordered_pts, dst)
        warped = cv2.warpPerspective(img, M, (max_w, max_h), borderMode=cv2.BORDER_REPLICATE)

        # If vertical text (height > width * 1.3), rotate 90 deg counterclockwise so text reads horizontally
        if max_h > max_w * 1.3:
            warped = cv2.rotate(warped, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Convert to grayscale
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to normalize metal shadows/glare
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Bilateral filter to reduce metallic grain while keeping sharp stencil edges
        filtered = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)

        # Otsu thresholding
        _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Check background polarity:
        # Background is majority around the outer boundary
        border = np.concatenate([thresh[0, :], thresh[-1, :], thresh[:, 0], thresh[:, -1]])
        border_mean = np.mean(border)

        # Target: Text = WHITE (255), Background = BLACK (0)
        # If the border (background) is bright (>127), invert so background is pure BLACK
        if border_mean > 127:
            thresh = cv2.bitwise_not(thresh)

        # Morphological clean up for clean stencil edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        if invert:
            thresh = cv2.bitwise_not(thresh)

        return warped, thresh

    def generate_digital_stamp(self, code: str, parsed: Dict[str, Any]) -> np.ndarray:
        """
        Generates a clean, high-resolution digital stencil badge:
        Pure White text on Pure Black Background (#000000).
        Meets the 'number white me print or background in black' requirement
        both visually on screen and as an exportable/printable label.
        """
        h, w = 200, 800
        stamp = np.zeros((h, w, 3), dtype=np.uint8)

        # Double border
        cv2.rectangle(stamp, (8, 8), (w - 9, h - 9), (255, 255, 255), 2)
        cv2.rectangle(stamp, (14, 14), (w - 15, h - 15), (100, 100, 100), 1)

        # Header Title
        cv2.putText(stamp, "CENTRALIZED AGRICULTURAL IMPLEMENT LASER CODE", (28, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)

        # Main Code in Bold White
        code_str = code if code else "NO CODE DETECTED"
        cv2.putText(stamp, code_str, (28, 106),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 3, cv2.LINE_AA)

        # Subtitle / Details
        details = []
        if parsed.get("state_name"):
            details.append(f"STATE: {parsed['state_name']} ({parsed.get('state_code', '')})")
        if parsed.get("model_code"):
            m_name = parsed.get("model_info", {}).get("name", f"Model {parsed['model_code']}")
            details.append(f"MODEL: {m_name}")
        if parsed.get("year"):
            details.append(f"MFG: {parsed['year']}")
        if parsed.get("serial_no"):
            details.append(f"SN: {parsed['serial_no']}")
        if parsed.get("suffix"):
            details.append(f"MARK: {parsed['suffix']}")

        detail_line = " | ".join(details) if details else "INDUSTRIAL LASER STENCIL IDENTIFIER"
        cv2.putText(stamp, detail_line[:85], (28, 155),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 220, 220), 1, cv2.LINE_AA)

        # Status stamp
        status_txt = "[VERIFIED IMPLEMENT CODE]" if parsed.get("is_valid") else "[RAW / UNVERIFIED]"
        color = (255, 255, 255) if parsed.get("is_valid") else (180, 180, 180)
        cv2.putText(stamp, status_txt, (w - 240, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        return stamp

    def _is_reference_document(self, raw_lines: List[str]) -> bool:
        """Checks if the scanned image is a Reference Catalog Chart or multi-row document."""
        joined = " ".join(raw_lines).upper()
        keywords = ["LIST OF CODES", "LASER MARKING", "MATERIAL CODE", "MODEL/SIZE", "CENTRALIZED", "SERIES"]
        kw_matches = sum(1 for kw in keywords if kw in joined)
        return (kw_matches >= 2) or (len(raw_lines) >= 20 and kw_matches >= 1)

    def process_image(self, img_input: Any, auto_rotate: bool = True) -> Dict[str, Any]:
        """
        Full OCR pipeline for metal stencil detection and extraction.
        
        Args:
            img_input: file path, bytes, or numpy BGR image
            auto_rotate: whether to test rotations if no code detected
        """
        # Load image
        if isinstance(img_input, str):
            img = cv2.imread(img_input)
        elif isinstance(img_input, bytes):
            nparr = np.frombuffer(img_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif hasattr(img_input, 'read'): # UploadedFile or buffer
            bytes_data = img_input.read()
            nparr = np.frombuffer(bytes_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            img = img_input

        if img is None:
            return {"error": "Failed to decode input image"}

        h, w = img.shape[:2]

        # Convert to RGB for RapidOCR
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res, _ = self.ocr(img_rgb)

        # Check orientation scoring
        def calc_score(ocr_res):
            if not ocr_res:
                return 0.0
            scores = []
            has_code_token = False
            state_pat = '|'.join(STATE_CODES.keys())
            for r in ocr_res:
                scores.append(float(r[2]))
                txt = r[1]
                if re.search(r'(' + state_pat + r'|CJ|142|202\d)', txt):
                    has_code_token = True
            mean_sc = sum(scores) / len(scores) if scores else 0
            return mean_sc + (1.5 if has_code_token else 0.0)

        best_res = res
        best_angle = 0
        best_score = calc_score(res)

        # Test rotations if code not found with high confidence
        if auto_rotate and (not res or best_score < 1.5):
            for angle in [90, 180, 270]:
                if angle == 90:
                    rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                elif angle == 180:
                    rot = cv2.rotate(img, cv2.ROTATE_180)
                elif angle == 270:
                    rot = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                rot_rgb = cv2.cvtColor(rot, cv2.COLOR_BGR2RGB)
                cur_res, _ = self.ocr(rot_rgb)
                score = calc_score(cur_res)
                if score > best_score:
                    best_score = score
                    best_res = cur_res
                    best_angle = angle

        # Select active image orientation
        if best_angle == 90:
            active_img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif best_angle == 180:
            active_img = cv2.rotate(img, cv2.ROTATE_180)
        elif best_angle == 270:
            active_img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            active_img = img

        raw_detections = []
        raw_lines = []

        if best_res:
            for item in best_res:
                box, txt, score = item[0], item[1], float(item[2])
                raw_detections.append({
                    "box": box,
                    "text": txt,
                    "score": round(score, 3)
                })
                raw_lines.append(txt)

        # Check if reference document / catalog chart
        is_document = self._is_reference_document(raw_lines)
        doc_codes = []

        if is_document:
            # Extract all implement codes in the catalog document
            for line in raw_lines:
                c = self._extract_single_line_code(line)
                if c and c not in doc_codes:
                    doc_codes.append(c)

            # If specific codes found, select the most specific one as representative
            if doc_codes:
                final_code = doc_codes[0]
            else:
                final_code = "LIST OF CODES FOR LASER MARKING"

            parsed_info = {
                "full_code": final_code,
                "is_document": True,
                "document_title": "Reference Catalog Chart (List of Laser Marking Codes)",
                "document_codes": doc_codes,
                "is_valid": bool(doc_codes),
                "model_catalog": IMPLEMENT_CATALOG
            }
            matched_boxes = [d["box"] for d in raw_detections[:5]]
        else:
            # Standard single metal part stencil
            final_code, parsed_info, matched_boxes = self.normalize_code_from_detections(raw_detections)
            parsed_info["is_document"] = False

        # Cropped visualization
        cropped_color = None
        cropped_binary_white_on_black = None
        annotated_img = active_img.copy()

        if matched_boxes and not is_document:
            all_pts = []
            for b in matched_boxes:
                for pt in b:
                    all_pts.append(pt)
            all_pts = np.array(all_pts, dtype=np.float32)

            min_rect = cv2.minAreaRect(all_pts)
            box_points = cv2.boxPoints(min_rect)
            box_points = self._order_points(box_points)

            cropped_color, cropped_binary_white_on_black = self.crop_and_binarize(active_img, box_points.tolist())

        elif is_document:
            # For document, crop top header region for preview
            h_d, w_d = active_img.shape[:2]
            header_h = min(int(h_d * 0.35), 600)
            cropped_color = active_img[0:header_h, :]
            # Binarize document header (white text on pure black)
            gray_doc = cv2.cvtColor(cropped_color, cv2.COLOR_BGR2GRAY)
            _, doc_bin = cv2.threshold(gray_doc, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # If paper is white, invert so text is white on black background
            if np.mean(doc_bin) > 127:
                doc_bin = cv2.bitwise_not(doc_bin)
            cropped_binary_white_on_black = doc_bin

        # Draw bounding boxes on annotated image
        for det in raw_detections:
            pts = np.array(det["box"], dtype=np.int32)
            cv2.polylines(annotated_img, [pts], True, (0, 255, 0), 2)

        # Generate Digital High-Contrast Stamp (Pure White on Pure Black)
        digital_stamp = self.generate_digital_stamp(final_code, parsed_info)

        return {
            "success": bool(final_code),
            "final_code": final_code,
            "parsed_info": parsed_info,
            "raw_detections": raw_detections,
            "best_angle": best_angle,
            "annotated_image": annotated_img,
            "cropped_color": cropped_color,
            "cropped_binary": cropped_binary_white_on_black, # White text on pure black background
            "digital_stamp": digital_stamp, # High-res printable badge with white text on black background
        }
