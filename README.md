# Media Archive Organizer (v2.5.4)

**Automated Media Organization & AI Cleanup Tool**



## Overview
Media Archive Organizer is a powerful tool designed to help you organize chaos.
It sorts your photos and videos into a structured `Year/Year-Month` format and uses **AI Scan** to separate family photos from landscapes, documents, and memes.

**Developer**: [Undadfeated](https://github.com/Undadfeated)
**Language**: Python (v2.5.4 Update)

## New Features (v2.5.4)
- **Hotfix**:
  - Fixed a `NameError` crash when using the "Move Files" button in the AI Scanner tab (missing import).

## New Features (v2.5.3)
- **Bug Fixes**:
  - **Fixed File Move**: Resolved an issue where files wouldn't move from the AI Scanner tab because they were "locked" by the preview window.
  - **Performance**: Drastically improved UI responsiveness when clicking through large photos (now loads optimized thumbnails instead of full-res images).

## New Features (v2.5.2)
- **Smart Filename Parsing**:
  - The app now automatically grabs dates from filenames (e.g., `IMG_20230101.jpg`, `VID-20221225.mp4`, `Signal-2024-05-10.jpg`) if EXIF metadata is missing.
  - This significantly improves accuracy for downloaded media, WhatsApp/Signal images, and screenshots, preventing them from being sorted into "Today's" folder.

## New Features (v2.5.1)
- **Smart Date Correction**:
  - The tool now intelligently **corrects** filenames that have incorrect date prefixes (e.g., from previous incorrect scans or manual errors).
  - If a file starts with `YYYY-MM-DD_` but the date is wrong, it will be stripped and replaced with the correct date from the metadata.

## New Features (v2.5.0)
- **Flexible Organization**:
  - **Flat Folder Option**: Choose between nested `YYYY/YYYY-MM/` or flat `YYYY-MM/` folder formatting.
  - **Smart Renaming**: Files are automatically prefixed with `YYYY-MM-DD_` for chronological sorting within folders.
- **Enhanced Scanning**:
  - **Video Metadata**: Improved date extraction for `.mp4`, `.mov`, and `.webm` files (keeps native dates or falls back to modified time).
- **Enhanced Logging**:
  - **Persistent Log File**: Now saves a `media_organizer.log` file in the same directory, even during Dry Runs.
  - **Detailed Tracking**: Logs timestamped "Old -> New" file paths for every action.
- **UI Logic**:
  - **Realtime Logging**: Added optional log window on the dashboard to see files being processed in realtime.
  - **Status Updates**: Improved progress status to show the exact file being worked on.
- **UI Polish**:
  - **Cleaner Look**: Removed grip arrow and optimized checkbox layout.
- **UI Polish**:
  - **Refined Grip**: Moved resize grip to the true corner for a cleaner look.
- **Maintenance**: Removed legacy MediaPipe Face detection code.
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

### 2. AI Scanner Tab
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
