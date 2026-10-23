# Laser Cut Metal Stencil OCR - Dedicated Backend REST API

An industrial vision OCR REST API service and Android SDK built for detecting, deskewing, binarizing, and recognizing laser-cut stencil codes on sheet metal parts, tubes, brackets, and agricultural implements.

📦 **GitHub Repository**: [https://github.com/lostxmusafir/raj-ai-ocr-.git](https://github.com/lostxmusafir/raj-ai-ocr-.git)

---

## Architecture Overview

- **Standalone Python REST API** (`server.py`): High-performance CPU inference via ONNX Runtime and OpenCV, with bridge-healing heuristics.
- **Native Android SDK Module** (`android/`): Ready-to-use Kotlin and Java client with automatic phone camera photo downscaling and Retrofit networking.
- **1-Click Local Server Launcher** (`run_api.bat`): Runs the API server on port 5000.

---

## Features

- **Robust Metal Stencil Recognition**:
  - Handles arbitrary orientations: horizontal, vertical, 180° upside-down, and skewed parts.
  - Handles both **1-line** and **2-line** laser stamped layouts regardless of line detection order.
  - Robust against noise text lines, logos, and metal surface scratches.
  - Bridges stencil gaps and splits (e.g. `CJ` → `GJ`, misread slashes `1` / `|` → `/`, letter `O` in year `2O26` → `2026`).
  - Supports all Indian State prefixes (`GJ`, `MH`, `MP`, `RJ`, `PB`, `HR`, `UP`, `KA`, `TN`, `AP`, `TS`, `DL`, etc.).
- **Implement Code Validation & Catalog Recognition**:
  - Validates according to the Indian Centralized Implement Code standard:
    `[State]/[Mfr Code]/[Model Code]/[Year]/[Serial No]/[Suffix]`
  - Semantic breakdown into State (e.g., Gujarat `GJ`), Manufacturer (`142`), Model Series (`444`, `445`, `446`, `447`, `3528`, `3674`), Year, and Serial unit.
- **High-Performance Lightweight API**:
  - Returns structured JSON in ~1 second.
  - Query parameter `?include_images=false` for ultra-compact ~500 byte responses on mobile networks.

---

## Running the API Server

### 1. Launch via Batch File (Windows)
Double-click `run_api.bat` in the root folder.

### 2. Launch via Command Line
```powershell
python server.py
```
The server will listen on `http://0.0.0.0:5000`.

---

## API Endpoints

### 1. Health Check
```bash
curl http://localhost:5000/health
```

### 2. Recognize Stencil Code from Image
```bash
curl -X POST -F "file=@part_photo.jpg" "http://localhost:5000/ocr?include_images=false"
```

Response JSON:
```json
{
  "status": "success",
  "final_code": "GJ/142/445/2026/43889",
  "parsed_info": {
    "is_valid": true,
    "state_code": "GJ",
    "state_name": "Gujarat",
    "mfr_code": "142",
    "model_code": "445",
    "year": "2026",
    "serial_no": "43889",
    "model_info": {
      "name": "REG V1 / SEMI MSS",
      "series": "Regular / Semi Series",
      "sizes": ["5ft", "5.5ft", "1.55m"]
    }
  },
  "best_angle": 0,
  "elapsed_ms": 1150.2
}
```

---

## Android Mobile SDK Module (`android/`)

The repository includes a ready-to-use Android library module with Kotlin & Java clients:

- `OcrSdk.kt` (Kotlin coroutines client with camera compression)
- `OcrJavaClient.java` (Java callback client)
- `OcrModels.kt` (Gson data classes)
- `build.gradle.kts` & `AndroidManifest.xml`

See [ANDROID_KOTLIN_JAVA_GUIDE.md](ANDROID_KOTLIN_JAVA_GUIDE.md) for full Android integration instructions.

---

## Running Verification Tests

Run the full 64-point test suite:
```powershell
python verify_all.py
```
Run PyTest edge-case tests:
```powershell
python -m pytest test_edge_cases.py -v
```
