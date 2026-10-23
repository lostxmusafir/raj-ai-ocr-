# Laser Cut Metal Stencil OCR - Dedicated Backend API Guide

This standalone REST API detects, deskews, binarizes, and recognizes laser-cut metal stencil part codes and centralized agricultural implement codes from uploaded photos.

---

## 🌐 Server Base URL

The backend runs as a standalone Python REST API service:

| Environment | Base URL | Note |
|---|---|---|
| **Local Development** | `http://localhost:5000` | Start server via `run_api.bat` or `python server.py` |
| **Android Emulator** | `http://10.0.2.2:5000` | Android emulator loopback to host PC |
| **Local Network / Production** | `http://<YOUR_SERVER_IP>:5000` | Accessible to mobile phones on WiFi or cloud VPS |

---

## 📌 Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ocr` | Upload photo (file or base64) to detect & recognize stencil code |
| `POST` | `/api/ocr` | Alias for `/ocr` |
| `GET` | `/health` | Health check, service status, and version |
| `GET` | `/catalog` | Implement catalog dictionary & state mappings |

---

## 🚀 1. Recognize Stencil Code (`POST /ocr`)

### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `auto_rotate` | `boolean` | `true` | Automatically checks 0°, 90°, 180°, and 270° orientations to detect vertical or upside-down parts. |
| `include_images` | `boolean` | `false` | Set to `false` for mobile to exclude base64 image strings from response for ultra-fast, lightweight responses (~500 bytes). |

---

### Method A: Multipart Form-Data (File Upload) — Recommended

Upload the image as a binary file in `multipart/form-data`.  
Accepted field names: `file` or `image`.

#### cURL Example:
```bash
curl -X POST "http://localhost:5000/ocr" \
     -F "file=@part_photo.jpg"
```

#### Lightweight Mobile Mode (No base64 images in response):
```bash
curl -X POST "http://localhost:5000/ocr?include_images=false" \
     -F "file=@part_photo.jpg"
```

---

### Method B: JSON Payload (Base64 Encoded Image)

Send a JSON body with the base64-encoded image string.

#### Header:
```http
Content-Type: application/json
```

#### Body:
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...",
  "auto_rotate": true,
  "include_images": false
}
```

---

## 📦 JSON Response Structure

### Success Response (`200 OK`)

```json
{
  "status": "success",
  "final_code": "GJ/142/446/2026/11881/UP",
  "parsed_info": {
    "full_code": "GJ/142/446/2026/11881/UP",
    "is_valid": true,
    "is_document": false,
    "state_code": "GJ",
    "state_name": "Gujarat",
    "mfr_code": "142",
    "model_code": "446",
    "model_info": {
      "name": "TUSKER / SEMI HSS / SEMI CHA",
      "series": "Heavy Duty / Semi Series",
      "sizes": ["5ft", "6ft", "1.65m"]
    },
    "year": "2026",
    "serial_no": "11881",
    "suffix": "UP"
  },
  "best_angle": 180,
  "elapsed_ms": 1150.2,
  "raw_detections": [
    {
      "box": [[120, 45], [450, 45], [450, 80], [120, 80]],
      "score": 0.94,
      "text": "GJ/142/446/2026/11881/UP"
    }
  ]
}
```

### Response Fields Explanation

| Field | Type | Description |
|---|---|---|
| `status` | `string` | `"success"` or `"error"` |
| `final_code` | `string` | The extracted, bridge-repaired, and normalized stencil number. |
| `parsed_info.is_valid` | `boolean` | `true` if code matches the Indian Centralized Implement Code format. |
| `parsed_info.state_code` | `string` | Indian state code (e.g., `GJ`, `MH`, `MP`, `RJ`, `PB`, `HR`, `UP`). |
| `parsed_info.state_name` | `string` | Full state name (e.g., `Gujarat`, `Maharashtra`). |
| `parsed_info.mfr_code` | `string` | Manufacturer registration code (e.g., `142`). |
| `parsed_info.model_code` | `string` | Implement model code (e.g., `444`, `445`, `446`, `447`, `3674`). |
| `parsed_info.model_info` | `object` | Matching catalog data (Implement Model Name, Series Category, Supported Sizes). |
| `parsed_info.year` | `string` | Manufacturing year (e.g., `2026`). |
| `parsed_info.serial_no` | `string` | Serial unit number (e.g., `11881`). |
| `parsed_info.suffix` | `string` | Optional orientation / inspection mark (e.g., `UP`). |
| `best_angle` | `integer` | Rotation applied to detect text (`0`, `90`, `180`, `270`). |
| `elapsed_ms` | `float` | Server processing time in milliseconds. |

---

## 💻 Code Examples for Developers

### 1. Python (`requests`)

```python
import requests

url = "http://localhost:5000/ocr?include_images=false"

# File upload
with open("metal_part.jpg", "rb") as img_file:
    files = {"file": img_file}
    response = requests.post(url, files=files)

data = response.json()
print("Detected Number:", data["final_code"])
print("Is Valid:", data["parsed_info"]["is_valid"])
print("State:", data["parsed_info"]["state_name"])
print("Model:", data["parsed_info"]["model_code"])
print("Processing Time:", data["elapsed_ms"], "ms")
```

---

### 2. JavaScript / Node.js (`fetch`)

```javascript
const fs = require('fs');
const FormData = require('form-data');
const fetch = require('node-fetch');

async function scanPart(imagePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(imagePath));

    const response = await fetch('http://localhost:5000/ocr?include_images=false', {
        method: 'POST',
        body: form
    });

    const result = await response.json();
    console.log("Status:", result.status);
    console.log("Final Code:", result.final_code);
    console.log("Model Info:", result.parsed_info.model_info);
}

scanPart('part_photo.jpg');
```

---

### 3. Android (Kotlin with OkHttp)

```kotlin
val client = OkHttpClient()
val file = File("/path/to/part_photo.jpg")

val requestBody = MultipartBody.Builder()
    .setType(MultipartBody.FORM)
    .addFormDataPart("file", file.name, file.asRequestBody("image/jpeg".toMediaTypeOrNull()))
    .build()

val request = Request.Builder()
    .url("http://10.0.2.2:5000/ocr?include_images=false")
    .post(requestBody)
    .build()

client.newCall(request).enqueue(object : Callback {
    override fun onResponse(call: Call, response: Response) {
        val json = JSONObject(response.body!!.string())
        val finalCode = json.getString("final_code")
        println("Identified Code: $finalCode")
    }
    override fun onFailure(call: Call, e: IOException) {
        e.printStackTrace()
    }
})
```

---

## 🛠️ Running the API Server

1. **Option 1**: Double-click `run_api.bat` in the project root directory.
2. **Option 2**: Run in terminal:
   ```bash
   python server.py
   ```
3. Server will start on `http://0.0.0.0:5000`.
