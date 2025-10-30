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
# NOTE: remapped so logical slot numbers (1..9) point to the physical motor pins
# according to the mapping you provided.
MOTOR_PINS = {
    # Logical 1 maps to physical 8's pins
    1: {'forward': 12, 'reverse': 13},  # physical 8
    # Logical 2 maps to physical 8 as well
    2: {'forward': 12, 'reverse': 13},  # physical 8
    # Logical 3 -> physical 7
    3: {'forward': 5,  'reverse': 6},   # physical 7
    # Logical 4 -> physical 6
    4: {'forward': 8,  'reverse': 7},   # physical 6
    # Logical 5 -> physical 4
    5: {'forward': 10, 'reverse': 9},   # physical 4
    # Logical 6 -> physical 5
    6: {'forward': 25, 'reverse': 11},  # physical 5
    # Logical 7 -> physical 3
    7: {'forward': 23, 'reverse': 24},  # physical 3
    # Logical 8 -> physical 2
    8: {'forward': 27, 'reverse': 22},  # physical 2
    # Logical 9 -> physical 1
    9: {'forward': 17, 'reverse': 18},  # physical 1
}

# Optional explicit mapping with inversion flags (from your calibration/observations)
# Use this if other parts of code want to know whether logical-forward produces
# physical-forward or whether commands must be inverted.
MOTOR_MAP = {
    1: {'physical': 8, 'invert': True},
    2: {'physical': 8, 'invert': False},
    3: {'physical': 7, 'invert': True},
    4: {'physical': 6, 'invert': False},
    5: {'physical': 4, 'invert': True},
    6: {'physical': 5, 'invert': False},
    7: {'physical': 3, 'invert': False},
    8: {'physical': 2, 'invert': True},
    9: {'physical': 1, 'invert': True},
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