import subprocess
import json
import sys
import shutil
def check_arduino_cli():
    """Check if arduino-cli is installed."""
    if not shutil.which('arduino-cli'):
        print("arduino-cli is not installed or not in your PATH.")
        print("Please install it from https://github.com/arduino/arduino-cli#installation")
        sys.exit(1)

def find_arduino():
    """Find the connected Arduino board and return its port and FQBN."""
    result = subprocess.run(
        ['arduino-cli', 'board', 'list', '--format', 'json'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print("Error running 'arduino-cli board list':")
        print(result.stderr)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON output from arduino-cli:")
        print(result.stdout)
        sys.exit(1)

    detected_ports = data.get('detected_ports', [])
    if not detected_ports:
        print("No Arduino boards found.")
        sys.exit(1)

    for port_info in detected_ports:
        port = port_info.get('port', {}).get('address')
        matching_boards = port_info.get('matching_boards', [])
        if not matching_boards:
            continue
        for board in matching_boards:
            fqbn = board.get('fqbn')
            if port and fqbn:
                return port, fqbn

    print("No compatible Arduino boards found.")
    sys.exit(1)

def upload_sketch(sketch_path, port, fqbn):
    """Compile and upload the Arduino sketch to the board."""
    compile_cmd = [
        'arduino-cli', 'compile', '--fqbn', fqbn, sketch_path
    ]
    print("Compiling the sketch...")
    result = subprocess.run(compile_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Compilation failed:")
        print(result.stderr)
        sys.exit(1)
    else:
        print("Compilation succeeded.")

    upload_cmd = [
        'arduino-cli', 'upload', '-p', port, '--fqbn', fqbn, sketch_path
    ]
    print("Uploading the sketch to the board...")
    result = subprocess.run(upload_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Upload failed:")
        print(result.stderr)
        sys.exit(1)
    else:
        print("Upload succeeded.")
