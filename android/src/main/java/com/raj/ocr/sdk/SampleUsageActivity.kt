package com.raj.ocr.sdk

import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

/**
 * Example Android Activity demonstrating how to use OcrSdk in Kotlin.
 */
class SampleUsageActivity : AppCompatActivity() {

    private lateinit var tvResult: TextView
    private lateinit var btnPickImage: Button

    // Photo picker launcher
    private val pickMedia = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { scanImageUri(it) }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Set up views programmatically or from layout
        btnPickImage.setOnClickListener {
            pickMedia.launch("image/*")
        }
    }

    private fun scanImageUri(imageUri: Uri) {
        tvResult.text = "Scanning laser cut code..."

        lifecycleScope.launch {
            val result = OcrSdk.scan(this@SampleUsageActivity, imageUri)

            result.onSuccess { response ->
                val detectedCode = response.finalCode ?: "No code found"
                val modelName = response.parsedInfo?.modelInfo?.name ?: "Unknown Model"
                val state = response.parsedInfo?.stateName ?: "Unknown State"

                tvResult.text = """
                    Identified Code: $detectedCode
                    State: $state
                    Model: $modelName
                    Year: ${response.parsedInfo?.year}
                    Serial: ${response.parsedInfo?.serialNo}
                    Scan Time: ${response.elapsedMs} ms
                """.trimIndent()
            }.onFailure { error ->
                tvResult.text = "Error: ${error.localizedMessage}"
                Toast.makeText(this@SampleUsageActivity, error.message, Toast.LENGTH_LONG).show()
            }
        }
    }
}
