import cv2
import numpy as np

class MeshTransformer:
    def __init__(self, width=640, height=480):
        """
        Initialize a transformer with the canvas size that all images will be mapped onto.
        """
        self.width = width
        self.height = height

    def transform(self, frame: np.ndarray, x_offset: float, y_offset: float, rotation_deg: float, opacity: float) -> np.ndarray:
        """
        Apply translation, rotation, and opacity to a single frame.
        """
        # Step 1: Rotate the image
        rotated = self._rotate_image(frame, rotation_deg)

        # Step 2: Create a blank canvas and place the rotated image on it
        canvas = np.zeros((self.height, self.width, 4), dtype=np.uint8)

        # Convert rotated to 4 channels (BGRA)
        if rotated.shape[2] == 3:
            rotated = cv2.cvtColor(rotated, cv2.COLOR_BGR2BGRA)

        # Step 3: Translate
        x_offset = int(x_offset)
        y_offset = int(y_offset)

        h, w = rotated.shape[:2]
        x_end = min(self.width, x_offset + w)
        y_end = min(self.height, y_offset + h)

        x_start = max(0, x_offset)
        y_start = max(0, y_offset)

        crop_x = max(0, -x_offset)
        crop_y = max(0, -y_offset)
        crop_w = x_end - x_start
        crop_h = y_end - y_start

        if crop_w > 0 and crop_h > 0:
            canvas[y_start:y_end, x_start:x_end] = rotated[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]

        # Step 4: Apply opacity to alpha channel
        canvas[:, :, 3] = (canvas[:, :, 3].astype(np.float32) * opacity).astype(np.uint8)

        return canvas

    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate an image around its center.
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        return rotated
