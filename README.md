# Media Archive Organizer (v2.1)

**Automated Media Organization & AI Cleanup Tool**



## Overview
Media Archive Organizer is a powerful tool designed to help you organize chaos.
It sorts your photos and videos into a structured `Year/Year-Month` format and uses **AI Face Detection** to separate family photos from landscapes, documents, and memes.

**Developer**: [Undadfeated](https://github.com/Undadfeated)
**Language**: Python (v2.0 Rewrite)

## New Features (v2.1)
- **AI Object Scanning**:
  - **No People**: Automatically identify photos *without* people (Landscapes, Objects).
  - **Keep Animals**: Option to keep photos of pets (Cats, Dogs, etc.) in the "No People" list using object detection.
- **High Performance**:
  - **Multi-threaded Logic**: Parallel image loading for maximum SSD/HDD throughput.
  - **GPU Acceleration**: OpenCL support for compatible cards via OpenCV.
- **Privacy First**: All processing is done **Locally** on your device. No cloud uploads.

## Usage

### 1. Organizer Tab
- **Source Folder**: Select your messy folder.
- **Mode**: Choose "Photos", "Videos", or both.
- **Dry Run**: Preview changes before moving any files.
- **Start**: Sorts files into `YYYY\YYYY-MM` folders based on EXIF/Metadata.

### 2. AI Face Scanner Tab
- **Goal**: Separate "Good Shots" (Landscapes/Art) from "People Shots" (Privacy/Personal).
- **Keep Animals**: 
  - **Checked**: Pets are excluded along with people.
  - **Unchecked**: Pets stay in your "No People" (Keep) list.
- **Start Scan**: Runs the AI.
- **Review**: Check the lists, verify previews.
- **Move Files**: Moves the "No People" files to a `No_People` subfolder for easy archiving.

## Installation
No installation required. Just run the standalone executable.

1. Go to **Releases**.
2. Download `MediaArchiveOrganizer_v2.exe`.
3. Run it.

> **Note on File Size (~87MB)**: The executable is large because it is a fully standalone app. It bundles the entire **Python 3.11 Runtime**, **OpenCV**, **MediaPipe (TensorFlow Lite)**, and the **AI Models** inside a single file. You do not need to install Python or any dependencies to run it.

## For Developers (Building from Source)
Requirements: Python 3.11+
```bash
pip install -r requirements.txt
python launcher.py
```

### Build Executable
```bash
build_exe.bat
```

## Credits
- **MediaPipe** (Google) for AI models.
- **OpenCV** for image processing.
- **CustomTkinter** for the UI.

---
*Coffee is always appreciated!* ☕
