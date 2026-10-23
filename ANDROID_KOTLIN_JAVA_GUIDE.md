# Android Mobile Developer Integration Guide (Kotlin & Java)

## 📌 API Details
- **Endpoint**: `http://<YOUR_SERVER_IP>:5000/ocr` (or `http://10.0.2.2:5000/ocr` for Android Emulator)
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Form Field**: `file` (File format: JPG, JPEG, PNG, WEBP)
- **Recommended Query Parameter for Mobile**: `?include_images=false`  
  *(Saves mobile data & memory by returning only the detected text, state, model, and serial number without huge base64 image strings. If you want the White-on-Black visual badge, leave it out or set `include_images=true`)*.

---

## 🏗️ 1. Kotlin Implementation (Retrofit + Coroutines)

### A. Dependencies (`build.gradle.kts` or `build.gradle`)
```kotlin
dependencies {
    // Retrofit & OkHttp
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.squareup.retrofit2:converter-gson:2.11.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
}
```

### B. Response Data Classes (`OcrModels.kt`)
```kotlin
package com.example.ocr.model

import com.google.gson.annotations.SerializedName

data class OcrResponse(
    @SerializedName("status") val status: String,
    @SerializedName("final_code") val finalCode: String?,
    @SerializedName("parsed_info") val parsedInfo: ParsedInfo?,
    @SerializedName("best_angle") val bestAngle: Int,
    @SerializedName("elapsed_ms") val elapsedMs: Double,
    @SerializedName("cropped_binary_base64") val croppedBinaryBase64: String?,
    @SerializedName("digital_stamp_base64") val digitalStampBase64: String?
)

data class ParsedInfo(
    @SerializedName("full_code") val fullCode: String?,
    @SerializedName("is_valid") val isValid: Boolean,
    @SerializedName("is_document") val isDocument: Boolean,
    @SerializedName("state_code") val stateCode: String?,
    @SerializedName("state_name") val stateName: String?,
    @SerializedName("mfr_code") val mfrCode: String?,
    @SerializedName("model_code") val modelCode: String?,
    @SerializedName("model_info") val modelInfo: ModelInfo?,
    @SerializedName("year") val year: String?,
    @SerializedName("serial_no") val serialNo: String?,
    @SerializedName("suffix") val suffix: String?
)

data class ModelInfo(
    @SerializedName("name") val name: String?,
    @SerializedName("series") val series: String?,
    @SerializedName("sizes") val sizes: List<String>?
)
```

### C. Retrofit Service Interface (`OcrApiService.kt`)
```kotlin
package com.example.ocr.network

import com.example.ocr.model.OcrResponse
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Query

interface OcrApiService {

    @Multipart
    @POST("api/ocr")
    suspend fun scanStencilImage(
        @Part file: MultipartBody.Part,
        @Query("include_images") includeImages: Boolean = false,
        @Query("auto_rotate") autoRotate: Boolean = true
    ): Response<OcrResponse>
}
```

### D. API Client Singleton (`RetrofitClient.kt`)
```kotlin
package com.example.ocr.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    // Use your backend server IP or 10.0.2.2:5000 for Android emulator
    private const val BASE_URL = "http://10.0.2.2:5000/"

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        })
        .build()

    val apiService: OcrApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(OcrApiService::class.java)
    }
}
```

### E. Calling API from ViewModel or Activity (Kotlin)
```kotlin
import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.ocr.network.RetrofitClient
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.FileOutputStream

class OcrViewModel : ViewModel() {

    fun uploadCapturedImage(imageFile: File, onResult: (String, Boolean) -> Unit) {
        viewModelScope.launch {
            try {
                // Prepare multipart request
                val requestBody = imageFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
                val part = MultipartBody.Part.createFormData("file", imageFile.name, requestBody)

                // Call API
                val response = RetrofitClient.apiService.scanStencilImage(
                    file = part,
                    includeImages = false // set true if you want base64 badges
                )

                if (response.isSuccessful && response.body() != null) {
                    val result = response.body()!!
                    val detectedCode = result.finalCode ?: "No code detected"
                    val isValid = result.parsedInfo?.isValid ?: false
                    onResult(detectedCode, isValid)
                } else {
                    onResult("Error: ${response.code()} ${response.message()}", false)
                }
            } catch (e: Exception) {
                onResult("Network Error: ${e.localizedMessage}", false)
            }
        }
    }

    // Helper: Convert Camera Uri to File for upload
    fun getFileFromUri(context: Context, uri: Uri): File {
        val tempFile = File(context.cacheDir, "camera_upload.jpg")
        context.contentResolver.openInputStream(uri)?.use { input ->
            FileOutputStream(tempFile).use { output ->
                input.copyTo(output)
            }
        }
        return tempFile
    }
}
```

