# motor_console_controller.py

from utils_motor.motor_controller import MotorController
import time

def main():
    # Configuration for the motor
    config = {
        "steps_per_revolution_base": 200,
        "micro_stepping": 16,
        "motor_max_speed": 1600,
        "set_motor_speed": 800,
        "motor_acceleration": 1600,
        "revolutions": 1
    }

    # Initialize the motor controller
    motor = MotorController(config)

    try:
        # Connect to the Arduino
        motor.connect()

        while True:
            # Get user input from the console
            user_input = input("Enter the number of steps (positive for forward, negative for backward, 'q' to quit): ")

            # Check if the user wants to quit
            if user_input.lower() == 'q':
                print("Exiting...")
                break

            # Try to convert the input to an integer
            try:
                steps = int(user_input)
            except ValueError:
                print("Invalid input. Please enter an integer value.")
                continue

            # Move the motor based on the user input
            if steps > 0:
                print(f"Moving forward by {steps} steps...")
                motor.rotate_forwards(steps)
            elif steps < 0:
                print(f"Moving backward by {-steps} steps...")
                motor.rotate_backwards(-steps)
            else:
                print("Zero steps entered, motor will not move.")

            # Small delay to allow serial communication to complete
            time.sleep(0.5)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Ensure the serial connection is closed properly
        motor.close()


if __name__ == "__main__":
    main()
