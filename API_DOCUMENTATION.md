# Laser Cut Metal Stencil OCR - Developer API Guide

This API detects, deskews, binarizes, and recognizes laser-cut metal stencil part codes and centralized agricultural implement codes from uploaded photos.

---

## 🌐 Base URLs

| Environment | Base URL | Note |
|---|---|---|
| **Live Cloud Production (Vercel)** | `https://raj-ai-ocr.vercel.app` | Hosted on Vercel Serverless (Ready to use immediately) |
| **Local Development Server** | `http://localhost:5000` | Start locally by double-clicking `run_api.bat` |

---

## 📌 Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ocr` | Upload photo (file or base64) to detect & recognize stencil code |
| `GET` | `/api/health` | Health check, API version, and supported model lists |
| `GET` | `/api/catalog` | Get centralized implement catalog dictionary & state mappings |

---

## 🚀 1. Recognize Stencil Code (`POST /api/ocr`)

### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `auto_rotate` | `boolean` | `true` | Automatically checks 0°, 90°, 180°, and 270° orientations to detect vertical or upside-down parts. |
| `include_images` | `boolean` | `true` | Set to `false` to exclude base64 image strings from response for ultra-fast and lightweight responses (~500 bytes). |

---

### Method A: Multipart Form-Data (File Upload) — Recommended

Upload the image as a binary file in `multipart/form-data`.  
Accepted field names: `file` or `image`.

#### cURL Example:
```bash
curl -X POST "https://raj-ai-ocr.vercel.app/api/ocr" \
     -F "file=@part_photo.jpg"
```

#### Lightweight Mode (No base64 images in response):
```bash
curl -X POST "https://raj-ai-ocr.vercel.app/api/ocr?include_images=false" \
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
  "include_images": true
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
  ],
  "cropped_binary_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "digital_stamp_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "annotated_image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
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
| `cropped_binary_base64` | `string` | **High-contrast cutout** showing extracted numbers in **Pure White text on Pure Black background**. |
| `digital_stamp_base64` | `string` | Ready-to-print synthetic digital badge card (White on Black). |

---

## 💻 Code Examples for Developers

### 1. Python (`requests`)

```python
import requests

url = "https://raj-ai-ocr.vercel.app/api/ocr"

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

    const response = await fetch('https://raj-ai-ocr.vercel.app/api/ocr', {
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

### 3. Frontend Web (Browser HTML & JavaScript)

```html
<input type="file" id="imageInput" accept="image/*">
<button onclick="uploadImage()">Scan Number</button>
<p id="resultDisplay" style="font-size: 24px; font-weight: bold; background: #000; color: #fff; padding: 12px;"></p>

<script>
async function uploadImage() {
    const fileInput = document.getElementById('imageInput');
    if (!fileInput.files.length) return alert('Select an image first!');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const res = await fetch('https://raj-ai-ocr.vercel.app/api/ocr', {
        method: 'POST',
        body: formData
    });

    const data = await res.json();
    document.getElementById('resultDisplay').innerText = data.final_code || 'No code detected';
}
</script>
```

---

### 4. Android (Java / Kotlin with OkHttp)

```kotlin
val client = OkHttpClient()
val file = File("/path/to/part_photo.jpg")

val requestBody = MultipartBody.Builder()
    .setType(MultipartBody.FORM)
    .addFormDataPart("file", file.name, file.asRequestBody("image/jpeg".toMediaTypeOrNull()))
    .build()

val request = Request.Builder()
    .url("https://raj-ai-ocr.vercel.app/api/ocr")
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

### 5. Flutter / Dart

```dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> scanImage(File imageFile) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('https://raj-ai-ocr.vercel.app/api/ocr'),
  );
  request.files.add(await http.MultipartFile.fromPath('file', imageFile.path));

  var streamedResponse = await request.send();
  var response = await http.Response.fromStream(streamedResponse);

  if (response.statusCode == 200) {
    var data = jsonDecode(response.body);
    print("Detected Code: ${data['final_code']}");
  }
}
```

---

## 🛠️ Running API Locally

To run the API on your local computer or on a local network server:
1. Double-click `run_api.bat` in the project root directory.
2. The server will start on `http://localhost:5000`.
3. Other devices on the same local Wi-Fi / network can call it via:
   `http://<YOUR_LOCAL_IP>:5000/api/ocr`
