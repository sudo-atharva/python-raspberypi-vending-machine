#!/usr/bin/env python3

import sys
import os
import time
import json
from pathlib import Path
import RPi.GPIO as GPIO
from config import MOTOR_PINS

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MOTOR_MAP_FILE = os.path.join(DATA_DIR, 'motor_map.json')


def ensure_data_dir():
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


def default_mapping():
    # Logical slot -> physical slot, invert flag
    return {str(k): {'physical': int(k), 'invert': False} for k in MOTOR_PINS.keys()}


def load_mapping():
    ensure_data_dir()
    if os.path.exists(MOTOR_MAP_FILE):
        try:
            with open(MOTOR_MAP_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # normalize keys as strings
                return {str(k): v for k, v in data.items()}
        except Exception as e:
            print(f"Warning: failed to load motor map: {e}")
            return default_mapping()
    else:
        return default_mapping()


def save_mapping(mapping):
    ensure_data_dir()
    try:
        with open(MOTOR_MAP_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2)
        print(f"Motor mapping saved to {MOTOR_MAP_FILE}")
    except Exception as e:
        print(f"Failed to save motor map: {e}")


class MotorTester:
    def __init__(self, mapping=None):
        self.mapping = mapping or load_mapping()
        self.setup_gpio()

    def setup_gpio(self):
        """Initialize GPIO settings"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Set up all motor pins
        for slot, pins in MOTOR_PINS.items():
            GPIO.setup(pins['forward'], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(pins['reverse'], GPIO.OUT, initial=GPIO.LOW)

        print("GPIO ready!")

    def logical_to_physical(self, logical_slot):
        key = str(logical_slot)
        m = self.mapping.get(key)
        if not m:
            # Fallback to identity
            return int(logical_slot), False
        return int(m.get('physical', logical_slot)), bool(m.get('invert', False))

    def test_motor(self, logical_slot, direction, duration):
        """Test a specific logical motor. Mapping is applied so logical slots map to physical ones.

        direction: 'f' or 'r' (or words starting with f/r)
        """
        if str(logical_slot) not in [str(k) for k in MOTOR_PINS.keys()]:
            print(f"Error: Invalid logical motor {logical_slot}. Valid: {list(MOTOR_PINS.keys())}")
            return False

        physical_slot, invert = self.logical_to_physical(logical_slot)

        # Determine intended direction
        dir_full = 'forward' if str(direction).lower().startswith('f') else 'reverse'

        # Apply inversion if mapping says so
        if invert:
            dir_full = 'reverse' if dir_full == 'forward' else 'forward'

        if physical_slot not in MOTOR_PINS:
            print(f"Mapped physical slot {physical_slot} not in MOTOR_PINS")
            return False

        pin = MOTOR_PINS[physical_slot][dir_full]

        print(f"Logical {logical_slot} -> Physical {physical_slot}, invert={invert}. Running {dir_full} (pin {pin}) for {duration}s")

        try:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(pin, GPIO.LOW)
            print("Done!")
            return True
        except Exception as e:
            print(f"Error running motor: {e}")
            return False

    def cleanup(self):
        """Clean up GPIO settings"""
        try:
            GPIO.cleanup()
            print("GPIO cleaned up successfully")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def calibrate_interactive(self):
        """Interactive calibration wizard.

        For each logical slot (1..9) the script will run the logical slot forward for 10s.
        You must observe which physical motor moved and whether it moved forward.
        Enter the physical slot number and 'y' if the observed motion was forward for the
        logical 'forward' command, otherwise enter 'n'. This builds a mapping and
        inversion flag so future commands make logical motors run physically forward.
        """
        print("Starting interactive calibration. Make sure you have a clear view of motors.")
        mapping = {}
        for logical in sorted(MOTOR_PINS.keys()):
            print('\n' + '-' * 40)
            print(f"Logical slot: {logical}")
            input("Press Enter to run logical forward for 10s (will activate mapped physical motor)...")

            # Run logical command (use current mapping if present; temporarily identity)
            # We run 10s forward on logical slot to let user observe which physical moved
            self.test_motor(logical, 'f', 10.0)

            # Ask user which physical motor moved
            while True:
                resp = input(f"Which PHYSICAL slot moved for logical {logical}? (enter number, or 0 if none) ").strip()
                if resp.isdigit():
                    phys = int(resp)
                    break
                else:
                    print("Please enter a number (e.g., 1..9) or 0 if you couldn't identify it.")

            if phys == 0:
                # User couldn't identify: fallback to identity mapping
                print("No physical motor recorded — leaving mapping as identity for this slot.")
                mapping[str(logical)] = {'physical': int(logical), 'invert': False}
                continue

            # Ask whether the observed movement corresponded to forward command
            while True:
                fwd = input("Did the motor move FORWARD when you commanded logical FORWARD? (y/n) ").strip().lower()
                if fwd in ('y', 'n'):
                    invert = (fwd == 'n')
                    break
                else:
                    print("Enter 'y' or 'n'.")

            mapping[str(logical)] = {'physical': phys, 'invert': invert}
            print(f"Saved: logical {logical} -> physical {phys}, invert={invert}")

        # Save mapping
        save_mapping(mapping)
        # Update current mapping in-memory
        self.mapping = mapping
        print("Calibration complete.")


def show_help():
    print("\nUsage:")
    print("  python test_motors.py 1 f 10    # Run logical motor 1 forward for 10s")
    print("  python test_motors.py 2 r 5     # Run logical motor 2 reverse for 5s")
    print("  python test_motors.py --calibrate # Run interactive calibration wizard")
    print("\nInteractive mode: run without args and use '1 f 10' style commands")
    print("Commands in interactive mode:")
    print("  c    - run calibration wizard")
    print("  h    - help")
    print("  q    - quit")
    print("\nAvailable logical motors:", list(MOTOR_PINS.keys()))


def main():
    # Simple CLI parsing
    args = sys.argv[1:]
    if args and args[0] in ('--calibrate', '-c', 'calibrate', 'cal'):
        tester = MotorTester()
        try:
            tester.calibrate_interactive()
        finally:
            tester.cleanup()
        return

    tester = MotorTester()
    try:
        if len(args) == 0:
            # Interactive mode
            print("\nMotor Tester - Interactive Mode")
            print("Enter commands like: 1 f 10")
            print("Type 'c' to calibrate, 'h' for help, 'q' to quit")
            while True:
                try:
                    cmd = input("\nCommand: ").strip().lower()
                    if cmd in ('q', 'quit'):
                        break
                    if cmd in ('h', 'help'):
                        show_help(); continue
                    if cmd in ('c', 'calibrate'):
                        tester.calibrate_interactive(); continue

                    parts = cmd.split()
                    if len(parts) != 3:
                        print("Please use format: 1 f 10")
                        continue
                    motor = int(parts[0])
                    direction = parts[1]
                    seconds = float(parts[2])
                    if direction not in ['f', 'r', 'forward', 'reverse']:
                        print("Direction must be 'f' or 'r'")
                        continue
                    tester.test_motor(motor, direction, seconds)
                except ValueError:
                    print("Invalid input. Use format: 1 f 10")
                except KeyboardInterrupt:
                    break

        elif len(args) == 3:
            try:
                motor = int(args[0])
                direction = args[1].lower()
                seconds = float(args[2])
                if direction not in ['f', 'r', 'forward', 'reverse']:
                    print("Direction must be 'f' or 'r'")
                    return
                tester.test_motor(motor, direction, seconds)
            except ValueError:
                print("Invalid input. Use format: python test_motors.py 1 f 10")
        else:
            show_help()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()