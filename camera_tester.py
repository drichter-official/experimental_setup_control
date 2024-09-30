import time

from utils_camera.camera_controller import CameraController

camera_controller = CameraController()
camera_controller.start_live_view()
time.sleep(3)
camera_controller.stop_live_view()