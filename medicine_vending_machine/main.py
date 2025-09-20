from scanner import wait_for_scan
from database import get_user_by_id
from gui import VendingGUI
from motor_control import cleanup
import atexit

def main():
    """Main entry point for the medicine vending machine."""
    # Register cleanup function
    atexit.register(cleanup)

    # Initialize GUI
    gui = VendingGUI()

    # Scan barcode for user identification
    barcode = wait_for_scan()
    user = get_user_by_id(barcode)

    if user:
        gui.show_catalog(user)
    else:
        gui.show_error("Invalid ID")

    # Start GUI event loop
    gui.mainloop()

if __name__ == "__main__":
    main()