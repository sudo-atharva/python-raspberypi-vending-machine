import serial
from config import SCANNER_PORT, SCANNER_BAUDRATE

def scan_barcode():
    """Scan barcode using the GM812L scanner."""
    try:
        ser = serial.Serial(SCANNER_PORT, SCANNER_BAUDRATE, timeout=5)
        barcode = ser.readline().decode('utf-8').strip()
        ser.close()
        return barcode if barcode else None
    except Exception as e:
        print(f"Scanner error: {e}")
        return None

def wait_for_scan():
    """Wait for a barcode scan and return the ID."""
    print("Please scan your barcode...")
    barcode = scan_barcode()
    while not barcode:
        barcode = scan_barcode()
    return barcode