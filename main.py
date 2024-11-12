import os
import argparse
import configparser
import time
import threading

from utils_camera.camera_controller import CameraController
from utils_arduino.arduino_controller import ArduinoController

from tqdm import tqdm

def aquire_images(config, camera_controller, motor_controller):
    """
    Function to handle motor control and image acquisition.
    Mainly used for threading purposes...
    """
    input("Press Enter to start image acquisition and motor rotation ...")
    os.makedirs(config['images_path'], exist_ok=True)
    for i in tqdm(range(config["n_images"])):
        # Capture an image and save it
        image_path = f"{config['images_path']}/{i}.png"
        camera_controller.take_picture(image_path)

        # Rotate the motor
        steps = (
            config["micro_stepping"]
            * config["steps_per_revolution_base"]
            * 40
            / config["n_images"]
        )
        motor_controller.rotate_forwards(steps)

        # Wait for 3 seconds before taking the next picture
        time.sleep(3)

    # Rotate the motor back to the original position
    motor_controller.rotate_backwards(
        config["micro_stepping"] * config["steps_per_revolution_base"] * 40
    )

    # Stop the live view after the loop is done
    camera_controller.stop_live_view()
    motor_controller.close()


def main():
    ######## Load Configuration ########
    parser = argparse.ArgumentParser(description='Motor Controller Script')
    parser.add_argument('--steps_per_revolution_base', type=int, default=200,
                        help='Number of steps for one rotation.')
    parser.add_argument('--micro_stepping', type=int, default=16, help='Microstepping level (1, 2, 4, 8, or 16).')
    parser.add_argument('--motor_max_speed', type=int, default=200, help='Maximum motor speed in steps per second.')
    parser.add_argument('--set_motor_speed', type=int, default=50, help='Desired motor speed in steps per second.')
    parser.add_argument('--motor_acceleration', type=int, default=200,
                        help='Motor acceleration in steps per second².')
    parser.add_argument('--revolutions', type=int, default=1, help='Number of revolutions to rotate.')
    parser.add_argument('--config_path', type=str, default='configs/config.ini', help='Configuration file path.')
    parser.add_argument('--load_config', action='store_true', help='Load configuration from file.')
    parser.add_argument('--sketch_path', type=str, required=True, help='Path to the Arduino sketch.')

    parser.add_argument('--n_images', type=int, default=40, help='Number of images to aquire.')
    parser.add_argument('--images_path', type=str, default='/data/40_imgs', help='Storage path for the images.')

    args = parser.parse_args()

    # If load_config is True, load config file and update args
    if args.load_config:
        print('Loading configuration from file')
        config = configparser.ConfigParser()
        config.read(args.config_path)
        config_defaults = config['DEFAULT']

        # Update args with values from the config file
        for key in config_defaults:
            if hasattr(args, key):
                # Convert the config value to the correct type
                arg_type = type(getattr(args, key))
                setattr(args, key, arg_type(config_defaults[key]))
            else:
                print(f"Warning: Unknown config parameter '{key}' in config file.")

    # Now you can use vars(args) as your config dict
    config = vars(args)

    # Create an instance of MotorController with the updated arguments
    motor_controller = ArduinoController(
        config=config,
        sketch_path=args.sketch_path,
    )
    motor_controller.connect()

    # Create an instance of CameraController
    camera_controller = CameraController()

    # Run the motor control task in a separate thread
    motor_thread = threading.Thread(target=aquire_images, args=(config, camera_controller, motor_controller))
    motor_thread.start()

    # Start the live view (this needs to be on the main thread)
    camera_controller.start_live_view()

    # Wait for the motor control thread to finish
    motor_thread.join()

if __name__ == "__main__":
    main()
