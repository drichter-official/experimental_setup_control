import argparse
import configparser
import time

from utils_motor.motor_controller import MotorController
#from utils_camera.camera_controller import CameraController

def main():
    import argparse
    import configparser

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
    motor_controller = MotorController(
        config=config,
        sketch_path=args.sketch_path,
    )

    try:
        motor_controller.connect()

        input("Press Enter to start the motor rotation...")

        #motor_controller.rotate_forwards()

        # Adjust the sleep time as needed for the motor to complete movement
        # time.sleep(2)
        motor_controller.rotate_forwards()
        # time.sleep(2)
        # motor_controller.rotate_backwards()

    finally:
        motor_controller.close()

if __name__ == "__main__":
    main()
