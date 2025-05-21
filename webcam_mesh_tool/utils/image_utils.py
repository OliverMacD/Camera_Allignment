import cv2
import numpy as np

def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotates an image (keeping the original size) around its center.
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return rotated

def translate_image(image: np.ndarray, x_offset: int, y_offset: int, canvas_width: int, canvas_height: int) -> np.ndarray:
    """
    Places an image on a blank canvas at a specified offset.
    """
    canvas = np.zeros((canvas_height, canvas_width, 4), dtype=np.uint8)

    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    h, w = image.shape[:2]
    x_offset = int(x_offset)
    y_offset = int(y_offset)

    x_end = min(canvas_width, x_offset + w)
    y_end = min(canvas_height, y_offset + h)

    x_start = max(0, x_offset)
    y_start = max(0, y_offset)

    crop_x = max(0, -x_offset)
    crop_y = max(0, -y_offset)
    crop_w = x_end - x_start
    crop_h = y_end - y_start

    if crop_w > 0 and crop_h > 0:
        canvas[y_start:y_end, x_start:x_end] = image[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]

    return canvas

def apply_opacity(image: np.ndarray, opacity: float) -> np.ndarray:
    """
    Applies opacity to the alpha channel of a BGRA image.
    """
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    image = image.copy()
    image[:, :, 3] = (image[:, :, 3].astype(np.float32) * opacity).astype(np.uint8)
    return image

def alpha_blend(base: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    """
    Alpha blend two BGRA images.
    """
    result = base.copy()
    alpha_overlay = overlay[:, :, 3:] / 255.0
    alpha_base = base[:, :, 3:] / 255.0

    for c in range(3):
        result[:, :, c] = (overlay[:, :, c] * alpha_overlay[:, :, 0] +
                           base[:, :, c] * (1 - alpha_overlay[:, :, 0])).astype(np.uint8)

    result[:, :, 3] = ((alpha_overlay[:, :, 0] + alpha_base[:, :, 0] * (1 - alpha_overlay[:, :, 0])) * 255).astype(np.uint8)

    return result