---

## ☕ 2. Java Implementation (Retrofit or OkHttp)

### A. Java POJO Models (`OcrResponse.java`)
```java
package com.example.ocr.model;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class OcrResponse {
    @SerializedName("status")
    public String status;

    @SerializedName("final_code")
    public String finalCode;

    @SerializedName("parsed_info")
    public ParsedInfo parsedInfo;

    @SerializedName("best_angle")
    public int bestAngle;

    @SerializedName("elapsed_ms")
    public double elapsedMs;

    public static class ParsedInfo {
        @SerializedName("full_code")
        public String fullCode;

        @SerializedName("is_valid")
        public boolean isValid;

        @SerializedName("state_code")
        public String stateCode;

        @SerializedName("state_name")
        public String stateName;

        @SerializedName("mfr_code")
        public String mfrCode;

        @SerializedName("model_code")
        public String modelCode;

        @SerializedName("year")
        public String year;

        @SerializedName("serial_no")
        public String serialNo;

        @SerializedName("suffix")
        public String suffix;

        @SerializedName("model_info")
        public ModelInfo modelInfo;
    }

    public static class ModelInfo {
        @SerializedName("name")
        public String name;

        @SerializedName("series")
        public String series;

        @SerializedName("sizes")
        public List<String> sizes;
    }
}
```

### B. Java Retrofit Interface (`OcrApiInterface.java`)
```java
package com.example.ocr.network;

import com.example.ocr.model.OcrResponse;
import okhttp3.MultipartBody;
import retrofit2.Call;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Query;

public interface OcrApiInterface {

    @Multipart
    @POST("api/ocr")
    Call<OcrResponse> uploadImage(
        @Part MultipartBody.Part file,
        @Query("include_images") boolean includeImages
    );
}
```

### C. Direct Java Upload with OkHttp (`OcrUploader.java`)
```java
package com.example.ocr;

import com.example.ocr.model.OcrResponse;
import com.google.gson.Gson;
import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class OcrUploader {

    // Replace with your server IP (e.g. 10.0.2.2:5000 for emulator or 192.168.1.X:5000 for local network)
    private static final String API_URL = "http://10.0.2.2:5000/ocr?include_images=false";
    private final OkHttpClient client;
    private final Gson gson;

    public interface OcrCallback {
        void onSuccess(OcrResponse response);
        void onError(String errorMessage);
    }

    public OcrUploader() {
        this.client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
                .build();
        this.gson = new Gson();
    }

    public void scanPartImage(File imageFile, OcrCallback callback) {
        RequestBody fileBody = RequestBody.create(
                MediaType.parse("image/jpeg"),
                imageFile
        );

        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", imageFile.getName(), fileBody)
                .build();

        Request request = new Request.Builder()
                .url(API_URL)
                .post(requestBody)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                callback.onError("Connection failure: " + e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
                    callback.onError("Server returned error: HTTP " + response.code());
                    return;
                }

                String responseBody = response.body().string();
                OcrResponse ocrResponse = gson.fromJson(responseBody, OcrResponse.class);
                callback.onSuccess(ocrResponse);
            }
        });
    }
}
```

---

## 📱 Mobile Best Practices (For Best OCR Accuracy)

1. **High Resolution**: Ensure camera captures at least 1080p (1920x1080).
2. **Flash / Lighting**: In dark factory environments, turning on the mobile torch (`FLASH_MODE_TORCH`) will remove harsh metal shadows and eliminate misread digits.
3. **Auto-Rotate**: The server already detects parts rotated at 0°, 90°, 180°, and 270° automatically.
4. **Bandwidth Optimization**: Set `include_images=false` when calling from mobile networks to reduce payload size from ~1.5MB to just ~500 bytes.
