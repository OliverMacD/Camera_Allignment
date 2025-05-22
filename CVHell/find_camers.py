import os
import cv2
import time
import glob

def list_video_devices():
    return sorted(glob.glob("/dev/video*"))

def test_camera(device, preview=False):
    index = int(device.replace("/dev/video", ""))
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        return False

    ret, frame = cap.read()
    if not ret:
        cap.release()
        return False

    if preview:
        cv2.imshow(f"Preview: {device}", frame)
        print(f"[INFO] Showing preview for {device}. Press any key to continue.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    cap.release()
    return True

def main(preview=False):
    devices = list_video_devices()
    print(f"[INFO] Found video devices: {devices}")

    working_cams = []
    for device in devices:
        print(f"[TEST] Checking {device}...", end="")
        if test_camera(device, preview=preview):
            print("✅ Alive")
            working_cams.append(device)
        else:
            print("❌ Not responding")

    print("\n=== Working Cameras ===")
    for cam in working_cams:
        print(cam)

    print("\nUse the previews to identify the cameras you want.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scan and preview working camera devices.")
    parser.add_argument("--preview", action="store_true", help="Show preview window for each camera")
    args = parser.parse_args()

    main(preview=args.preview)
