
import re
from datetime import datetime

def parse_date(filename):
    patterns = [
        r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})", # Standard YYYY-MM-DD or YYYYMMDD
    ]
    
    print(f"Testing: {filename}")
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                y, m, d = match.groups()
                # Validate ranges
                if 1900 <= int(y) <= 2100 and 1 <= int(m) <= 12 and 1 <= int(d) <= 31:
                    print(f"  MATCH: {y}-{m}-{d}")
                    return datetime(int(y), int(m), int(d))
            except:
                continue
    print("  NO MATCH")
    return None

test_files = [
    "IMG_20230101_120000.jpg",
    "VID-20221231-WA0001.mp4",
    "2024-05-20_Family.png",
    "Screenshot_20231115_100000.png",
    "random_file.txt",
    "19000101_Old.jpg"
]

for f in test_files:
    parse_date(f)
