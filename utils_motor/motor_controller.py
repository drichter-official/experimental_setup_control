# utils_motor/motor_controller.py

import serial
import time

# Import the utility functions from utils_motor.utils
from utils_motor.utils import find_arduino, check_arduino_cli, upload_sketch

class MotorController:
    def __init__(self,config, sketch_path):
        """
        Initialize the MotorController with given parameters.
        """
        try:
            self.steps_per_revolution_base = config["steps_per_revolution_base"]
            self.micro_stepping = config["micro_stepping"]
            self.motor_max_speed = config["motor_max_speed"]
            self.set_motor_speed = config["set_motor_speed"]
            self.motor_acceleration = config["motor_acceleration"]
            self.revolutions = config["revolutions"]
        except KeyError as e:
            pass
        self.sketch_path = sketch_path

        self.ser = None  # Serial connection
        self.port = None  # Arduino port
        self.fqbn = None  # Arduino Fully Qualified Board Name

        self.config = config
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
        upload_sketch(self.sketch_path, self.port, self.fqbn, self.config)

        time.sleep(2)  # Wait for the Arduino to reset after uploading

        # Set up the serial connection
        self.ser = serial.Serial(self.port, 9600, timeout=1)
        print("Initializing Arduino serial connection")
        time.sleep(1)  # Wait for the connection to initialize

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

