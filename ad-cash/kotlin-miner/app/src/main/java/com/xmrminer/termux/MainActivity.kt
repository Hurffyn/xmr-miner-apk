package com.xmrminer.termux

import android.os.Bundle
import android.widget.Button
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.io.BufferedReader
import java.io.File
import java.io.InputStreamReader

class MainActivity : AppCompatActivity() {
    private lateinit var logTextView: TextView
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    private var minerProcess: Process? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        logTextView = findViewById(R.id.logTextView)
        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)

        setupPythonEnvironment()

        startButton.setOnClickListener {
            startMining()
        }

        stopButton.setOnClickListener {
            stopMining()
        }
    }

    private fun setupPythonEnvironment() {
        appendLog("Setting up Python environment...")
        
        // Copy Python files from assets to internal storage
        val pythonDir = File(filesDir, "python")
        if (!pythonDir.exists()) {
            pythonDir.mkdirs()
            
            // Copy core modules
            copyAssetFolder("core", File(pythonDir, "core"))
            
            // Copy main scripts
            assets.list("")?.forEach { file ->
                if (file.endsWith(".py")) {
                    copyAssetFile(file, File(pythonDir, file))
                }
            }
            
            appendLog("✓ Python environment ready")
        }
    }

    private fun copyAssetFile(assetPath: String, outFile: File) {
        try {
            assets.open(assetPath).use { input ->
                outFile.outputStream().use { output ->
                    input.copyTo(output)
                }
            }
        } catch (e: Exception) {
            appendLog("Error copying $assetPath: ${e.message}")
        }
    }

    private fun copyAssetFolder(assetFolder: String, outFolder: File) {
        try {
            outFolder.mkdirs()
            assets.list(assetFolder)?.forEach { file ->
                val assetPath = "$assetFolder/$file"
                val outFile = File(outFolder, file)
                
                if (assets.list(assetPath)?.isNotEmpty() == true) {
                    copyAssetFolder(assetPath, outFile)
                } else {
                    copyAssetFile(assetPath, outFile)
                }
            }
        } catch (e: Exception) {
            appendLog("Error copying folder $assetFolder: ${e.message}")
        }
    }

    private fun startMining() {
        appendLog("\n=== Starting XMR Miner ===")
        
        Thread {
            try {
                val pythonDir = File(filesDir, "python")
                val mainScript = File(pythonDir, "miner_android.py")
                
                // Run Python with Termux
                val pb = ProcessBuilder(
                    "/data/data/com.termux/files/usr/bin/python3",
                    mainScript.absolutePath
                )
                pb.directory(pythonDir)
                pb.redirectErrorStream(true)
                
                minerProcess = pb.start()
                
                // Read output
                BufferedReader(InputStreamReader(minerProcess!!.inputStream)).use { reader ->
                    var line: String?
                    while (reader.readLine().also { line = it } != null) {
                        runOnUiThread {
                            appendLog(line!!)
                        }
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    appendLog("Error: ${e.message}")
                    appendLog("Make sure Termux is installed!")
                }
            }
        }.start()
    }

    private fun stopMining() {
        minerProcess?.destroy()
        appendLog("\n=== Miner Stopped ===")
    }

    private fun appendLog(message: String) {
        logTextView.append("$message\n")
        findViewById<ScrollView>(R.id.scrollView).fullScroll(ScrollView.FOCUS_DOWN)
    }
}
