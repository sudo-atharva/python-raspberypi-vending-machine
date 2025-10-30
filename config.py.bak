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
MOTOR_PINS = {
    1: {'forward': 17, 'reverse': 18},  # Pin 11, Pin 12
    2: {'forward': 27, 'reverse': 22},  # Pin 13, Pin 15
    3: {'forward': 23, 'reverse': 24},  # Pin 16, Pin 18
    4: {'forward': 10, 'reverse': 9},   # Pin 19, Pin 21
    5: {'forward': 25, 'reverse': 11},  # Pin 22, Pin 23
    6: {'forward': 8, 'reverse': 7},    # Pin 24, Pin 26
    7: {'forward': 5, 'reverse': 6},    # Pin 29, Pin 31
    8: {'forward': 12, 'reverse': 13},  # Pin 32, Pin 33
    9: {'forward': 16, 'reverse': 26},  # Pin 36, Pin 37
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