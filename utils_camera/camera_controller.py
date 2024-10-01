# camera_controller.py

import threading
import tkinter as tk
from PIL import Image, ImageTk
import queue
import typing
import time
import numpy as np

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, TLCamera, Frame
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE


class LiveViewCanvas(tk.Canvas):
    """Tkinter Canvas for displaying live images."""

    def __init__(self, parent, image_queue):
        # type: (typing.Any, queue.Queue) -> LiveViewCanvas
        self.image_queue = image_queue
        self._image_width = 0
        self._image_height = 0
        super().__init__(parent)
        self.pack()
        self._update_image()

    def _update_image(self):
        try:
            image = self.image_queue.get_nowait()
            self._photo_image = ImageTk.PhotoImage(master=self, image=image)
            if (self._photo_image.width() != self._image_width) or (self._photo_image.height() != self._image_height):
                # Resize the canvas to match the new image size
                self._image_width = self._photo_image.width()
                self._image_height = self._photo_image.height()
                self.config(width=self._image_width, height=self._image_height)
            self.create_image(0, 0, image=self._photo_image, anchor='nw')
        except queue.Empty:
            pass
        # Schedule the next update
        self.after(10, self._update_image)


class ImageAcquisitionThread(threading.Thread):
    """Thread for acquiring images from the camera."""

    def __init__(self, camera):
        # type: (TLCamera) -> None
        super().__init__()
        self._camera = camera
        self._bit_depth = camera.bit_depth
        self._camera.image_poll_timeout_ms = 0  # Non-blocking
        self._image_queue = queue.Queue(maxsize=2)
        self._stop_event = threading.Event()
        self._save_event = threading.Event()
        self._save_path = None

    def get_output_queue(self):
        # type: () -> queue.Queue
        return self._image_queue

    def stop(self):
        self._stop_event.set()

    def save_next_frame(self, image_path):
        self._save_path = image_path
        self._save_event.set()

    def _get_image(self, frame):
        # Convert frame to PIL Image
        scaled_image = frame.image_buffer >> (self._bit_depth - 8)
        return Image.fromarray(scaled_image.astype(np.uint8))

    def run(self):
        while not self._stop_event.is_set():
            try:
                frame = self._camera.get_pending_frame_or_null()
                if frame is not None:
                    pil_image = self._get_image(frame)
                    self._image_queue.put_nowait(pil_image)
                    if self._save_event.is_set():
                        pil_image.save(self._save_path)
                        print(f"Image saved to {self._save_path}")
                        self._save_event.clear()
                else:
                    # No frame available; sleep briefly
                    time.sleep(0.01)
            except queue.Full:
                pass
            except Exception as error:
                print(f"Encountered error: {error}, image acquisition will stop.")
                break
        print("Image acquisition has stopped")


class CameraController:
    """Controller class for camera operations."""

    def __init__(self):
        self._sdk = TLCameraSDK()
        camera_list = self._sdk.discover_available_cameras()
        if not camera_list:
            raise Exception("No cameras found.")
        self._camera = self._sdk.open_camera(camera_list[0])

        # Configure camera settings
        self._camera.frames_per_trigger_zero_for_unlimited = 0
        self._camera.arm(2)
        self._camera.issue_software_trigger()

        # Initialize image acquisition thread
        self._image_acquisition_thread = ImageAcquisitionThread(self._camera)

        # Initialize GUI components
        self._root = tk.Tk()
        self._root.title(self._camera.name)

        # Create a frame for the live view canvas and controls
        self._main_frame = tk.Frame(self._root)
        self._main_frame.pack()

        # Create a canvas for displaying the live view
        self._live_view_canvas = LiveViewCanvas(
            parent=self._main_frame,
            image_queue=self._image_acquisition_thread.get_output_queue()
        )

        # Create a frame for the controls (Take Picture button and slider)
        self._controls_frame = tk.Frame(self._main_frame)
        self._controls_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        # Add a "Take Picture" button on the left side
        self._take_picture_button = tk.Button(
            self._controls_frame, text="Take Picture", command=self._on_take_picture
        )
        self._take_picture_button.pack(side=tk.LEFT, padx=10)

        # Print exposure time range
        print(
            f"Exposure time range: {self._camera.exposure_time_range_us.min} us to {50000} us") # self._camera.exposure_time_range_us.max

        # Add an exposure time slider on the right side with a wide width
        exposure_min = max(self._camera.exposure_time_range_us.min, 1)  # Ensure min is at least 1 us
        exposure_max = 50000

        self._exposure_scale = tk.Scale(
            self._controls_frame,
            from_=exposure_min,
            to=exposure_max,
            resolution=40,
            orient=tk.HORIZONTAL,
            label="Exposure Time (us)",
            length=1000  # Increase the physical width of the slider
        )
        self._exposure_scale.set(self._camera.exposure_time_us)
        self._exposure_scale.pack(side=tk.RIGHT, padx=0)
        self._exposure_scale.bind("<ButtonRelease-1>", self._on_exposure_change)

        # Handle window close event
        self._root.protocol("WM_DELETE_WINDOW", self.stop_live_view)

    def start_live_view(self):
        """Start the live view and image acquisition."""
        print("Starting live view...")
        self._image_acquisition_thread.start()
        self._root.mainloop()

    def stop_live_view(self):
        """Stop the live view and clean up resources."""
        print("Stopping live view...")
        try:
            self._image_acquisition_thread.stop()
            self._image_acquisition_thread.join()

            self._camera.disarm()
            print("Camera disarmed successfully.")

            # Dispose of the camera object if it hasn't been disposed of yet
            self._camera.dispose()
            print("Camera disposed successfully.")

            # Dispose of the SDK
            self._sdk.dispose()
            print("SDK disposed successfully.")

        except Exception as e:
            print(f"An error occurred while stopping the live view: {e}")

        self._root.quit()
        print("Camera resources closed.")

    def take_picture(self, image_path):
        """Capture an image and save it to the specified path."""
        self._image_acquisition_thread.save_next_frame(image_path)

    def _on_take_picture(self):
        """Callback for the 'Take Picture' button."""
        image_path = f"image_{int(time.time())}.png"
        self.take_picture(image_path)

    def _on_exposure_change(self, event):
        """Callback when the exposure time scale is changed."""
        exposure_time_us = int(self._exposure_scale.get())
        try:
            self._camera.exposure_time_us = exposure_time_us
            print(f"Exposure time set to {exposure_time_us} us")
        except Exception as e:
            print(f"Failed to set exposure time: {e}")
            try:
                self._camera.disarm()
                self._camera.exposure_time_us = exposure_time_us
                self._camera.arm(2)
                self._camera.issue_software_trigger()
                print(f"Exposure time set to {exposure_time_us} us after re-arming")
            except Exception as e:
                print(f"Failed to set exposure time after re-arming: {e}")

