import argparse
import configparser
import time

from utils_motor.motor_controller import MotorController
#from utils_camera.camera_controller import CameraController

def main():
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

        def get_arg(config_section, arg_name, current_value, arg_type):
            if arg_name in config_section:
                return arg_type(config_section[arg_name])
            else:
                return current_value

        args.steps_per_revolution_base = get_arg(config_defaults, 'steps_per_revolution_base',
                                                 args.steps_per_revolution_base, int)
        args.micro_stepping = get_arg(config_defaults, 'micro_stepping', args.micro_stepping, int)
        args.motor_max_speed = get_arg(config_defaults, 'motor_max_speed', args.motor_max_speed, int)
        args.set_motor_speed = get_arg(config_defaults, 'set_motor_speed', args.set_motor_speed, int)
        args.motor_acceleration = get_arg(config_defaults, 'motor_acceleration', args.motor_acceleration, int)
        args.revolutions = get_arg(config_defaults, 'revolutions', args.revolutions, int)

    # Create an instance of MotorController with the updated arguments
    motor_controller = MotorController(
        steps_per_revolution_base=args.steps_per_revolution_base,
        micro_stepping=args.micro_stepping,
        motor_max_speed=args.motor_max_speed,
        set_motor_speed=args.set_motor_speed,
        motor_acceleration=args.motor_acceleration,
        revolutions=args.revolutions,
        sketch_path=args.sketch_path
    )

    try:
        motor_controller.connect()
        motor_controller.configure()

        input("Press Enter to start the motor rotation...")

        motor_controller.rotate_forwards()

        # Adjust the sleep time as needed for the motor to complete movement
        time.sleep(2)
        #motor_controller.rotate_forwards()
        time.sleep(2)
        #motor_controller.rotate_backwards()

    finally:
        motor_controller.close()

if __name__ == "__main__":
    main()
