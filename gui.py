import os
import csv
import tkinter as tk
from datetime import datetime
from typing import Optional
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Set modern theme colors
PRIMARY = "#4a6fa5"
SECONDARY = "#6c757d"
SUCCESS = "#28a745"
DANGER = "#dc3545"
LIGHT = "#f8f9fa"
DARK = "#343a40"

from config import SCREEN_WIDTH, SCREEN_HEIGHT, PRINTER_PORT, PRINTER_BAUDRATE
from database import (
    load_medicines,
    load_questionnaire,
    log_transaction,
    get_user_by_id,
)
from motor_control import dispense


# Existing printer module prints a basic receipt; we provide a local version that also includes amount
# without changing other files.

def print_order_receipt(user_id: str, user_name: str, medicine_name: str, slot_id: int, amount: float) -> None:
    init_printer = b"\x1b\x40"  # Initialize printer
    feed_lines = b"\x1b\x64\x04"  # Print and feed n lines (n=4)
    cut_paper = b"\x1d\x56\x42\x00"  # Cut paper

    receipt_text = f"""
Medicine Vending Machine Receipt

User ID: {user_id}
Name: {user_name}
Medicine: {medicine_name}
Amount: ₹{amount:.2f}
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Thank you for your payment!
"""

    # Prefer direct USB printer device if available (/dev/usb/lp0), else fallback to serial
    target_path = PRINTER_PORT
    try:
        if os.path.exists(target_path) and target_path.startswith("/dev/usb/lp"):
            with open(target_path, "wb", buffering=0) as f:
                f.write(init_printer)
                f.write(receipt_text.replace("\r\n", "\n").encode("utf-8"))
                f.write(b"\n\n")
                f.write(feed_lines)
                f.write(cut_paper)
            print("Receipt printed successfully (usblp).")
            return
        # Serial fallback
        import serial  # Imported here to avoid dependency issues on non-RPi dev machines
        with serial.Serial(PRINTER_PORT, PRINTER_BAUDRATE, timeout=1, write_timeout=2) as ser:
            ser.write(init_printer)
            ser.write(receipt_text.replace("\r\n", "\n").encode("utf-8"))
            ser.write(b"\n\n")
            ser.write(feed_lines)
            ser.flush()
            try:
                import time as _t
                _t.sleep(0.2)
            except Exception:
                pass
            ser.write(cut_paper)
            ser.flush()
        print("Receipt printed successfully (serial).")
    except Exception as e:  # pragma: no cover
        print(f"Printer error: {e}")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def generate_qr_image(data: str, out_path: str, size: int = 240) -> str:
    """Generate a QR code image for payment. Tries to use qrcode; falls back to a placeholder image."""
    # Try to use qrcode if available
    try:
        import qrcode  # type: ignore

        img = qrcode.make(data)
        img = img.resize((size, size))
        img.save(out_path)
        return out_path
    except Exception:
        # Fallback: draw a placeholder image
        img = Image.new("RGB", (size, size), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([4, 4, size - 4, size - 4], outline=(0, 0, 0), width=4)
        draw.text((10, size // 2 - 10), "Scan to Pay", fill=(0, 0, 0))
        img.save(out_path)
        return out_path


class VendingGUI(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Medicine Vending Machine")
        
        # Set default font and styling
        default_font = ('Arial', 18)  # Increased font size
        self.option_add('*TButton*Font', default_font)
        self.option_add('*TLabel*Font', default_font)
        
        # Configure styles for better performance and touch
        style = ttk.Style()
        
        # Base button style - simpler and faster
        style.configure('TButton', 
                      font=('Arial', 16),
                      padding=10,
                      relief='raised',
                      borderwidth=2)
        
        # Button variants with consistent sizing
        for btn_style in ['TButton', 'info.TButton', 'success.TButton', 'danger.TButton', 'secondary.TButton']:
            style.configure(btn_style,
                          font=('Arial', 16),
                          padding=15,
                          width=15)  # Fixed width for consistency
        
        # Hover effects for better feedback
        style.map('TButton',
                 foreground=[('active', 'white')],
                 background=[('active', '!disabled', '#4a7abc')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        # Specific style for large buttons
        style.configure('Large.TButton',
                      font=('Arial', 20, 'bold'),
                      padding=20,
                      width=20)
        
        # Disable animation for better performance
        style.configure('.',
                      relief='flat',
                      borderwidth=0,
                      focusthickness=3,
                      focuscolor='none')
        
        # Initialize variables
        self.current_user = None
        self.manual_id_var = tk.StringVar()
        self._qr_photo = None
        self.pending_medicine = None
        
        # Set up the main window
        self.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}+0+0")
        
        # Configure window properties
        self.title("Medicine Vending Machine")
        self.configure(background='white')
        
        # Create main container
        self.container = ttk.Frame(self)
        self.container.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Set up fullscreen mode
        self._is_fullscreen = True
        try:
            self.attributes("-fullscreen", True)
            self.attributes("-zoomed", True)  # Fallback for some systems
        except Exception as e:
            print(f"Warning: Could not set fullscreen: {e}")
        
        # Prevent window closing
        self.protocol("WM_DELETE_WINDOW", self.safe_exit)
        self.bind("<Escape>", lambda e: self.safe_exit())
        self.bind("<F11>", self._toggle_fullscreen_event)
        
        # Force focus to the window
        self.focus_force()
        
        # Show welcome screen with a small delay to ensure window is ready
        self.after(100, self.show_welcome)

    def clear_screen(self):
        """Clear all widgets from the window."""
        if not hasattr(self, 'container') or not self.container.winfo_exists():
            # Recreate container if it doesn't exist
            self.container = ttk.Frame(self)
            self.container.pack(fill=BOTH, expand=True)
            return
            
        # Safely destroy all child widgets
        for widget in self.container.winfo_children():
            try:
                if widget.winfo_exists():
                    widget.destroy()
            except Exception as e:
                print(f"Warning: Error destroying widget: {e}")
        
        # Force update to ensure widgets are destroyed
        self.update_idletasks()

    def show_welcome(self):
        """Display welcome screen with options to scan or enter ID manually."""
        # Reset user state first
        self.current_user = None
        self.pending_medicine = None
        
        # Clear and set up the main container
        self.clear_screen()
        
        # Ensure we have a valid container
        if not hasattr(self, 'container') or not self.container.winfo_exists():
            self.container = ttk.Frame(self)
            self.container.pack(fill=BOTH, expand=True)
        
        try:
            # Main container with padding
            main_frame = ttk.Frame(self.container, padding=20)
            main_frame.pack(fill=BOTH, expand=True)
            
            # Header
            header = ttk.Frame(main_frame)
            header.pack(fill=X, pady=(20, 10))
            
            title_label = ttk.Label(
                header, 
                text="Medicine Vending Machine", 
                font=('Arial', 24, 'bold'), 
                bootstyle='primary'
            )
            title_label.pack(pady=(0, 10))
            
            # Welcome message
            ttk.Label(
                main_frame,
                text="Welcome!",
                font=('Arial', 22, 'bold'),
                bootstyle='secondary'
            ).pack(pady=(10, 20))
            
            # Instruction
            ttk.Label(
                main_frame, 
                text="Please scan your barcode or enter your ID", 
                font=('Arial', 16),
                bootstyle='secondary'
            ).pack(pady=(0, 30))
            
            # Action buttons frame
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(expand=True, fill=BOTH, pady=10)
            
            # Scan button
            ttk.Button(
                btn_frame,
                text="📷 Scan Barcode",
                style='info.TButton',
                command=self.show_scan_instructions,
                padding=15
            ).pack(pady=10, fill=X)
            
            # Manual entry button
            ttk.Button(
                btn_frame,
                text="⌨️ Enter ID Manually",
                style='secondary.TButton',
                command=self.show_manual_id_entry,
                padding=15
            ).pack(pady=10, fill=X)
            
            # Add some space at the bottom
            ttk.Frame(btn_frame, height=20).pack()
            
        except Exception as e:
            print(f"Critical error in show_welcome: {str(e)}")
            # Last resort recovery
            try:
                # Try to completely reset the UI
                for widget in self.winfo_children():
                    widget.destroy()
                
                # Recreate the main container
                self.container = ttk.Frame(self)
                self.container.pack(fill=BOTH, expand=True)
                
                # Show minimal recovery UI
                ttk.Label(
                    self.container,
                    text="Welcome to Medicine Vending Machine",
                    font=('Arial', 20, 'bold'),
                    bootstyle='primary'
                ).pack(pady=50)
                
                ttk.Button(
                    self.container,
                    text="Start",
                    command=self.show_welcome,
                    style='info.TButton',
                    padding=15
                ).pack(pady=20)
                
            except Exception as inner_e:
                print(f"Fatal error during recovery: {str(inner_e)}")
                # If we get here, the UI is in an unrecoverable state
                self.destroy()
                self.quit()

    def show_scan_instructions(self):
        """Show simple scan instructions screen (placeholder for future auto-scan)."""
        self.clear_screen()
        
        # Create a frame in the container
        frame = ttk.Frame(self.container)
        frame.pack(expand=True)
        
        ttk.Label(
            frame,
            text="Scan your barcode now",
            font=("Arial", 22),
            bootstyle="primary"
        ).pack(pady=20)
        
        ttk.Label(
            frame,
            text="After scanning, the system will process your ID.",
            font=("Arial", 14)
        ).pack(pady=10)
        
        ttk.Button(
            frame,
            text="Back",
            command=self.show_welcome,
            style="secondary.TButton"
        ).pack(pady=20)

    def show_manual_id_entry(self):
        """Display on-screen keypad for manual ID entry."""
        self.clear_screen()
        
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Enter Your ID", font=('Arial', 22, 'bold')).pack(pady=10)
        
        # Entry field
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(pady=10)
        
        entry = ttk.Entry(entry_frame, 
                         textvariable=self.manual_id_var, 
                         font=('Arial', 20), 
                         justify="center",
                         width=15)
        entry.pack(pady=10)
        entry.focus_set()
        
        # Keypad
        keypad_frame = ttk.Frame(main_frame)
        keypad_frame.pack(pady=20)
        
        buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("Clear", 3, 0), ("0", 3, 1), ("⌫", 3, 2)
        ]
        
        for (text, r, c) in buttons:
            if text.isdigit():
                cmd = lambda t=text: self.append_digit(t)
                style = 'primary.TButton'
            elif text == "Clear":
                cmd = self.clear_id
                style = 'danger.TButton'
            else:  # backspace
                cmd = self.backspace_id
                style = 'warning.TButton'
                
            btn = ttk.Button(
                keypad_frame, 
                text=text, 
                style=style,
                width=6,
                command=cmd
            )
            btn.grid(row=r, column=c, padx=5, pady=5, ipadx=10, ipady=10)
        
        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="Submit",
            style='success.TButton',
            width=15,
            command=self.submit_manual_id
        ).grid(row=0, column=0, padx=10)
        
        ttk.Button(
            btn_frame,
            text="Back",
            style='secondary.TButton',
            width=15,
            command=self.show_welcome
        ).grid(row=0, column=1, padx=10)

    def append_digit(self, d):
        current = self.manual_id_var.get()
        self.manual_id_var.set(current + d)

    def backspace_id(self):
        current = self.manual_id_var.get()
        if current:
            self.manual_id_var.set(current[:-1])

    def clear_id(self):
        self.manual_id_var.set("")

    def _toggle_fullscreen_event(self, event=None):
        """Toggle fullscreen mode with F11 key."""
        self._is_fullscreen = not self._is_fullscreen
        try:
            self.attributes("-fullscreen", self._is_fullscreen)
            if not self._is_fullscreen:
                self.attributes("-zoomed", False)
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")

    def safe_exit(self, event=None):
        """Safely exit the application."""
        try:
            self.destroy()
        except:
            import os
            os._exit(0)

    def submit_manual_id(self):
        """Handle manual ID submission with better error handling."""
        try:
            # Get and clean the input
            user_id = self.manual_id_var.get().strip()
            
            # Validate input
            if not user_id:
                self.show_error("Please enter a valid ID")
                return
                
            # Ensure we have a valid container
            if not hasattr(self, 'container') or not self.container.winfo_exists():
                self.container = ttk.Frame(self)
                self.container.pack(fill=BOTH, expand=True)
            
            # Clear and show loading state
            self.clear_screen()
            
            # Create a new frame for loading content
            loading_frame = ttk.Frame(self.container)
            loading_frame.pack(expand=True, fill=BOTH)
            
            ttk.Label(
                loading_frame,
                text="Verifying ID...",
                font=('Arial', 18, 'bold'),
                bootstyle='info'
            ).pack(pady=50)
            
            # Force UI update
            self.update_idletasks()
            self.update()
            
            def process_id():
                try:
                    # Get user data
                    user = get_user_by_id(user_id)
                    if user:
                        # Store user data and show catalog
                        self.current_user = user
                        self.after(100, lambda: self.show_catalog(user))
                    else:
                        self.show_error("Invalid ID. Please try again.")
                        self.after(1000, self.show_manual_id_entry)
                except Exception as e:
                    print(f"Error processing ID: {str(e)}")
                    self.show_error("Error processing request. Please try again.")
                    self.after(1000, self.show_manual_id_entry)
            
            # Process ID in a separate thread to keep UI responsive
            import threading
            threading.Thread(target=process_id, daemon=True).start()
            
        except Exception as e:
            print(f"Fatal error in submit_manual_id: {str(e)}")
            self.show_error("A critical error occurred. Restarting...")
            self.after(1000, self.show_welcome)

    def show_catalog(self, user):
        """Display medicine catalog in a 3x3 grid for touchscreen."""
        def create_med_button(parent, med, row, col):
            """Create a medicine button with fixed size and touch-friendly padding."""
            frame = ttk.Frame(parent, padding=5)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
            
            btn_text = f"{med.get('name', 'Unknown')}\n₹{med.get('price', 0):.2f}"
            
            btn = ttk.Button(
                frame,
                text=btn_text,
                style='TButton',
                command=lambda m=med: self.select_medicine(m)
            )
            btn.pack(fill=BOTH, expand=True)
            return frame

        try:
            self.clear_screen()
            
            # Store user in instance variable if not already set
            if not hasattr(self, 'current_user') or not self.current_user:
                self.current_user = user
            
            # Main container with padding
            main_frame = ttk.Frame(self.container, padding=5)
            main_frame.pack(fill=BOTH, expand=True)
            
            # Header with user info and logout
            header = ttk.Frame(main_frame)
            header.pack(fill=X, pady=(0, 5))
            
            # Display user name or ID if name is not available
            user_display = f"User ID: {self.current_user.get('id', 'N/A')}"
            if 'name' in self.current_user and self.current_user['name']:
                user_display = self.current_user['name']
                
            ttk.Label(
                header,
                text=user_display,
                font=('Arial', 18, 'bold'),
                bootstyle='primary'
            ).pack(side=LEFT, fill=X, expand=True)
            
            # Logout button
            ttk.Button(
                header,
                text="🔒 Logout",
                style='danger.TButton',
                command=self.show_welcome
            ).pack(side=RIGHT, padx=5)
            
            # Title
            ttk.Label(
                main_frame,
                text="Select a Medicine",
                font=('Arial', 20, 'bold'),
                bootstyle='secondary'
            ).pack(pady=(0, 10))
            
            # Medicine grid (3x3)
            grid_frame = ttk.Frame(main_frame)
            grid_frame.pack(fill=BOTH, expand=True, pady=5)
            
            # Configure grid layout
            for i in range(3):  # 3 rows
                grid_frame.rowconfigure(i, weight=1, uniform='row')
            for i in range(3):  # 3 columns
                grid_frame.columnconfigure(i, weight=1, uniform='col')
            
            # Load and display medicines
            try:
                medicines = load_medicines()
                if not medicines:
                    ttk.Label(
                        grid_frame,
                        text="No medicines available.",
                        font=('Arial', 16),
                        bootstyle='warning'
                    ).grid(row=0, column=0, columnspan=3, pady=50)
                else:
                    # Display up to 9 medicines (3x3 grid)
                    for i, med in enumerate(medicines[:9]):  # Limit to 9 items
                        row = i // 3
                        col = i % 3
                        create_med_button(grid_frame, med, row, col)
            except Exception as e:
                print(f"Error loading medicines: {e}")
                ttk.Label(
                    grid_frame,
                    text="Error loading medicine list.",
                    font=('Arial', 16),
                    bootstyle='danger'
                ).grid(row=0, column=0, columnspan=3, pady=50)
            
            # Bottom action buttons
            action_frame = ttk.Frame(main_frame)
            action_frame.pack(fill=X, pady=(10, 0))
            
            # Action buttons with fixed size
            buttons = [
                ("❓ Help", 'info', self.show_mcq),
                ("🏠 Home", 'secondary', self.show_welcome)
            ]
            
            for i, (text, style, cmd) in enumerate(buttons):
                btn = ttk.Button(
                    action_frame,
                    text=text,
                    style=f'{style}.TButton',
                    command=cmd
                )
                btn.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
                action_frame.columnconfigure(i, weight=1)
            
            # Force UI update
            self.update_idletasks()
            
        except Exception as e:
            print(f"Error in show_catalog: {str(e)}")
            self.show_error("Failed to load catalog. Please try again.")
            self.after(1000, self.show_welcome)

    def select_medicine(self, medicine):
        """Handle medicine selection and dispense, then go to payment screen."""
        try:
            success = dispense(medicine.get("slot"))
            if success:
                # Store pending medicine for payment
                self.pending_medicine = medicine
                self.show_payment_screen(medicine)
            else:
                self.show_error("Failed to dispense medicine. Please try again.")
        except Exception as e:
            print(f"Error dispensing medicine: {e}")
            self.show_error("An error occurred while processing your request.")
            self.show_payment_screen(medicine)
        else:
            self.show_error("Out of Stock")

    def show_mcq(self):
        """Display MCQ questionnaire."""
        self.clear_screen()
        questionnaire = load_questionnaire()
        if "questions" in questionnaire and questionnaire["questions"]:
            question = questionnaire["questions"][0]
            tk.Label(self, text=question["text"], font=("Arial", 18)).pack(pady=20)
            for option in question["options"]:
                tk.Button(
                    self,
                    text=option["text"],
                    font=("Arial", 14),
                    width=20,
                    height=2,
                    command=lambda o=option: self.recommend_medicine(o["medicine"]),
                ).pack(pady=5)
        else:
            self.show_error("No questionnaire available")

    def recommend_medicine(self, med_id):
        """Show recommended medicine for confirmation."""
        self.clear_screen()
        medicines = load_medicines()
        if med_id in medicines:
            med = medicines[med_id]
            tk.Label(self, text=f"Recommended: {med['name']}", font=("Arial", 20)).pack(pady=20)
            tk.Button(self, text="Confirm", font=("Arial", 16), width=10, height=2, command=lambda: self.select_medicine(med)).pack(
                pady=10
            )
            tk.Button(
                self,
                text="Cancel",
                font=("Arial", 16),
                width=10,
                height=2,
                command=lambda: self.show_catalog(self.current_user),
            ).pack(pady=10)
        else:
            self.show_error("Medicine not found")

    def show_payment_screen(self, medicine):
        """Show payment screen with QR code and payment options."""
        price = medicine.get('price', 0)
        self.clear_screen()
        
        # Main container with padding
        container = ttk.Frame(self.container, padding=20)
        container.pack(fill=BOTH, expand=True)
        
        # Title
        ttk.Label(
            container, 
            text="Payment", 
            font=('Arial', 28, 'bold'),
            bootstyle='primary'
        ).pack(pady=(0, 20))
        
        # Amount display with larger font
        amount_frame = ttk.Frame(container)
        amount_frame.pack(pady=(0, 20))
        
        ttk.Label(
            amount_frame, 
            text="Total Amount:", 
            font=('Arial', 24)
        ).pack(side=LEFT, padx=10)
        
        ttk.Label(
            amount_frame, 
            text=f"₹{price:.2f}", 
            font=('Arial', 28, 'bold'),
            bootstyle='success'
        ).pack(side=LEFT, padx=10)
        
        # QR Code Section with larger frame
        qr_frame = ttk.LabelFrame(
            container, 
            text="Payment Options", 
            padding=30,
            bootstyle='info'
        )
        qr_frame.pack(pady=20, fill=BOTH, expand=True)
        
        # Load static QR code image if it exists, otherwise show message
        qr_path = os.path.join(os.path.dirname(__file__), "static_qr.png")
        
        if os.path.exists(qr_path):
            try:
                # Load and display the static QR code
                qr_img = Image.open(qr_path)
                qr_img = qr_img.resize((300, 300), Image.Resampling.LANCZOS)
                self._qr_photo = ImageTk.PhotoImage(qr_img)
                qr_label = ttk.Label(qr_frame, image=self._qr_photo)
                qr_label.image = self._qr_photo  # Keep reference
                qr_label.pack(pady=20)
                
                ttk.Label(
                    qr_frame, 
                    text="Scan the QR code with any UPI app",
                    font=('Arial', 16)
                ).pack(pady=(15, 5))
                
            except Exception as e:
                print(f"Error loading QR code: {str(e)}")
                ttk.Label(
                    qr_frame, 
                    text="[QR Code Loading Error]",
                    font=('Arial', 16),
                    bootstyle='danger'
                ).pack(pady=20)
        else:
            # If no static QR code found, show payment instructions
            ttk.Label(
                qr_frame, 
                text="Please make payment to the following UPI ID:",
                font=('Arial', 18, 'bold')
            ).pack(pady=(10, 5))
            
            ttk.Label(
                qr_frame, 
                text="your-upi-id@okbizaxis",
                font=('Arial', 20, 'bold'),
                bootstyle='primary'
            ).pack(pady=(0, 10))
            
            ttk.Label(
                qr_frame, 
                text=f"Amount: ₹{price:.2f}",
                font=('Arial', 18)
            ).pack(pady=(0, 10))
            
            ttk.Label(
                qr_frame, 
                text="After payment, click 'Payment Done' below",
                font=('Arial', 14, 'italic')
            ).pack(pady=(10, 0))
        
        # Action buttons - larger and more prominent
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=30)
        
        # Payment Done button
        ttk.Button(
            btn_frame,
            text="✓ Payment Done",
            style='success.Large.TButton',
            width=20,
            padding=20,
            command=lambda: self.on_paid(medicine, price),
        ).grid(row=0, column=0, padx=20, pady=10, ipadx=20, ipady=10)
        
        # Back button
        ttk.Button(
            btn_frame,
            text="← Back to Home",
            style='secondary.Large.TButton',
            width=20,
            padding=20,
            command=self.show_welcome,
        ).grid(row=0, column=1, padx=20, pady=10, ipadx=20, ipady=10)

    def on_paid(self, medicine: dict, price: float):
        """Handle payment confirmation: log CSV, print receipt, log transaction, thank you."""
        # Log CSV
        self.log_payment_csv(
            user_id=str(self.current_user["id"]),
            medicine_name=str(medicine.get("name", "")),
            amount=price,
            dt=datetime.now(),
        )
        # Print receipt with amount
        print_order_receipt(
            user_id=str(self.current_user["id"]),
            user_name=str(self.current_user.get("name", "")),
            medicine_name=str(medicine.get("name", "")),
            slot_id=int(medicine.get("slot", 0)),
            amount=price,
        )
        # Log standard transaction as well
        log_transaction(self.current_user["id"], medicine.get("name", ""), medicine.get("slot", 0))
        self.show_thank_you()

    def log_payment_csv(self, user_id: str, medicine_name: str, amount: float, dt: datetime) -> None:
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        ensure_dir(data_dir)
        csv_path = os.path.join(data_dir, "payments.csv")
        file_exists = os.path.exists(csv_path)
        with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["id", "medicine", "amount", "date", "time"])  # header
            writer.writerow([user_id, medicine_name, f"{amount:.2f}", dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")])
        print(f"Payment logged to {csv_path}")

    def show_thank_you(self):
        """Display thank you screen."""
        self.clear_screen()
        
        # Create frame in container
        frame = ttk.Frame(self.container)
        frame.pack(expand=True)
        
        ttk.Label(
            frame,
            text="Thank you! Please take your medicine.",
            font=("Arial", 24),
            bootstyle="success"
        ).pack(pady=20)
        
        ttk.Button(
            frame,
            text="Done",
            style="primary.TButton",
            command=self.show_welcome
        ).pack(pady=20)

    def show_error(self, message):
        """Display error message."""
        self.clear_screen()
        
        # Create frame in container
        frame = ttk.Frame(self.container)
        frame.pack(expand=True)
        
        ttk.Label(
            frame,
            text=message,
            font=("Arial", 20),
            bootstyle="danger"
        ).pack(pady=20)
        
        ttk.Button(
            frame,
            text="Back",
            style="secondary.TButton",
            command=self.show_welcome
        ).pack(pady=20)

    def _toggle_fullscreen_event(self, event=None):
        """Toggle fullscreen mode via F11 for testing without rebooting the Pi."""
        self._is_fullscreen = not self._is_fullscreen
        try:
            self.attributes("-fullscreen", self._is_fullscreen)
        except Exception:
            pass
        return "break"

    def clear_screen(self):
        """Clear all widgets from the screen."""
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = VendingGUI()
    app.mainloop()
