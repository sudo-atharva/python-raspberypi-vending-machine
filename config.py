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
    1: {'forward': 17, 'reverse': 18},
    2: {'forward': 19, 'reverse': 20},
    3: {'forward': 21, 'reverse': 22},
    4: {'forward': 23, 'reverse': 24},
    5: {'forward': 25, 'reverse': 26},
    6: {'forward': 27, 'reverse': 28},
    7: {'forward': 29, 'reverse': 30},
    8: {'forward': 31, 'reverse': 32},
    9: {'forward': 33, 'reverse': 34},
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