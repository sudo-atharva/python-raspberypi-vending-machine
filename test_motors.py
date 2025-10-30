#!/usr/bin/env python3

import sys
import os
import time
import argparse

# Add parent directory to path so we can import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MOTOR_PINS
import RPi.GPIO as GPIO

class MotorTester:
    def __init__(self):
        self.setup_gpio()
    
    def setup_gpio(self):
        """Initialize GPIO settings"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Set up all motor pins
        for slot, pins in MOTOR_PINS.items():
            GPIO.setup(pins['forward'], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(pins['reverse'], GPIO.OUT, initial=GPIO.LOW)
        
        print("GPIO initialized successfully")
    
    def test_motor(self, slot, direction, duration):
        """Test a specific motor
        
        Args:
            slot (int): Motor slot number (1-9)
            direction (str): 'forward' or 'reverse'
            duration (float): Duration to run the motor in seconds
        """
        if slot not in MOTOR_PINS:
            print(f"Error: Invalid slot number {slot}. Valid slots are {list(MOTOR_PINS.keys())}")
            return False
            
        pin = MOTOR_PINS[slot][direction]
        print(f"Testing motor {slot} ({direction}) on GPIO pin {pin} for {duration} seconds...")
        
        try:
            # Ensure pin starts LOW
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.1)
            
            # Activate motor
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(duration)
            
            # Stop motor
            GPIO.output(pin, GPIO.LOW)
            
            print(f"Test completed for motor {slot}")
            return True
            
        except Exception as e:
            print(f"Error testing motor: {e}")
            return False
        
    def cleanup(self):
        """Clean up GPIO settings"""
        try:
            GPIO.cleanup()
            print("GPIO cleaned up successfully")
        except Exception as e:
            print(f"Error during cleanup: {e}")

def interactive_mode():
    """Run the motor tester in interactive mode"""
    tester = MotorTester()
    
    try:
        while True:
            print("\nMotor Tester Interactive Mode")
            print("-" * 30)
            print("Available slots:", list(MOTOR_PINS.keys()))
            print("\nCommands:")
            print("  test <slot> <direction> <duration>")
            print("  list - Show available motors")
            print("  quit - Exit the program")
            
            cmd = input("\nEnter command: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "list":
                print("\nAvailable Motors:")
                for slot in MOTOR_PINS:
                    print(f"Slot {slot}: Forward pin {MOTOR_PINS[slot]['forward']}, "
                          f"Reverse pin {MOTOR_PINS[slot]['reverse']}")
            elif cmd.startswith("test"):
                try:
                    parts = cmd.split()
                    if len(parts) != 4:
                        print("Usage: test <slot> <direction> <duration>")
                        continue
                        
                    _, slot, direction, duration = parts
                    slot = int(slot)
                    duration = float(duration)
                    
                    if direction not in ['forward', 'reverse']:
                        print("Direction must be 'forward' or 'reverse'")
                        continue
                        
                    tester.test_motor(slot, direction, duration)
                    
                except ValueError:
                    print("Invalid input. Slot must be a number and duration must be a number in seconds")
            else:
                print("Unknown command")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        tester.cleanup()

def main():
    parser = argparse.ArgumentParser(description='Test vending machine motors individually')
    parser.add_argument('-s', '--slot', type=int, help='Motor slot number to test (1-9)')
    parser.add_argument('-d', '--direction', choices=['forward', 'reverse'], help='Motor direction')
    parser.add_argument('-t', '--time', type=float, default=1.0, help='Test duration in seconds')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.slot and args.direction:
        tester = MotorTester()
        try:
            tester.test_motor(args.slot, args.direction, args.time)
        finally:
            tester.cleanup()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()