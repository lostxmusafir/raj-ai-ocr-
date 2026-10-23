package com.raj.ocr.sdk

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Internal Retrofit & OkHttp client manager for the OCR SDK.
 */
object RetrofitClient {

    // Default URL: Android emulator localhost (10.0.2.2:5000) or update via OcrSdk.setServerUrl()
    const val DEFAULT_BASE_URL = "http://10.0.2.2:5000/"

    private var currentBaseUrl: String = DEFAULT_BASE_URL
    private var cachedService: OcrApiService? = null

    /**
     * Configure a custom backend URL (e.g. "http://192.168.1.100:5000/" for local development).
     */
    fun setBaseUrl(url: String) {
        val normalized = if (url.endsWith("/")) url else "$url/"
        if (normalized != currentBaseUrl) {
            currentBaseUrl = normalized
            cachedService = null
        }
    }

    private val okHttpClient: OkHttpClient by lazy {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.HEADERS
        }

        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .addInterceptor(logging)
            .retryOnConnectionFailure(true)
            .build()
    }

    val apiService: OcrApiService
        get() {
            if (cachedService == null) {
                cachedService = Retrofit.Builder()
                    .baseUrl(currentBaseUrl)
                    .client(okHttpClient)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build()
                    .create(OcrApiService::class.java)
            }
            return cachedService!!
        }
}
