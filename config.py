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
# Physical layout (7,8,9 / 4,5,6 / 1,2,3):
#  [7][8][9]    PIN Mapping Reference:
#  [4][5][6]    Slot 1: BCM 17,18  (Pin 11,12)
#  [1][2][3]    Slot 2: BCM 27,22  (Pin 13,15)
#                Slot 3: BCM 23,24  (Pin 16,18)
#                Slot 4: BCM 10,9   (Pin 19,21)
#                Slot 5: BCM 25,11  (Pin 22,23)
#                Slot 6: BCM 8,7    (Pin 24,26)
#                Slot 7: BCM 5,6    (Pin 29,31)
#                Slot 8: BCM 12,13  (Pin 32,33)
#                Slot 9: BCM 16,26  (Pin 36,37)

MOTOR_PINS = {
    # Each logical slot points to its corresponding physical motor's pins
    1: {'forward': 17, 'reverse': 18},  # physical 1
    2: {'forward': 12, 'reverse': 13},  # physical 8
    3: {'forward': 5,  'reverse': 6},   # physical 7
    4: {'forward': 10, 'reverse': 9},   # physical 4
    5: {'forward': 25, 'reverse': 11},  # physical 5
    6: {'forward': 8,  'reverse': 7},   # physical 6
    7: {'forward': 23, 'reverse': 24},  # physical 3
    8: {'forward': 27, 'reverse': 22},  # physical 2
    9: {'forward': 27, 'reverse': 22},  # physical 2 (shared with logical 8)
}

# Maps logical slots to physical slots and direction inversion.
# Physical layout visualization:
#  [7][8][9]
#  [4][5][6]
#  [1][2][3]
MOTOR_MAP = {
    1: {'physical': 1, 'invert': False},
    2: {'physical': 8, 'invert': False},
    3: {'physical': 7, 'invert': False},
    4: {'physical': 4, 'invert': True},
    5: {'physical': 5, 'invert': True},
    6: {'physical': 6, 'invert': False},
    7: {'physical': 3, 'invert': False},
    8: {'physical': 2, 'invert': False},
    9: {'physical': 2, 'invert': False},  # Shares physical motor 2 with logical 8
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