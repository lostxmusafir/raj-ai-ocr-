package com.raj.ocr.sdk

import com.google.gson.annotations.SerializedName

/**
 * Top-level response returned by the Laser Stencil OCR Backend.
 */
data class OcrResponse(
    @SerializedName("status")
    val status: String,

    @SerializedName("final_code")
    val finalCode: String?,

    @SerializedName("parsed_info")
    val parsedInfo: ParsedInfo?,

    @SerializedName("best_angle")
    val bestAngle: Int = 0,

    @SerializedName("elapsed_ms")
    val elapsedMs: Double = 0.0,

    @SerializedName("cropped_binary_base64")
    val croppedBinaryBase64: String? = null,

    @SerializedName("digital_stamp_base64")
    val digitalStampBase64: String? = null,

    @SerializedName("raw_detections")
    val rawDetections: List<RawDetection>? = null
)

/**
 * Semantic breakdown of the Indian Centralized Implement Code:
 * Format: State / Manufacturer / Model / Year / Serial [/ Suffix]
 */
data class ParsedInfo(
    @SerializedName("full_code")
    val fullCode: String?,

    @SerializedName("is_valid")
    val isValid: Boolean = false,

    @SerializedName("is_document")
    val isDocument: Boolean = false,

    @SerializedName("state_code")
    val stateCode: String?,

    @SerializedName("state_name")
    val stateName: String?,

    @SerializedName("mfr_code")
    val mfrCode: String?,

    @SerializedName("model_code")
    val modelCode: String?,

    @SerializedName("model_info")
    val modelInfo: ModelInfo?,

    @SerializedName("year")
    val year: String?,

    @SerializedName("serial_no")
    val serialNo: String?,

    @SerializedName("suffix")
    val suffix: String?
)

/**
 * Catalog details matched from the implement specification database.
 */
data class ModelInfo(
    @SerializedName("name")
    val name: String?,

    @SerializedName("series")
    val series: String?,

    @SerializedName("sizes")
    val sizes: List<String>?
)

/**
 * Raw text polygon bounding box detection from the vision model.
 */
data class RawDetection(
    @SerializedName("text")
    val text: String,

    @SerializedName("score")
    val score: Double,

    @SerializedName("box")
    val box: List<List<Float>>
)
