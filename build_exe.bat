@echo off
echo Building Media Archive Organizer v2.8.1...
py -3.11 -m PyInstaller --noconfirm --onefile --windowed --name "MediaArchiveOrganizer_v2.8.1" --icon "src/assets/icon.ico" --hidden-import=piexif --collect-all mediapipe --collect-all customtkinter --add-data "src;src" launcher.py
echo Build Complete. EXE is in dist/
