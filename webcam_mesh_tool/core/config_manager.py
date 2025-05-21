import json
import os

class ConfigManager:
    def __init__(self, path: str = "config/default_config.json"):
        """
        Initialize the config manager.
        Loads the config if it exists; otherwise, initializes an empty config.
        """
        self.path = path
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.config = json.load(f)
        else:
            print(f"[INFO] No config found at {self.path}, starting with empty config.")
            self.config = {}

    def get_config(self):
        return self.config

    def get_camera_ids(self):
        return list(self.config.keys())

    def get_camera_params(self, camera_id):
        return self.config.get(camera_id, {
            "device_id": int(camera_id.replace("camera_", "")),
            "x_offset": 0,
            "y_offset": 0,
            "rotation_deg": 0,
            "opacity": 1.0
        })

    def update_param(self, camera_id, param, value):
        """
        Update a specific parameter for a given camera.
        Creates the camera entry if it doesn't exist.
        """
        if camera_id not in self.config:
            self.config[camera_id] = self.get_camera_params(camera_id)
        self.config[camera_id][param] = value

    def set_camera_params(self, camera_id, params: dict):
        """
        Replace all parameters for a given camera.
        """
        self.config[camera_id] = params

    def save(self, save_path: str = None):
        """
        Save the current config to the original path or a custom path.
        """
        target = save_path or self.path
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as f:
            json.dump(self.config, f, indent=2)
        print(f"[INFO] Config saved to {target}")
