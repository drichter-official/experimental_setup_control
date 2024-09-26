# utils_motor/motor_controller.py

import serial
import time

# Import the utility functions from utils_motor.utils
from utils_motor.utils import find_arduino, check_arduino_cli, upload_sketch

class MotorController:
    def __init__(self, steps_per_revolution_base=200, micro_stepping=16,
                 motor_max_speed=200, set_motor_speed=50,
                 motor_acceleration=200, revolutions=1, sketch_path=None):
        """
        Initialize the MotorController with given parameters.
        """
        self.steps_per_revolution_base = steps_per_revolution_base
        self.micro_stepping = micro_stepping
        self.motor_max_speed = motor_max_speed
        self.set_motor_speed = set_motor_speed
        self.motor_acceleration = motor_acceleration
        self.revolutions = revolutions
        self.sketch_path = sketch_path

        self.ser = None  # Serial connection
        self.port = None  # Arduino port
        self.fqbn = None  # Arduino Fully Qualified Board Name

        self._validate_parameters()

    def _validate_parameters(self):
        """
        Validate motor parameters.
        """
        assert self.micro_stepping in [1, 2, 4, 8, 16], "Invalid microstepping value. Allowed values are [1, 2, 4, 8, 16]"
        # Add more validations as needed

    def connect(self):
        """
        Find the Arduino, upload the sketch, and establish a serial connection.
        """
        if not self.sketch_path:
            raise ValueError("Sketch path must be provided to upload the Arduino sketch.")

        check_arduino_cli()
        self.port, self.fqbn = find_arduino()
        print(f"Found Arduino on port {self.port} with FQBN {self.fqbn}")
        upload_sketch(self.sketch_path, self.port, self.fqbn)

        time.sleep(2)  # Wait for the Arduino to reset after uploading

        # Set up the serial connection
        self.ser = serial.Serial(self.port, 9600, timeout=1)
        print("Initializing Arduino serial connection")
        time.sleep(1)  # Wait for the connection to initialize

    def configure(self):
        """
        Send configuration commands to the Arduino.
        """
        print("Loading configuration setup")
        commands = [
            f'r{self.steps_per_revolution_base}'
            f'm{self.micro_stepping}',
            f'M{self.motor_max_speed * self.micro_stepping}',
            f'S{self.set_motor_speed * self.micro_stepping}',
            f'A{self.motor_acceleration * self.micro_stepping}'
        ]
        for command in commands:
            self._send_command(command)
            time.sleep(0.5)

    def _send_command(self, command, value=None):
        """
        Send a command to the Arduino over serial communication.
        """
        if value is not None:
            full_command = f"{command}{value}\n"
        else:
            full_command = f"{command}\n"
        self.ser.write(full_command.encode())
    def rotate_forwards(self, steps=None):
        """
        Rotate the motor by a specified number of steps.
        """
        if steps is None:
            steps = self.steps_per_revolution_base * self.micro_stepping * self.revolutions
        self._send_command('F', value=steps)
        print(f"Motor rotating forwards by {steps} steps")

    def rotate_backwards(self, steps=None):
        """
        Rotate the motor by a specified number of steps.
        """
        if steps is None:
            steps = self.steps_per_revolution_base * self.micro_stepping * self.revolutions
        self._send_command('B', value=steps)

    def close(self):
        """
        Close the serial connection to the Arduino.
        """
        if self.ser:
            self.ser.close()
            print("Serial connection closed.")

