#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
from config import MOTOR_PINS

def setup_gpio():
    """Initialize GPIO settings"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Set up all motor pins
    for slot, pins in MOTOR_PINS.items():
        GPIO.setup(pins['forward'], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins['reverse'], GPIO.OUT, initial=GPIO.LOW)
    
    print("GPIO ready!")

def run_motor_forward(slot, duration=5):
    """Run a motor forward for the specified duration"""
    # Get the forward pin for this slot
    pin = MOTOR_PINS[slot]['forward']
    
    print(f"Running motor {slot} forward...")
    try:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)
        print(f"Motor {slot} complete!")
    except Exception as e:
        print(f"Error running motor {slot}: {e}")
        GPIO.output(pin, GPIO.LOW)  # Safety: ensure motor is stopped

def main():
    try:
        setup_gpio()
        print("\nStarting sequential forward test of all motors")
        print("Motor layout (pin numbers):")
        print(" Motor 1: BCM 17 (forward), 18 (reverse)")
        print(" Motor 2: BCM 27 (forward), 22 (reverse)")
        print(" Motor 3: BCM 23 (forward), 24 (reverse)")
        print(" Motor 4: BCM 10 (forward), 9  (reverse)")
        print(" Motor 5: BCM 25 (forward), 11 (reverse)")
        print(" Motor 6: BCM 8  (forward), 7  (reverse)")
        print(" Motor 7: BCM 5  (forward), 6  (reverse)")
        print(" Motor 8: BCM 12 (forward), 13 (reverse)")
        print(" Motor 9: BCM 16 (forward), 26 (reverse)")
        print("\nWill run each motor forward for 5 seconds...")
        
        input("Press Enter to begin...")
        
        # Run motors 1 through 9 in sequence
        for slot in range(1, 10):
            print(f"\nStarting motor {slot}")
            run_motor_forward(slot)
            # Short pause between motors
            time.sleep(1)
            
        print("\nTest complete!")
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main()