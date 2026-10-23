package com.raj.ocr.sdk

import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Query

/**
 * Retrofit interface for communicating with the Laser Stencil OCR Backend.
 */
interface OcrApiService {

    /**
     * Upload an image of a sheet metal part to detect and recognize laser-cut stencil code.
     *
     * @param file Multipart file part containing the JPEG/PNG image.
     * @param includeImages If false (default), excludes heavy base64 images from JSON to save mobile bandwidth.
     * @param autoRotate If true (default), automatically checks 0°, 90°, 180°, and 270° orientations.
     */
    @Multipart
    @POST("ocr")
    suspend fun scanImage(
        @Part file: MultipartBody.Part,
        @Query("include_images") includeImages: Boolean = false,
        @Query("auto_rotate") autoRotate: Boolean = true
    ): Response<OcrResponse>

    /**
     * Java / Call-based version for non-coroutine usage.
     */
    @Multipart
    @POST("ocr")
    fun scanImageCall(
        @Part file: MultipartBody.Part,
        @Query("include_images") includeImages: Boolean = false,
        @Query("auto_rotate") autoRotate: Boolean = true
    ): retrofit2.Call<OcrResponse>
}
