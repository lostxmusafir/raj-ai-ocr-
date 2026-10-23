package com.raj.ocr.sdk

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream

/**
 * High-level, developer-friendly SDK for scanning laser-cut metal stencil codes.
 */
object OcrSdk {

    /**
     * Configure backend server URL.
     * Default: http://10.0.2.2:5000/ (Android Emulator to Host PC)
     * For real phone on local WiFi, use: http://<YOUR_PC_IP>:5000/
     */
    fun setServerUrl(url: String) {
        RetrofitClient.setBaseUrl(url)
    }

    /**
     * Scan a sheet metal part image file using Kotlin Coroutines.
     *
     * @param imageFile The JPEG or PNG image file captured by camera or gallery.
     * @param includeImages Whether to return base64 white-on-black binarized images (default: false).
     * @return Result containing [OcrResponse] on success or an [Exception] on failure.
     */
    suspend fun scan(
        imageFile: File,
        includeImages: Boolean = false
    ): Result<OcrResponse> = withContext(Dispatchers.IO) {
        try {
            // Optimize image if larger than 2MB before upload
            val fileToUpload = if (imageFile.length() > 2 * 1024 * 1024) {
                compressImageFile(imageFile)
            } else {
                imageFile
            }

            val requestBody = fileToUpload.asRequestBody("image/jpeg".toMediaTypeOrNull())
            val part = MultipartBody.Part.createFormData("file", fileToUpload.name, requestBody)

            val response = RetrofitClient.apiService.scanImage(
                file = part,
                includeImages = includeImages,
                autoRotate = true
            )

            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                if (body.status == "success") {
                    Result.success(body)
                } else {
                    Result.failure(Exception("OCR processing failed: ${body.status}"))
                }
            } else {
                val errorMsg = response.errorBody()?.string() ?: response.message()
                Result.failure(Exception("Server returned HTTP ${response.code()}: $errorMsg"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Convenience method to scan an Android content Uri (e.g. from CameraX or Photo Picker).
     */
    suspend fun scan(
        context: Context,
        imageUri: Uri,
        includeImages: Boolean = false
    ): Result<OcrResponse> = withContext(Dispatchers.IO) {
        try {
            val tempFile = copyUriToTempFile(context, imageUri)
            scan(tempFile, includeImages)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Helper: Copy content URI to a temporary file
    private fun copyUriToTempFile(context: Context, uri: Uri): File {
        val tempFile = File.createTempFile("ocr_scan_", ".jpg", context.cacheDir)
        context.contentResolver.openInputStream(uri)?.use { input ->
            FileOutputStream(tempFile).use { output ->
                input.copyTo(output)
            }
        }
        return tempFile
    }

    // Helper: Downscale high-resolution phone camera photos to ~1920px max dimension
    private fun compressImageFile(originalFile: File): File {
        val boundsOptions = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeFile(originalFile.absolutePath, boundsOptions)

        val maxDim = 1920
        var sampleSize = 1
        while (boundsOptions.outWidth / sampleSize > maxDim || boundsOptions.outHeight / sampleSize > maxDim) {
            sampleSize *= 2
        }

        val decodeOptions = BitmapFactory.Options().apply { inSampleSize = sampleSize }
        val bitmap = BitmapFactory.decodeFile(originalFile.absolutePath, decodeOptions) ?: return originalFile

        val compressedFile = File.createTempFile("compressed_", ".jpg", originalFile.parentFile)
        FileOutputStream(compressedFile).use { out ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 85, out)
        }
        return compressedFile
    }
}
