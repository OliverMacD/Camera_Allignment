import json
import os
import cv2
import time
import numpy as np

CONFIG_PATH = "config/streamlit_config.json"
WIDTH = 800
HEIGHT = 600

def load_config(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_config(config, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\n✅ Saved config to {path}\n")

def print_config(config):
    print("\nCurrent Camera Config:")
    for cam_id, params in config.items():
        print(f"  {cam_id} ({params['device_id']}):")
        print(f"    x_offset      = {params['x_offset']}")
        print(f"    y_offset      = {params['y_offset']}")
        print(f"    rotation_deg  = {params['rotation_deg']}")
        print(f"    opacity       = {params['opacity']}\n")

def list_webcams(max_index=10):
    print("\n🔍 Scanning for webcams...")
    found = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            found.append(i)
            print(f"  ✅ Found webcam at index {i}")
            cap.release()
    if not found:
        print("❌ No webcams found.")
    return found

def modify_camera(config, cam_id):
    if cam_id not in config:
        print(f"Camera '{cam_id}' not found. Adding new...")
        device_id = int(input("Enter device index: "))
        config[cam_id] = {
            "device_id": device_id,
            "x_offset": 0,
            "y_offset": 0,
            "rotation_deg": 0,
            "opacity": 1.0
        }

    params = config[cam_id]
    print(f"\nModifying {cam_id} (device {params['device_id']})")

    try:
        params["x_offset"] = int(input(f"  x_offset [{params['x_offset']}]: ") or params["x_offset"])
        params["y_offset"] = int(input(f"  y_offset [{params['y_offset']}]: ") or params["y_offset"])
        params["rotation_deg"] = float(input(f"  rotation_deg [{params['rotation_deg']}]: ") or params["rotation_deg"])
        params["opacity"] = float(input(f"  opacity [{params['opacity']}]: ") or params["opacity"])
    except Exception as e:
        print(f"⚠️  Invalid input: {e}")

def show_mesh_preview(config):
    from core.camera_handler import CameraHandler
    from core.mesh_transformer import MeshTransformer

    device_ids = [params["device_id"] for params in config.values()]
    camera_ids = list(config.keys())

    print("📷 Launching mesh preview window (press 'q' to quit)...")

    handler = CameraHandler(device_ids, width=WIDTH, height=HEIGHT)
    transformer = MeshTransformer(width=WIDTH, height=HEIGHT)
    handler.start()

    try:
        while True:
            frames = handler.get_frames()
            canvas = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)

            for i, cam_id in enumerate(camera_ids):
                params = config[cam_id]
                transformed = transformer.transform(
                    frames[i],
                    params["x_offset"],
                    params["y_offset"],
                    params["rotation_deg"],
                    params["opacity"]
                )
                alpha = transformed[:, :, 3:] / 255.0
                for c in range(3):
                    canvas[:, :, c] = (transformed[:, :, c] * alpha[:, :, 0] +
                                       canvas[:, :, c] * (1 - alpha[:, :, 0])).astype(np.uint8)
                canvas[:, :, 3] = ((alpha[:, :, 0] + canvas[:, :, 3] / 255.0 * (1 - alpha[:, :, 0])) * 255).astype(np.uint8)

            rgb_frame = cv2.cvtColor(canvas, cv2.COLOR_BGRA2BGR)
            cv2.imshow("Live Mesh Preview", rgb_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        handler.stop()
        cv2.destroyAllWindows()
        print("🛑 Preview closed.")

def run_cli():
    print("🎛 Webcam Mesh Config CLI\n")

    config = load_config(CONFIG_PATH)

    while True:
        print("\n--- Main Menu ---")
        print("[1] View current config")
        print("[2] Modify existing camera")
        print("[3] Add new camera")
        print("[4] Save config")
        print("[5] Scan for available webcams")
        print("[6] Show mesh preview (OpenCV window)")
        print("[7] Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            print_config(config)
        elif choice == "2":
            cam_id = input("Enter camera ID (e.g., camera_0): ")
            if cam_id in config:
                modify_camera(config, cam_id)
            else:
                print("❌ Camera not found.")
        elif choice == "3":
            cam_id = input("Enter new camera ID (e.g., camera_2): ")
            modify_camera(config, cam_id)
        elif choice == "4":
            save_config(config, CONFIG_PATH)
        elif choice == "5":
            list_webcams()
        elif choice == "6":
            if not config:
                print("❌ No config loaded. Please create or load a config first.")
            else:
                show_mesh_preview(config)
        elif choice == "7":
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    run_cli()
