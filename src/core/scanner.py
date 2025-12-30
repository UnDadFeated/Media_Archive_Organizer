import os
import sys
import cv2
import mediapipe as mp
# Explicitly import solutions to avoid 'no attribute' errors in frozen builds
from mediapipe.python.solutions import face_detection
from mediapipe.python.solutions import vision
import threading
import time
from typing import List, Callable, Optional

class ScannerEngine:
    """
    AI Scanner using MediaPipe Face Detection.
    Logic: 
    - No Face Detected -> 'No People' (Keep/Left)
    - Face Detected -> 'Excluded' (Reject/Right)
    """
    
    def __init__(self, logger_callback: Optional[Callable[[str], None]] = None):
        self.logger = logger_callback or (lambda x: print(x))
        self.stop_event = threading.Event()
        
        # Results
        self.no_people_files: List[str] = []
        self.excluded_files: List[str] = []
        
        # Progress Callbacks (current, total, eta_seconds)
        self.progress_callback: Optional[Callable[[int, int, float], None]] = None

    def cancel(self):
        self.stop_event.set()

    def run_scan(self, directory: str, include_subfolders: bool = True, use_gpu: bool = False, keep_animals: bool = False):
        if not os.path.exists(directory):
            self.logger(f"Error: Directory not found: {directory}")
            return

        self.no_people_files.clear()
        self.excluded_files.clear()
        self.stop_event.clear()

        # Gather files
        self.logger("Scanning directory structure...")
        image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}
        all_files = []

        for root, dirs, files in os.walk(directory):
            for f in files:
                if os.path.splitext(f)[1].lower() in image_exts:
                    all_files.append(os.path.join(root, f))
            if not include_subfolders:
                break

        total = len(all_files)
        self.logger(f"Found {total} images. Starting Pipeline ({'GPU' if use_gpu else 'CPU'})...")
        
        # Models
        face_engine = None
        animal_engine = None
        
        try:
            if use_gpu:
                face_engine = self._init_opencv_face()
            else:
                face_engine = self._init_mediapipe_face()
                
            # If keep_animals is True (Checked), User wants to EXCLUDE animals (per new request).
            if keep_animals:
                animal_engine = self._init_animal_detector()
                self.logger("Animal Filter Enabled (Excluding Animals).")
            else:
                self.logger("Animal Filter Disabled (Keeping Animals).")
                
        except Exception as e:
            self.logger(f"Model Init Failed: {e}")
            return

        # Pipeline
        import queue
        img_queue = queue.Queue(maxsize=20)
        
        def producer():
            for f in all_files:
                if self.stop_event.is_set(): break
                try:
                    img = cv2.imread(f)
                    if img is not None:
                        img_queue.put((f, img))
                except: pass
            img_queue.put(None) # Sentinel

        # Start Producer
        t_prod = threading.Thread(target=producer, daemon=True)
        t_prod.start()
        
        # Consumer (Main Thread Context)
        start_time = time.time()
        processed_count = 0
        
        while True:
            if self.stop_event.is_set(): break
            
            try:
                item = img_queue.get(timeout=1)
            except queue.Empty:
                if not t_prod.is_alive(): break
                continue
                
            if item is None: break
            
            f_path, image = item
            
            # 1. Face Detect
            has_face = False
            try:
                if use_gpu:
                    has_face = self._detect_face_opencv(face_engine, image)
                else:
                    has_face = self._detect_face_mediapipe(face_engine, image)
            except: pass

            # 2. Logic
            is_excluded = False
            
            if has_face:
                is_excluded = True
            elif keep_animals and animal_engine:
                # No face, checks for animal to KEEP
                # If Animal -> keep (so NOT excluded)
                # If No Animal -> keep
                # Wait, User said: "exclude photos with animals... give option to move the ones with no people, or animals"
                # Request: "add a checkbox for 'keep animals' before scan"
                # Interpretation:
                # Default (Unchecked): Animals -> Excluded.
                # Checked: Animals -> Kept (No People folder).
                
                # So if !KeepAnimals:
                #   We need to detect animals and EXCLUDE them.
                # If KeepAnimals:
                #   We ignore animals (they fall into 'No People' bucket).
                pass
            
            # Correcting Logic based on Request:
            # "now, also exlude photos with animals, just give opton to move the ones with no people, or animals."
            # "add a checkbox for "keep animals" before scan"
            
            # Base Propositon: "No People" scan keeps things with NO humans.
            # Now we add "No Animals" constraint.
            
            if has_face:
                is_excluded = True
            else:
                # No human. Check animal?
                # If keep_animals is TRUE (Checked): We want to EXCLUDE animals.
                # If keep_animals is FALSE (Unchecked): We IGNORE animals (Keep them).
                
                if keep_animals:
                    # We need to detect animals here
                    if animal_engine:
                         if self._detect_animal(animal_engine, image):
                             is_excluded = True

            if is_excluded:
                self.excluded_files.append(f_path)
            else:
                self.no_people_files.append(f_path)
                
            processed_count += 1
            self._report_progress(processed_count, total, start_time)

        # Cleanup
        if not use_gpu and face_engine: face_engine.close()
        # Animal engine (MediaPipe Task) might need close? It's an ImageClassifier usually or ObjectDetector.
        # We will implement _init properly.

        if self.stop_event.is_set():
            self.logger("Scan Cancelled.")
        else:
            self.logger(f"Done. Kept: {len(self.no_people_files)}, Excluded: {len(self.excluded_files)}")

    def _init_opencv_face(self):
        model = self._get_model_path('face_detection_yunet_2023mar.onnx')
        return cv2.FaceDetectorYN.create(
            model=model, config="", input_size=(320, 320),
            score_threshold=0.5, nms_threshold=0.3, top_k=5000,
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV, target_id=cv2.dnn.DNN_TARGET_OPENCL
        )

    def _detect_face_opencv(self, detector, image):
        h, w, _ = image.shape
        detector.setInputSize((w, h))
        _, faces = detector.detect(image)
        return faces is not None

    def _init_mediapipe_face(self):
        mp_face = mp.solutions.face_detection
        return mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.20)

    def _detect_face_mediapipe(self, detector, image):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        res = detector.process(img_rgb)
        return bool(res.detections)

    def _init_animal_detector(self):
        # MediaPipe Tasks
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        
        model_path = self._get_model_path('efficientdet_lite0.tflite')
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.4, max_results=5)
        return vision.ObjectDetector.create_from_options(options)

    def _detect_animal(self, detector, image):
        # Returns True if Cat, Dog, Bird etc.
        import mediapipe as mp
        
        # Convert to MP Image
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        detection_result = detector.detect(mp_image)
        
        animal_labels = {'cat', 'dog', 'bird', 'horse', 'sheep', 'cow', 'bear', 'zebra', 'giraffe'}
        
        for detection in detection_result.detections:
            for category in detection.categories:
                if category.category_name in animal_labels:
                    return True
        return False

    def _get_model_path(self, filename):
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, 'src', 'core', 'models', filename)

    # Legacy method wrapper if needed, but we replaced run_scan completely.


    def _report_progress(self, idx, total, start_time):
        if idx % 5 == 0 or idx == total - 1:
            elapsed = time.time() - start_time
            if idx > 0:
                avg_time = elapsed / idx
                eta = avg_time * (total - idx)
            else:
                eta = 0
            
            if self.progress_callback:
                self.progress_callback(idx + 1, total, eta)

