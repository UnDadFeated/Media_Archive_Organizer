import os
import shutil
import hashlib
from datetime import datetime
from typing import List, Callable, Optional
import piexif

class OrganizerEngine:
    def __init__(self, logger_callback: Optional[Callable[[str], None]] = None):
        self.logger = logger_callback or (lambda x: print(x))

    def get_date_taken(self, file_path: str) -> Optional[datetime]:
        """
        Extract date taken from EXIF or fallback to file modified time.
        """
        try:
            # 1. Try Piexif
            exif_dict = piexif.load(file_path)
            # DateTimeOriginal is 36867
            if 36867 in exif_dict.get("Exif", {}):
                date_str = exif_dict["Exif"][36867].decode("utf-8")
                # Format is usually "YYYY:MM:DD HH:MM:SS"
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            
            # DateTimeDigitized is 36868
            if 36868 in exif_dict.get("Exif", {}):
                date_str = exif_dict["Exif"][36868].decode("utf-8")
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")

        except Exception:
            pass
            
        # Fallback to file creation/modification
        try:
            return datetime.fromtimestamp(os.path.getmtime(file_path))
        except:
            return None

    def organize(self, source_dir: str, dry_run: bool = True):
        if not os.path.exists(source_dir):
            self.logger("Source directory does not exist.")
            return

        self.logger(f"Starting Organization (Dry Run: {dry_run})...")
        
        files_moved = 0
        duplicates_found = 0
        
        # Basic extensions
        valid_exts = {'.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi'}
        
        for root, _, files in os.walk(source_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in valid_exts:
                    continue
                    
                full_path = os.path.join(root, file)
                date_obj = self.get_date_taken(full_path)
                
                if not date_obj:
                    self.logger(f"Skipping {file}: Could not determine date.")
                    continue
                
                # Target Structure: Source/YYYY/YYYY-MM/
                year = str(date_obj.year)
                month = f"{date_obj.year}-{date_obj.month:02d}"
                
                target_dir = os.path.join(source_dir, year, month)
                target_path = os.path.join(target_dir, file)
                
                # Check if it's already there
                if full_path == target_path:
                    continue
                
                # Deduplication / Collision
                if os.path.exists(target_path):
                    # Simple size check for now
                    if os.path.getsize(full_path) == os.path.getsize(target_path):
                        self.logger(f"[DUPLICATE] {file} exists in {month}. Skipping.")
                        duplicates_found += 1
                        continue
                    else:
                        # Name collision, rename
                        base, extension = os.path.splitext(file)
                        new_name = f"{base}_{int(datetime.now().timestamp())}{extension}"
                        target_path = os.path.join(target_dir, new_name)

                if not dry_run:
                    os.makedirs(target_dir, exist_ok=True)
                    try:
                        shutil.move(full_path, target_path)
                        files_moved += 1
                    except Exception as e:
                        self.logger(f"Error moving {file}: {e}")
                else:
                    files_moved += 1
                    # self.logger(f"[DRY] Would move {file} to {year}/{month}")

        self.logger(f"Done. Moved: {files_moved}. Duplicates: {duplicates_found}.")

