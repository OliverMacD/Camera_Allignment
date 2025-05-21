import cv2
import threading
import time
import numpy as np

class CameraHandler:
    def __init__(self, device_ids, width=640, height=480, fps=30):
        """
        Initialize camera streams for each device ID.
        """
        self.device_ids = device_ids
        self.captures = []
        self.frames = [None] * len(device_ids)
        self.width = width
        self.height = height
        self.fps = fps
        self.running = False
        self.lock = threading.Lock()

        for i, cam_id in enumerate(device_ids):
            cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open webcam {cam_id}")
            self.captures.append(cap)

    def _frame_updater(self, index, capture):
        """
        Continuously grab frames in a separate thread for each camera.
        """
        while self.running:
            ret, frame = capture.read()
            if ret:
                with self.lock:
                    self.frames[index] = frame
            time.sleep(1 / self.fps)

    def start(self):
        """
        Start threaded capture from all cameras.
        """
        if self.running:
            return
        self.running = True
        self.threads = []
        for i, cap in enumerate(self.captures):
            t = threading.Thread(target=self._frame_updater, args=(i, cap), daemon=True)
            t.start()
            self.threads.append(t)
        print("[INFO] CameraHandler threads started.")

    def get_frames(self):
        """
        Safely return the latest frame from each camera.
        """
        with self.lock:
            return [frame.copy() if frame is not None else np.zeros((self.height, self.width, 3), dtype=np.uint8)
                    for frame in self.frames]

    def stop(self):
        """
        Stop all threads and release all cameras.
        """
        self.running = False
        for cap in self.captures:
            cap.release()
        print("[INFO] CameraHandler stopped and cameras released.")
