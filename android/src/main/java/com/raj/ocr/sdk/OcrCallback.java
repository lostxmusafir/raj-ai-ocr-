package com.raj.ocr.sdk;

/**
 * Callback interface for asynchronous OCR scan requests in Java.
 */
public interface OcrCallback {

    /**
     * Called when the image was successfully analyzed by the backend.
     *
     * @param response Complete parsed OCR response including final code and model breakdown.
     */
    void onSuccess(OcrResponse response);

    /**
     * Called when a network or processing error occurred.
     *
     * @param error The exception describing the error.
     */
    void onError(Throwable error);
}
