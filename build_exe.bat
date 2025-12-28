@echo off
echo Building Media Archive Organizer v2.2...
py -3.11 -m PyInstaller --noconfirm --onefile --windowed --name "MediaArchiveOrganizer_v2.2" --hidden-import=piexif --collect-all mediapipe --collect-all customtkinter --add-data "src;src" launcher.py
echo Build Complete. EXE is in dist/
pause
