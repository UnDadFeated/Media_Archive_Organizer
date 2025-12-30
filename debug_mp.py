import os
import mediapipe

mp_dir = os.path.dirname(mediapipe.__file__)
modules_dir = os.path.join(mp_dir, 'modules')
if os.path.exists(modules_dir):
    print(f"Listing modules: {os.listdir(modules_dir)}")

try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    print("SUCCESS: Imported mediapipe.tasks.python.vision")
    print(f"Vision dir: {dir(vision)}")
except ImportError as e:
    print(f"FAIL: Import tasks: {e}")
