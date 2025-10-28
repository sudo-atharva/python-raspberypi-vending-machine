import RPi.GPIO as GPIO
import time
import atexit
from config import MOTOR_PINS

# Global variable to track if GPIO is initialized
_gpio_initialized = False

def _init_gpio():
    """Initialize GPIO pins if not already initialized."""
    global _gpio_initialized
    if not _gpio_initialized:
        try:
            # Set GPIO mode and disable warnings
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup motor pins as outputs
            for slot, pins in MOTOR_PINS.items():
                GPIO.setup(pins['forward'], GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(pins['reverse'], GPIO.OUT, initial=GPIO.LOW)
            
            _gpio_initialized = True
            print("GPIO initialized successfully")
        except Exception as e:
            print(f"Error initializing GPIO: {e}")
            _gpio_initialized = False
    return _gpio_initialized

def dispense(slot_id, direction='forward', duration=1.0):
    """Dispense medicine from the specified slot."""
    if not _init_gpio():
        print("Failed to initialize GPIO")
        return False
        
    if slot_id not in MOTOR_PINS:
        print(f"Invalid slot ID: {slot_id}")
        return False

    try:
        pins = MOTOR_PINS[slot_id]
        pin = pins.get(direction)
        
        if pin is None:
            print(f"Invalid direction: {direction}")
            return False
            
        print(f"Dispensing from slot {slot_id} ({direction}) for {duration} seconds...")
        
        # Ensure pin is LOW before starting
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.1)  # Small delay to ensure clean start
        
        # Activate motor
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        
        # Ensure pin is turned off
        GPIO.output(pin, GPIO.LOW)
        
        print(f"Successfully dispensed from slot {slot_id}")
        return True
        
    except Exception as e:
        print(f"Error during dispensing: {e}")
        # Try to clean up GPIO on error
        try:
            GPIO.cleanup()
        except:
            pass
        return False

def cleanup():
    """Clean up GPIO pins."""
    global _gpio_initialized
    try:
        if _gpio_initialized:
            GPIO.cleanup()
            _gpio_initialized = False
            print("GPIO cleaned up successfully")
    except Exception as e:
        print(f"Error during GPIO cleanup: {e}")

# Register cleanup to be called on program exit
atexit.register(cleanup)