import serial
import time
import re
from typing import Optional
from config import SCANNER_PORT, SCANNER_BAUDRATE

CONTROL_CHARS_RE = re.compile(r"[\x00-\x1F\x7F]")


def _open_serial(port: str, baud: int, timeout: float = 1.0) -> serial.Serial:
    """Open serial port with robust defaults for GM812L.

    GM812L typically enumerates as /dev/ttyACM0 or /dev/ttyUSB0 and uses 9600-8N1.
    """
    return serial.Serial(
        port=port,
        baudrate=baud,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout,
        write_timeout=1.0,
    )


def scan_barcode_once(timeout: float = 2.0) -> Optional[str]:
    """Open the scanner, read a single line, clean it, and return the code or None."""
    try:
        with _open_serial(SCANNER_PORT, SCANNER_BAUDRATE, timeout=timeout) as ser:
            raw = ser.readline()
            if not raw:
                return None
            try:
                text = raw.decode('utf-8', errors='replace')
            except Exception:
                text = raw.decode('latin1', errors='replace')
            text = CONTROL_CHARS_RE.sub('', text).strip()
            return text or None
    except Exception as e:
        print(f"Scanner error: {e}")
        return None


def wait_for_scan(poll_interval: float = 0.2) -> str:
    """Block until a non-empty scan is read. Use small sleeps to avoid CPU spin."""
    print("Please scan your barcode...")
    while True:
        code = scan_barcode_once(timeout=1.0)
        if code:
            return code
        time.sleep(poll_interval)