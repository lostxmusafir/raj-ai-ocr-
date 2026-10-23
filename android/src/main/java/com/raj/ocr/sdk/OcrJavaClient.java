package com.raj.ocr.sdk;

import android.content.Context;
import android.net.Uri;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Java-friendly client for scanning laser-cut stencil codes.
 */
public class OcrJavaClient {

    /**
     * Configure custom backend URL if running locally.
     */
    public static void setServerUrl(String url) {
        RetrofitClient.INSTANCE.setBaseUrl(url);
    }

    /**
     * Asynchronously scans an image file.
     *
     * @param imageFile The image file from storage or camera.
     * @param callback Result callback.
     */
    public static void scan(File imageFile, final OcrCallback callback) {
        scan(imageFile, false, callback);
    }

    /**
     * Asynchronously scans an image file with optional base64 image inclusion.
     */
    public static void scan(File imageFile, boolean includeImages, final OcrCallback callback) {
        RequestBody reqFile = RequestBody.create(
                MediaType.parse("image/jpeg"),
                imageFile
        );
        MultipartBody.Part body = MultipartBody.Part.createFormData("file", imageFile.getName(), reqFile);

        Call<OcrResponse> call = RetrofitClient.INSTANCE.getApiService().scanImageCall(body, includeImages, true);
        call.enqueue(new Callback<OcrResponse>() {
            @Override
            public void onResponse(Call<OcrResponse> call, Response<OcrResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    OcrResponse res = response.body();
                    if ("success".equalsIgnoreCase(res.getStatus())) {
                        callback.onSuccess(res);
                    } else {
                        callback.onError(new Exception("OCR Status: " + res.getStatus()));
                    }
                } else {
                    callback.onError(new Exception("HTTP Error: " + response.code() + " " + response.message()));
                }
            }

            @Override
            public void onFailure(Call<OcrResponse> call, Throwable t) {
                callback.onError(t);
            }
        });
    }

    /**
     * Scans an image from an Android content Uri (e.g. from camera capture).
     */
    public static void scan(Context context, Uri imageUri, final OcrCallback callback) {
        try {
            File tempFile = File.createTempFile("java_ocr_", ".jpg", context.getCacheDir());
            InputStream in = context.getContentResolver().openInputStream(imageUri);
            if (in == null) {
                callback.onError(new Exception("Failed to open image URI"));
                return;
            }
            FileOutputStream out = new FileOutputStream(tempFile);
            byte[] buf = new byte[8192];
            int len;
            while ((len = in.read(buf)) > 0) {
                out.write(buf, 0, len);
            }
            in.close();
            out.close();

            scan(tempFile, false, callback);
        } catch (Exception e) {
            callback.onError(e);
        }
    }
}
