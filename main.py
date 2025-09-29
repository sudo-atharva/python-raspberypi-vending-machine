from gui import VendingGUI
from motor_control import cleanup
import atexit


def main():
    """Main entry point for the medicine vending machine."""
    # Register cleanup function
    atexit.register(cleanup)

    # Initialize and start GUI; user authentication handled within GUI
    gui = VendingGUI()
    gui.mainloop()


if __name__ == "__main__":
    main()
