import numpy as np
from core.camera_handler import CameraHandler
from core.mesh_transformer import MeshTransformer
from core.config_manager import ConfigManager
import cv2
import os

class WebcamMesh:
    def __init__(self, config_path: str = "config/default_config.json", width=640, height=480):
        """
        Initialize the mesh system using a configuration file.
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()

        self.width = width
        self.height = height

        device_ids = [params["device_id"] for params in self.config.values()]
        self.camera_handler = CameraHandler(device_ids, width=self.width, height=self.height)
        self.transformer = MeshTransformer(width=self.width, height=self.height)

        self.camera_ids = list(self.config.keys())

        self.camera_handler.start()

    def get_composite_frame(self) -> np.ndarray:
        """
        Returns a single composited frame using current config.
        """
        frames = self.camera_handler.get_frames()
        canvas = np.zeros((self.height, self.width, 4), dtype=np.uint8)

        for i, camera_id in enumerate(self.camera_ids):
            params = self.config[camera_id]
            transformed = self.transformer.transform(
                frames[i],
                params["x_offset"],
                params["y_offset"],
                params["rotation_deg"],
                params["opacity"]
            )
            canvas = self._alpha_blend(canvas, transformed)

        return canvas

    def _alpha_blend(self, base: np.ndarray, overlay: np.ndarray) -> np.ndarray:
        """
        Alpha blends two BGRA images together.
        """
        alpha_overlay = overlay[:, :, 3:] / 255.0
        alpha_base = base[:, :, 3:] / 255.0

        # Blend each RGB channel
        for c in range(3):
            base[:, :, c] = (overlay[:, :, c] * alpha_overlay[:, :, 0] +
                             base[:, :, c] * (1 - alpha_overlay[:, :, 0])).astype(np.uint8)

        # Update alpha channel
        base[:, :, 3] = ((alpha_overlay[:, :, 0] + alpha_base[:, :, 0] * (1 - alpha_overlay[:, :, 0])) * 255).astype(np.uint8)

        return base

    def export_still(self, output_path="output/final_composite_feed/still.png"):
        """
        Save the current composite frame as a PNG.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        frame = self.get_composite_frame()
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        cv2.imwrite(output_path, bgr_frame)
        print(f"[INFO] Still exported to {output_path}")

    def stop(self):
        """
        Gracefully stop the camera threads.
        """
        self.camera_handler.stop()
