#!/usr/bin/env python3

import sys
import os
import time
import RPi.GPIO as GPIO
from config import MOTOR_PINS

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
        
        print("GPIO ready!")
    
    def test_motor(self, slot, direction, duration):
        """Test a specific motor"""
        if slot not in MOTOR_PINS:
            print(f"Error: Invalid motor number {slot}. Choose from {list(MOTOR_PINS.keys())}")
            return False
            
        direction_full = 'forward' if direction.lower().startswith('f') else 'reverse'
        pin = MOTOR_PINS[slot][direction_full]
        
        print(f"Running motor {slot} {direction_full} for {duration} seconds...")
        
        try:
            # Start motor
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(duration)
            
            # Stop motor
            GPIO.output(pin, GPIO.LOW)
            print("Done!")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
        
    def cleanup(self):
        """Clean up GPIO settings"""
        try:
            GPIO.cleanup()
            print("GPIO cleaned up successfully")
        except Exception as e:
            print(f"Error during cleanup: {e}")

def show_help():
    print("\nUsage: python test_motors.py [motor] [direction] [seconds]")
    print("\nExample commands:")
    print("  python test_motors.py 1 f 10    # Run motor 1 forward for 10 seconds")
    print("  python test_motors.py 2 r 5     # Run motor 2 reverse for 5 seconds")
    print("\nParameters:")
    print("  motor: 1-9")
    print("  direction: f (forward) or r (reverse)")
    print("  seconds: how long to run")
    print("\nOr just run without parameters for interactive mode")
    print("\nAvailable motors:", list(MOTOR_PINS.keys()))

def main():
    tester = MotorTester()
    
    try:
        if len(sys.argv) == 1:
            # Interactive mode
            print("\nMotor Tester - Interactive Mode")
            print("Enter commands like: 1 f 10")
            print("  1-9: motor number")
            print("  f/r: forward/reverse")
            print("  seconds to run")
            print("\nType 'q' to quit, 'h' for help")
            
            while True:
                try:
                    cmd = input("\nCommand: ").strip().lower()
                    
                    if cmd == 'q':
                        break
                    elif cmd == 'h':
                        show_help()
                        continue
                    
                    parts = cmd.split()
                    if len(parts) != 3:
                        print("Please use format: 1 f 10")
                        continue
                    
                    motor = int(parts[0])
                    direction = parts[1]
                    seconds = float(parts[2])
                    
                    if direction not in ['f', 'r']:
                        print("Direction must be 'f' for forward or 'r' for reverse")
                        continue
                    
                    tester.test_motor(motor, direction, seconds)
                    
                except ValueError:
                    print("Invalid input. Use format: 1 f 10")
                except KeyboardInterrupt:
                    break
        
        elif len(sys.argv) == 4:
            # Command line mode
            try:
                motor = int(sys.argv[1])
                direction = sys.argv[2].lower()
                seconds = float(sys.argv[3])
                
                if direction not in ['f', 'r']:
                    print("Direction must be 'f' for forward or 'r' for reverse")
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