#!/usr/bin/env python3
"""
GM812L Barcode Scanner Diagnostic Tool

Usage:
  python tools/test_scanner_gm812l.py [--port /dev/ttyACM0] [--baud 9600]

Features:
- Opens the serial port and continuously reads lines
- Prints raw bytes and UTF-8 decoded text
- Shows timing and length of frames
- Handles common errors and provides remediation hints
- Exits with Ctrl+C

Notes:
- Ensure the user is in the 'dialout' group on Debian/Raspberry Pi: sudo usermod -aG dialout $USER
- You may need to replug the scanner after adding group membership and log out/in.
- Try different device nodes (e.g., /dev/ttyACM0, /dev/ttyUSB0) depending on how the device enumerates.
"""

import argparse
import sys
import time
from typing import Optional

try:
    import serial  # type: ignore
except Exception as e:  # pragma: no cover
    print("pyserial is not installed. Install with: pip install pyserial", file=sys.stderr)
    sys.exit(1)


def open_port(path: str, baud: int) -> serial.Serial:
    try:
        ser = serial.Serial(path, baudrate=baud, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port {path}: {e}")
        print("Hints: \n- Check device path (ls /dev/ttyACM* /dev/ttyUSB*)\n- Check permissions (id; groups; add to dialout group)\n- Ensure no other process is using the port (lsof)")
        raise


def decode_bytes(data: bytes) -> str:
    try:
        return data.decode('utf-8', errors='replace').strip()
    except Exception:
        return data.hex(' ')


def run(path: str, baud: int) -> None:
    print(f"[INFO] Opening {path} @ {baud} baud...")
    ser = open_port(path, baud)
    print("[INFO] Port opened. Waiting for scans... Press Ctrl+C to exit.")
    try:
        while True:
            t0 = time.monotonic()
            line = ser.readline()  # reads until \n or timeout
            dt = time.monotonic() - t0
            if not line:
                continue
            decoded = decode_bytes(line)
            print(f"[FRAME] {len(line)} bytes in {dt*1000:.1f} ms | raw={line!r} | text='{decoded}'")
    except KeyboardInterrupt:
        print("\n[INFO] Exiting on user request")
    finally:
        try:
            ser.close()
            print("[INFO] Serial port closed.")
        except Exception:
            pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', default='/dev/ttyACM0', help='Serial device path')
    ap.add_argument('--baud', type=int, default=9600, help='Baudrate')
    args = ap.parse_args()
    run(args.port, args.baud)
