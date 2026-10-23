# Laser Cut Metal Stencil OCR & Implement Code Scanner

An industrial vision OCR application built with **Streamlit** and **RapidOCR (PaddleOCR ONNX)** designed for detecting, deskewing, binarizing, and recognizing laser-cut stencil codes on sheet metal parts, tubes, brackets, and agricultural implements.

---

## Features

- **Multi-Source Input**:
  - 📷 **Live Camera Scanner**: Scan directly via webcam or smartphone camera with `st.camera_input` (includes automatic EXIF orientation normalization).
  - 📁 **File Upload**: Upload high-resolution images (PNG, JPG, JPEG, WEBP).
  - 🖼️ **Sample Gallery**: Quick 1-click testing with all sample part images from the factory.
- **Robust Metal Stencil Recognition**:
  - Handles arbitrary orientations: horizontal, vertical, 180° upside-down, and skewed parts.
  - Handles both **1-line** and **2-line** laser stamped layouts regardless of line detection order.
  - Robust against noise text lines, logos, and metal surface scratches.
  - Bridges stencil gaps and splits (e.g. `CJ` → `GJ`, misread slashes `1` / `|` → `/`, letter `O` in year `2O26` → `2026`).
  - Supports all Indian State prefixes (`GJ`, `MH`, `MP`, `RJ`, `PB`, `HR`, `UP`, `KA`, `TN`, `AP`, `TS`, `DL`, etc.).
- **High-Contrast White-on-Black Visualization ("number white me print or background in black")**:
  - **Identified number printed in glowing White text on pure Black background** (`#000000`).
  - 📋 **1-Click Copy**: Built-in copy-to-clipboard code block for fast data entry.
  - 🔬 **Real Cutout Binarization**: Perspective-deskewed physical cutout patch rendered in high-contrast White text on pure Black.
  - 🏷️ **Digital Label Badge**: Synthetic high-resolution industrial label badge (White on Black) ready for immediate printing or inspection logging.
- **Implement Code Validation & Catalog Recognition**:
  - Validates according to the Indian Centralized Implement Code standard:
    `[State]/[Mfr Code]/[Model Code]/[Year]/[Serial No]/[Suffix]`
  - Semantic breakdown into State (e.g., Gujarat `GJ`), Manufacturer (`142`), Model Series (`444`, `445`, `446`, `447`, `3528`, `3674`), Year, and Serial unit.
  - **Document / Reference Chart Mode**: Intelligently identifies reference catalog documents (like the "List of Codes for Laser Marking"), extracting codes and displaying a searchable table of models, series categories, and sizes.
- **Export & History**:
  - Export detected code (TXT), structured JSON report, high-contrast binary mask (PNG), and digital label badge (PNG).
  - Interactive scan history log with timing metrics.

---

## Quick Start

### 1. Launch the Streamlit App
Double-click `run_app.bat` or run the following command in PowerShell:

```powershell
& "$env:LOCALAPPDATA\Python\bin\python.exe" -m streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

### 2. Run Tests
Verify OCR accuracy across all sample images:

```powershell
& "$env:LOCALAPPDATA\Python\bin\python.exe" test_ocr.py
```

Run the automated pytest unit and edge-case suite:

```powershell
& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest test_edge_cases.py -v
```

---

## File Structure

- `app.py`: Streamlit web interface and user interaction logic with high-contrast display cards.
- `ocr_engine.py`: OCR pipeline, rotation handling, RGB normalization, deskewing, binarization (White on Black), digital badge generation, and robust code parser.
- `test_ocr.py`: Verification script across all 5 sample images in the folder.
- `test_edge_cases.py`: Pytest suite covering token cleaning, 1-line/2-line normalization, reversed line order, noise resilience, quadrilateral vertex sorting, digital badge generation, and corrupt inputs.
- `run_app.bat`: Windows batch script with automatic local Python detection to launch the app with one click.
