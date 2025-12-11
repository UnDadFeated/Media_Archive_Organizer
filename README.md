# Media Archive Organizer 📸🎬

A robust, high-performance tool to organize your photo and video collections by **Original Creation Date**.

![Icon](Media_Archive_Organizer.UI/app_icon.ico)

## Features
- **Logic 2.0 Engine**:
  - **Smart Deduplication**: Checks MD5 content hashes to skip identifying files and rename name-collisions.
  - **Broad Format Support**: `.jpg`, `.png`, `.heic`, `.mov`, `.mp4` + **RAW** (`.cr2`, `.nef`, `.arw`).
  - **Parallel Processing**: Multi-threaded scanning for blazing speed.
  - **Dry Run Mode**: Simulate the organization before moving a single file.
- **Modern GUI**: Dark-themed WPF interface with real-time logging.
- **Safety**:
  - **Timezone Fix**: Corrects QuickTime UTC dates to Local Time.
  - **Fallback**: Uses 'Date Modified' if Metadata is missing.

## Installation
1.  Download the latest release.
2.  Run `Media_Archive_Organizer.UI.exe`.

## Usage
1.  Select your Source Folder (e.g., your SD card or "Unsorted" folder).
2.  Check **Dry Run** to see what will happen.
3.  Click **Start Organization**.
4.  Files will be moved to `Photos/yyyy-MM` and `Videos/yyyy-MM`.

## Build from Source
**Requirements:** .NET 8 SDK
```powershell
dotnet restore
dotnet build
```
