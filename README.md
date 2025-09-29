# Medicine Vending Machine

A Raspberry Pi-based automated medicine vending machine with touchscreen interface, barcode scanning, and receipt printing capabilities.

## Project Overview

This project implements a smart medicine vending machine that allows users to:
- Authenticate using barcode ID cards
- Select medicines through a touchscreen interface
- Get medicine recommendations through a questionnaire
- Receive printed receipts for transactions
- Dispense medicines automatically using motor control

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
   - Ensure all JSON files are present in `medicine_vending_machine/data/`
   - Update `medicines.json` with your inventory
   - Add authorized users to `users.json`
   - Customize `questionnaire.json` if needed

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
cd medicine_vending_machine
python main.py
```

2. System Operation:
   - Welcome screen appears on startup
   - User scans their ID card
   - System validates user credentials
   - User can:
     - Select medicine directly from catalog
     - Use questionnaire for recommendations
   - Machine dispenses selected medicine
   - Receipt is printed automatically

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
   - Check port configuration
   - Clean scanner surface
   - Test with known working barcodes

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
