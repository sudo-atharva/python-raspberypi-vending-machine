import serial
from datetime import datetime
from config import PRINTER_PORT, PRINTER_BAUDRATE

def print_receipt(user_id, user_name, medicine_name, slot_id):
    """Print receipt using thermal printer."""
    try:
        ser = serial.Serial(PRINTER_PORT, PRINTER_BAUDRATE, timeout=1)

        # ESC/POS commands for basic formatting
        init_printer = b'\x1b\x40'  # Initialize printer
        cut_paper = b'\x1d\x56\x42\x00'  # Cut paper

        receipt_text = f"""
Medicine Vending Machine Receipt

User ID: {user_id}
Name: {user_name}
Medicine: {medicine_name}
Slot: {slot_id}
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Thank you for using our service!
"""

        ser.write(init_printer)
        ser.write(receipt_text.encode('utf-8'))
        ser.write(cut_paper)
        ser.close()

        print("Receipt printed successfully.")
    except Exception as e:
        print(f"Printer error: {e}")