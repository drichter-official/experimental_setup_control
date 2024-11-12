# light_tester.py

from utils_arduino.arduino_controller import ArduinoController
import time
import serial

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

    # Initialize the arduino controller
    arduino = ArduinoController(config)

    try:
        # Connect to the Arduino
        arduino.connect()

        # Initialize LED tester
        ser = serial.Serial(arduino.port, 9600, timeout=1)
        time.sleep(2)  # Allow some time for the Arduino to reset

        while True:
            # Get user input from the console
            user_input = input("Enter command for LED strip ('on'/'off'/'set_color RRGGBB'/'brightness 0-255'/'quit'): ")

            # Check if the user wants to quit
            if user_input.lower() == 'quit':
                print("Exiting...")
                break

            # Handle LED strip commands
            if user_input.lower() == 'on':
                print("Turning on the LED strip with full brightness...")
                ser.write(b'L255\n')  # Turn on with full brightness
            elif user_input.lower() == 'off':
                print("Turning off the LED strip...")
                ser.write(b'O\n')  # Turn off
            elif user_input.lower().startswith('set_color '):
                color_hex = user_input.split()[1]
                if len(color_hex) == 6:
                    print(f"Setting LED strip color to #{color_hex}...")
                    ser.write(f'C{color_hex}\n'.encode())
                else:
                    print("Invalid color format. Please use RRGGBB format.")
            elif user_input.lower().startswith('brightness '):
                try:
                    brightness = int(user_input.split()[1])
                    if 0 <= brightness <= 255:
                        print(f"Setting LED strip brightness to {brightness}...")
                        ser.write(f'L{brightness}\n'.encode())
                    else:
                        print("Brightness must be between 0 and 255.")
                except ValueError:
                    print("Invalid brightness value. Please enter a number between 0 and 255.")
            else:
                print("Invalid command. Please try again.")

            # Small delay to allow serial communication to complete
            time.sleep(0.5)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Ensure the serial connection is closed properly
        arduino.close()


if __name__ == "__main__":
    main()
