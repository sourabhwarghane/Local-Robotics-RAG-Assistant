# Robotics RAG Hardware Documentation Downloader

This package is for the **Local RAG / Robotics Knowledge Assistant** project on Windows.

## What it downloads

| Hardware | Source | File type | RAG priority |
|---|---|---:|---:|
| SLAMTEC RPLIDAR C1 / C1M1 | SLAMTEC | Datasheet PDF + Dev Kit Manual PDF | High |
| NVIDIA Jetson Orin Nano / Super Dev Kit | NVIDIA | Carrier Board PDF + current User Guide HTML | High |
| ESP32-C3 | Espressif | Datasheet PDF + Hardware Design Guidelines PDF | High |
| Waveshare IMX219-120 | Waveshare | Product/Wiki documentation HTML | High |
| BTS7960 | Infineon | IC datasheet PDF | Medium |
| Generic USB mic / low-cost BT speaker | Your own AMR notes | No arbitrary vendor manual | Low |

## How to use

1. Copy `download_hardware_docs.ps1` into the root of your project:

```text
Local_RAG_Robotics_Assistant/
    download_hardware_docs.ps1
    data/
    src/
    ...
```

2. Open PowerShell in that project folder.

3. If Windows blocks local scripts for the current session, run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

4. Run:

```powershell
.\download_hardware_docs.ps1
```

It will create/download into:

```text
data/raw/
├── sensors/
│   ├── rplidar_c1/
│   └── imx219_120/
├── jetson/
├── esp32_c3/
├── motor_driver/
│   └── bts7960/
└── audio/
```

## Why there is no microphone / fake JBL manual

Those inexpensive generic devices do not have a trustworthy hardware identity. Indexing a random microphone or JBL manual would teach the RAG system facts that may not apply to your actual device. Your own AMR audio/STT/TTS documentation is a better source.

## Important next step

Your current `document_loader.py` handles PDF/DOCX. NVIDIA's current Super Developer Kit guide and Waveshare's IMX219-120 guide are maintained online, so the script saves them as HTML. Before ingestion, add HTML support to the loader (we can do this in the next step).
