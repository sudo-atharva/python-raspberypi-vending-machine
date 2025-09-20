import csv
import time
import RPi.GPIO as GPIO

# Motor GPIO Pins
MOTOR_PIN1 = 17  # Change as per your wiring
MOTOR_PIN2 = 27  # Change as per your wiring

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)

# Function to run motor for specified rotations
def run_motor(rotations, delay=1):
    for _ in range(rotations):
        GPIO.output(MOTOR_PIN1, GPIO.HIGH)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        time.sleep(delay)  # Run motor for delay seconds per rotation
        GPIO.output(MOTOR_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        time.sleep(0.5)  # Pause between rotations

# Function to read rotations from CSV file
def get_rotations_from_csv(file_path):
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    return int(row[0])  # Assuming first column has rotation count
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return 5  # Default to 5 rotations if error occurs

# CSV file path
csv_file = "rotations.csv"  # Change to the actual path

# Get rotations from CSV
rotations = get_rotations_from_csv(csv_file)
print(f"Running motor for {rotations} rotations")

# Run motor
run_motor(rotations)

# Cleanup GPIO
GPIO.cleanup()