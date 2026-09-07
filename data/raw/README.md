# Data

This folder contains the source documents used to build the knowledge base for the Local Robotics RAG Assistant.

## Folder Structure

```text
data/
└── raw/
    ├── amr/
    ├── ros2/
    ├── sensors/
    ├── jetson/
    ├── esp32_c3/
    ├── motor_driver/
    └── audio/
```

## Knowledge Base

The project uses documentation related to:

* My Autonomous Mobile Robot (AMR)
* ROS 2 Humble
* NVIDIA Jetson Orin Nano
* SLAMTEC RPLIDAR C1
* ESP32-C3
* IMX219 camera
* BTS7960 motor driver
* Audio hardware

Supported document formats include:

```text
.pdf
.docx
.txt
.rst
.html
.htm
```

## Adding Documents

Place documents in the appropriate category inside `data/raw/`.

For example:

```text
data/raw/sensors/RPLIDAR_C1_Datasheet.pdf
data/raw/ros2/ROS2_Humble_QoS_Settings.rst
data/raw/amr/AMR_Project_Documentation.docx
```

Then rebuild the knowledge base:

```bash
python ingest.py
```

The ingestion pipeline will:

```text
Documents
→ Text Extraction
→ Chunking
→ Embeddings
→ FAISS Vector Index
```

Generated retrieval files are stored separately in:

```text
vector_db/
```

## Note on Third-Party Documentation

Some documents used during development are official documentation or datasheets published by third-party vendors and organizations.

These files may not be included directly in this repository due to redistribution/licensing considerations.

Users can download the relevant documentation from the official sources and place it in the appropriate `data/raw/` folder before running the ingestion pipeline.

My own AMR documentation can be included directly in the repository.
