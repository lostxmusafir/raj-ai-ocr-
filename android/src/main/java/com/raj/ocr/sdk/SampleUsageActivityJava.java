package com.raj.ocr.sdk;

import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

/**
 * Example Android Activity demonstrating how to use OcrJavaClient in Java.
 */
public class SampleUsageActivityJava extends AppCompatActivity {

    private TextView tvResult;
    private Button btnPickImage;

    private final ActivityResultLauncher<String> pickMedia = registerForActivityResult(
            new ActivityResultContracts.GetContent(),
            uri -> {
                if (uri != null) {
                    scanImageUri(uri);
                }
            }
    );

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (btnPickImage != null) {
            btnPickImage.setOnClickListener(v -> pickMedia.launch("image/*"));
        }
    }

    private void scanImageUri(Uri imageUri) {
        if (tvResult != null) {
            tvResult.setText("Scanning laser cut code in Java...");
        }

        OcrJavaClient.scan(this, imageUri, new OcrCallback() {
            @Override
            public void onSuccess(OcrResponse response) {
                runOnUiThread(() -> {
                    String code = response.getFinalCode();
                    String state = response.getParsedInfo() != null ? response.getParsedInfo().getStateName() : "";
                    String model = response.getParsedInfo() != null ? response.getParsedInfo().getModelCode() : "";

                    if (tvResult != null) {
                        tvResult.setText("Code: " + code + "\nState: " + state + "\nModel: " + model);
                    }
                });
            }

            @Override
            public void onError(Throwable error) {
                runOnUiThread(() -> {
                    if (tvResult != null) {
                        tvResult.setText("Error: " + error.getMessage());
                    }
                    Toast.makeText(SampleUsageActivityJava.this, error.getMessage(), Toast.LENGTH_LONG).show();
                });
            }
        });
    }
}
