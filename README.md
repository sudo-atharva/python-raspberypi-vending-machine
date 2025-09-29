# Medicine Vending Machine

A Raspberry Pi-based automated medicine vending machine with touchscreen interface, barcode scanning, and receipt printing capabilities.

## Project Overview

This project implements a smart medicine vending machine that allows users to:
- Authenticate using barcode ID cards or manually enter ID on the touchscreen
- Select medicines through a touchscreen interface
- Get medicine recommendations through a questionnaire
- Dispense medicines automatically using motor control
- Complete payment on-screen with a QR code (touchscreen only; QR is not printed on receipt)
- Receive printed receipts for transactions

## Hardware Requirements

1. Raspberry Pi (3 or 4 recommended)
2. Touchscreen Display (800x480 resolution)
3. GM812L Barcode Scanner (serial)
4. Thermal Receipt Printer (USB)
5. DC Motors for dispensing connected to l293d motor driver. two motor for each l293d motor driver with forward/reverse funtionality
6. GPIO connections for motor control
7. Power supply unit
8. Medicine storage compartments/slots

## Software Requirements

### System Requirements
- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- Git (for cloning the repository)

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required Python packages:
- RPi.GPIO - For GPIO control
- pyserial - For barcode scanner and printer communication
- tkinter - For GUI implementation
- Pillow - For image display of QR on the touchscreen
- json - For data storage (included in Python standard library)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sudo-atharva/python-raspberypi-vending-machine.git
cd python-raspberypi-vending-machine
```

2. Install required packages:
```bash
pip install RPi.GPIO pyserial
```

3. Configure hardware ports in `config.py`:
   - Set correct USB ports for printer and scanner
   - Verify GPIO pin assignments for motors
   - Adjust screen resolution if needed

4. Set up data files:
   - Ensure all JSON files are present in `data/`
   - Update `medicines.json` with your inventory (include a numeric price field)
   - Add authorized users to `users.json`
   - Customize `questionnaire.json` if needed
   - Ensure the static QR image exists at `assets/images/qr.jpg` (this is shown on the payment screen). The receipt will not include the QR image.

## Project Structure

```
medicine_vending_machine/
├── config.py           # Configuration settings
├── database.py        # Data management functions
├── gui.py            # Touchscreen interface
├── main.py           # Main program entry point
├── motor_control.py  # Motor control functions
├── printer.py        # Receipt printer functions
├── scanner.py        # Barcode scanner functions
├── assets/           # Static assets
│   └── images/       # UI images
└── data/            # Data storage
    ├── medicines.json       # Medicine inventory
    ├── questionnaire.json   # Symptom questionnaire
    ├── transactions.log     # Transaction history
    └── users.json          # Authorized users
```

## Configuration

### Motor Configuration
In `config.py`, configure GPIO pins for each slot:
```python
MOTOR_PINS = {
    1: {'forward': 17, 'reverse': 18},
    2: {'forward': 19, 'reverse': 20},
    # ... configure all slots
}
```

### Hardware Ports
Configure serial ports in `config.py`:
```python
PRINTER_PORT = '/dev/ttyUSB0'
PRINTER_BAUDRATE = 9600
SCANNER_PORT = '/dev/ttyACM0'
SCANNER_BAUDRATE = 9600
```

### Display Settings
Set screen resolution in `config.py`:
```python
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
```

## Usage

1. Start the application:
```bash
python main.py
```

2. System Operation:
   - Welcome screen appears on startup (kiosk mode fullscreen, closing is disabled)
   - User scans their ID card or taps "Enter ID Manually" to enter via on-screen keypad
   - System validates user credentials
   - User can:
     - Select medicine directly from catalog
     - Use questionnaire for recommendations
   - Machine dispenses selected medicine
   - Payment screen shows total amount and displays the QR image from `assets/images/qr.jpg`
   - After tapping "Paid":
     - A CSV entry is appended to `data/payments.csv` with id, medicine, amount, date, time
     - A thermal receipt is printed (without QR image)
   - Thank you screen is shown

## Data Management

### Medicine Inventory
Edit `medicines.json` to manage inventory:
```json
{
    "1": {
        "name": "Medicine Name",
        "description": "Description",
        "slot": 1,
        "price": 5.0
    }
}
```

### User Management
Add/edit users in `users.json`:
```json
{
    "12345": {
        "name": "User Name",
        "id": "12345"
    }
}
```

### Transaction Logging
- All transactions are automatically logged to `transactions.log`
- Format: `timestamp: User <id> dispensed <medicine> from slot <slot>`

## Safety Features

1. User Authentication
   - Barcode scanning ensures only authorized access
   - User data validation before dispensing

2. Motor Control
   - Precise timing for accurate dispensing
   - Emergency stop capability
   - GPIO cleanup on program exit

3. Error Handling
   - Invalid user detection
   - Hardware communication errors
   - Out-of-stock detection

## Maintenance

1. Regular Tasks:
   - Check and refill medicine slots
   - Review transaction logs
   - Clean barcode scanner
   - Test motor operation
   - Verify printer paper supply

2. System Updates:
   - Update medicine inventory in `medicines.json`
   - Maintain user database in `users.json`
   - Update questionnaire as needed
   - Check for software updates

## Troubleshooting

1. Scanner Issues:
   - Verify USB connection
   - Check port configuration (SCANNER_PORT) and baudrate (SCANNER_BAUDRATE)
   - Clean scanner surface
   - Test with known working barcodes
   - Use the included diagnostic: `python tools/test_scanner_gm812l.py --port /dev/ttyACM0 --baud 9600`

2. Printer Problems:
   - Check paper supply
   - Verify serial connection
   - Test printer separately
   - Check baudrate settings

3. Motor Issues:
   - Verify GPIO connections
   - Check power supply
   - Test individual motors
   - Verify pin configurations

4. Kiosk Mode / Lockdown:
   - The app runs in fullscreen; window close and common quit keybindings are disabled.
   - To exit during development, modify gui.py to remove the kiosk bindings or run in a regular window.

4. Display Problems:
   - Check resolution settings
   - Verify touchscreen drivers
   - Test display connection
   - Calibrate if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and support:
- Create an issue on GitHub
- Contact: [Your Contact Information]
- Documentation: [Link to additional documentation if available]
