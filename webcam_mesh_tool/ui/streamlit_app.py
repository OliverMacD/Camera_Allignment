import streamlit as st
from core.config_manager import ConfigManager
from core.webcam_mesh import WebcamMesh
import numpy as np
import cv2
from PIL import Image
import os
import json
import time

CONFIG_PATH = "config/streamlit_config.json"

def launch_ui():
    st.set_page_config(page_title="Webcam Mesh Configurator", layout="wide")

    if "stage" not in st.session_state:
        st.session_state.stage = "setup"
        st.session_state.num_cameras = 2
        st.session_state.device_map = {}
        st.session_state.mesh = None
        st.session_state.config_manager = None
        st.session_state.live_preview = False

    st.title("🔧 Webcam Mesh Configurator")

    if st.session_state.stage == "setup":
        st.header("Step 1: Select Number of Cameras")
        st.session_state.num_cameras = st.slider("Number of Cameras", min_value=2, max_value=8, value=2)

        st.header("Step 2: Assign Device Index for Each Camera")
        for i in range(st.session_state.num_cameras):
            cam_id = f"camera_{i}"
            st.session_state.device_map[cam_id] = st.number_input(
                f"Camera {i} → System Device Index", min_value=0, max_value=20, value=i, key=f"device_{i}"
            )

        if st.button("Start Configuration"):
            config = {}
            for cam_id, device_id in st.session_state.device_map.items():
                config[cam_id] = {
                    "device_id": int(device_id),
                    "x_offset": 0,
                    "y_offset": 0,
                    "rotation_deg": 0,
                    "opacity": 1.0
                }

            os.makedirs("config", exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump(config, f, indent=2)

            # Just store the config path and move to next stage
            st.session_state.stage = "mesh_view"
            st.session_state.mesh_initialized = False
            st.rerun()


    elif st.session_state.stage == "mesh_view":

        # Lazy-load only once
        if "mesh_initialized" not in st.session_state or not st.session_state.mesh_initialized:
            st.session_state.config_manager = ConfigManager(CONFIG_PATH)
            st.session_state.mesh = WebcamMesh(CONFIG_PATH, width=800, height=600)
            st.session_state.mesh_initialized = True


        st.sidebar.header("🎛 Adjust Cameras")

        st.sidebar.checkbox("🔁 Live Feed (Auto-refresh)", value=st.session_state.live_preview, key="live_preview")

        updated = False
        for cam_id in st.session_state.config_manager.get_camera_ids():
            with st.sidebar.expander(f"{cam_id}", expanded=True):
                x = st.slider(f"{cam_id} X Offset", -400, 400, value=st.session_state.config_manager.get_camera_params(cam_id)["x_offset"])
                y = st.slider(f"{cam_id} Y Offset", -300, 300, value=st.session_state.config_manager.get_camera_params(cam_id)["y_offset"])
                rot = st.slider(f"{cam_id} Rotation", -180, 180, value=st.session_state.config_manager.get_camera_params(cam_id)["rotation_deg"])
                alpha = st.slider(f"{cam_id} Opacity", 0.0, 1.0, value=st.session_state.config_manager.get_camera_params(cam_id)["opacity"])

                st.session_state.config_manager.update_param(cam_id, "x_offset", x)
                st.session_state.config_manager.update_param(cam_id, "y_offset", y)
                st.session_state.config_manager.update_param(cam_id, "rotation_deg", rot)
                st.session_state.config_manager.update_param(cam_id, "opacity", alpha)
                updated = True

        if st.sidebar.button("💾 Save Config"):
            st.session_state.config_manager.save(CONFIG_PATH)

        st.subheader("📷 Composite View")

        frame_placeholder = st.empty()

        def show_frame():
            frame = st.session_state.mesh.get_composite_frame()
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            image = Image.fromarray(bgr_frame)
            frame_placeholder.image(image, caption="Live View", use_column_width=True)

        if st.session_state.live_preview:
            while st.session_state.live_preview:
                show_frame()
                time.sleep(0.1)
        else:
            show_frame()
