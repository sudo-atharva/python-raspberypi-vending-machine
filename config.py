import os

# Directory paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')

# Data files
MEDICINES_FILE = os.path.join(DATA_DIR, 'medicines.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
QUESTIONNAIRE_FILE = os.path.join(DATA_DIR, 'questionnaire.json')

# Motor GPIO pins (BCM mode)
# Each slot has forward and reverse pins
# All motors except 5 have swapped pins to fix direction
MOTOR_PINS = {
    1: {'forward': 18, 'reverse': 17},  # Pin 12, Pin 11
    2: {'forward': 22, 'reverse': 27},  # Pin 15, Pin 13
    3: {'forward': 24, 'reverse': 23},  # Pin 18, Pin 16
    4: {'forward': 9,  'reverse': 10},  # Pin 21, Pin 19
    5: {'forward': 25, 'reverse': 11},  # Pin 22, Pin 23 (unchanged)
    6: {'forward': 7,  'reverse': 8},   # Pin 26, Pin 24
    9: {'forward': 6,  'reverse': 5},   # Pin 31, Pin 29
    7: {'forward': 13, 'reverse': 12},  # Pin 33, Pin 32
    8: {'forward': 26, 'reverse': 16},  # Pin 37, Pin 36
}

# Printer configuration
PRINTER_PORT = '/dev/usb/lp0'  # Adjust based on actual port
PRINTER_BAUDRATE = 9600

# Barcode scanner configuration
SCANNER_PORT = '/dev/ttyACM0'  # Adjust based on actual port
SCANNER_BAUDRATE = 9600

# Touchscreen display size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Other settings
LOG_FILE = os.path.join(DATA_DIR, 'transactions.log')