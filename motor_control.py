import RPi.GPIO as GPIO
import time
from config import MOTOR_PINS

GPIO.setmode(GPIO.BCM)

# Setup motor pins as outputs
for slot, pins in MOTOR_PINS.items():
    GPIO.setup(pins['forward'], GPIO.OUT)
    GPIO.setup(pins['reverse'], GPIO.OUT)

def dispense(slot_id, direction='forward', duration=1.0):
    """Dispense medicine from the specified slot."""
    if slot_id not in MOTOR_PINS:
        print(f"Invalid slot ID: {slot_id}")
        return False

    pins = MOTOR_PINS[slot_id]
    pin = pins[direction]

    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)

    print(f"Dispensed from slot {slot_id} ({direction})")
    return True

def cleanup():
    """Clean up GPIO pins."""
    GPIO.cleanup()