#!/usr/bin/env python3
"""
USB Thermal Printer Diagnostic Tool (ESC/POS over serial)

Usage:
  python tools/test_printer_usb.py [--port /dev/ttyUSB0] [--baud 9600]

What it does:
- Opens the serial port to the thermal printer
- Sends initialize, prints a sample test receipt, feeds lines, and cuts paper
- Shows detailed errors and hints to fix common issues

Make sure:
- The device node is correct (e.g., /dev/ttyUSB0 or /dev/ttyUSB1)
- You have permissions to access the port (dialout group)
- Baudrate matches the printer (commonly 9600 or 19200)
"""

import argparse
import sys
import time

try:
    import serial  # type: ignore
except Exception:
    print("pyserial is not installed. Install with: pip install pyserial")
    sys.exit(1)


def open_printer(path: str, baud: int) -> serial.Serial:
    try:
        ser = serial.Serial(
            port=path,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            write_timeout=2,
        )
        return ser
    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port {path}: {e}")
        print("Hints: \n- Check device path (ls /dev/ttyUSB*)\n- Check permissions (sudo usermod -aG dialout $USER)\n- Ensure no other process is using the port (sudo lsof /dev/ttyUSB0)")
        raise


def escpos_test(ser: serial.Serial):
    init = b"\x1b\x40"  # Initialize
    bold_on = b"\x1b\x45\x01"
    bold_off = b"\x1b\x45\x00"
    align_center = b"\x1b\x61\x01"
    align_left = b"\x1b\x61\x00"
    feed_4 = b"\x1b\x64\x04"  # feed 4 lines
    cut_full = b"\x1d\x56\x42\x00"

    ser.write(init)
    ser.write(align_center)
    ser.write(bold_on)
    ser.write("Thermal Printer Test\n".encode("utf-8"))
    ser.write(bold_off)
    ser.write("ESC/POS Sample\n".encode("utf-8"))
    ser.write(align_left)

    # Check character sets
    ser.write("\nUTF-8 Characters test:\n".encode("utf-8"))
    ser.write("- Rupee: \xe2\x82\xb9\n".encode("utf-8"))  # may not render if font unsupported
    ser.write("- Degree: \xc2\xb0C\n".encode("utf-8"))

    # Print timestamp
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    ser.write(f"\nPrinted at: {ts}\n".encode("utf-8"))

    ser.write(feed_4)
    ser.flush()
    time.sleep(0.3)
    ser.write(cut_full)
    ser.flush()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', default='/dev/ttyUSB0', help='Serial device path for printer')
    ap.add_argument('--baud', type=int, default=9600, help='Baudrate, e.g., 9600 or 19200')
    args = ap.parse_args()

    print(f"[INFO] Opening printer at {args.port} @ {args.baud}...")
    try:
        ser = open_printer(args.port, args.baud)
    except Exception:
        sys.exit(1)

    try:
        escpos_test(ser)
        print("[INFO] Test sent. If nothing printed, check: port, baudrate, cable, and ESC/POS compatibility.")
    except Exception as e:
        print(f"[ERROR] Printing failed: {e}")
    finally:
        try:
            ser.close()
        except Exception:
            pass
        print("[INFO] Serial port closed.")
