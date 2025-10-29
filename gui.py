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
        self.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}+0+0")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 14))
        self.style.configure('Title.TLabel', font=('Helvetica', 28, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Helvetica', 16))
        self.style.configure('Price.TLabel', font=('Helvetica', 20, 'bold'), foreground=PRIMARY)
        
        # Kiosk mode: fullscreen and prevent closing
        try:
            self.attributes("-fullscreen", True)
        except Exception:
            pass
            
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.bind("<Alt-F4>", lambda e: "break")
        self.bind("<Escape>", lambda e: "break")
        self.bind("<Control-q>", lambda e: "break")
        
        # Toggleable fullscreen for testing
        self._is_fullscreen = True
        self.bind("<F11>", self._toggle_fullscreen_event)
        
        self.current_user: Optional[dict] = None
        self.manual_id_var = tk.StringVar()
        self._qr_photo = None
        self.pending_medicine: Optional[dict] = None
        
        # Create a container frame for all screens
        self.container = ttk.Frame(self)
        self.container.pack(fill=BOTH, expand=True)
        
        self.show_welcome()

    def show_welcome(self):
        """Display welcome screen with options to scan or enter ID manually."""
        self.clear_screen()
        
        # Header
        header = ttk.Frame(self.container, padding=20)
        header.pack(fill=X, pady=(40, 20))
        ttk.Label(header, text="Welcome to", font=('Helvetica', 24), bootstyle=SECONDARY).pack()
        ttk.Label(header, text="Medicine Vending Machine", style='Title.TLabel', bootstyle=PRIMARY).pack()
        
        # Main content
        content = ttk.Frame(self.container, padding=20)
        content.pack(expand=YES, fill=BOTH)
        
        ttk.Label(content, 
                 text="Please scan your barcode or enter your ID", 
                 style='Subtitle.TLabel').pack(pady=(0, 30))
        
        # Action buttons
        btn_frame = ttk.Frame(content)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="Scan Barcode",
            style='primary.TButton',
            width=20,
            command=self.show_scan_instructions,
        ).grid(row=0, column=0, padx=10, pady=10, ipady=10)
        
        ttk.Button(
            btn_frame,
            text="Enter ID Manually",
            style='secondary.TButton',
            width=20,
            command=self.show_manual_id_entry,
        ).grid(row=0, column=1, padx=10, pady=10, ipady=10)

    def show_scan_instructions(self):
        """Show simple scan instructions screen (placeholder for future auto-scan)."""
        self.clear_screen()
        tk.Label(self, text="Scan your barcode now", font=("Arial", 22)).pack(pady=20)
        tk.Label(self, text="After scanning, the system will process your ID.", font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Back", font=("Arial", 16), width=10, height=2, command=self.show_welcome).pack(pady=20)

    def show_manual_id_entry(self):
        """Display on-screen keypad for manual ID entry."""
        self.clear_screen()
        self.manual_id_var.set("")

        tk.Label(self, text="Enter Your ID", font=("Arial", 22)).pack(pady=10)

        entry = tk.Entry(self, textvariable=self.manual_id_var, font=("Arial", 20), justify="center")
        entry.pack(pady=10)
        entry.focus_set()

        keypad = tk.Frame(self)
        keypad.pack(pady=10)

        buttons = [
            ("1", 0, 0),
            ("2", 0, 1),
            ("3", 0, 2),
            ("4", 1, 0),
            ("5", 1, 1),
            ("6", 1, 2),
            ("7", 2, 0),
            ("8", 2, 1),
            ("9", 2, 2),
            ("Clear", 3, 0),
            ("0", 3, 1),
            ("<-", 3, 2),
        ]
        for (text, r, c) in buttons:
            if text.isdigit():
                cmd = lambda t=text: self.append_digit(t)
            elif text == "Clear":
                cmd = self.clear_id
            else:  # backspace
                cmd = self.backspace_id
            tk.Button(keypad, text=text, font=("Arial", 18), width=6, height=2, command=cmd).grid(
                row=r, column=c, padx=5, pady=5
            )

        action_frame = tk.Frame(self)
        action_frame.pack(pady=15)

        tk.Button(action_frame, text="Submit", font=("Arial", 16), width=12, height=2, command=self.submit_manual_id).grid(
            row=0, column=0, padx=10
        )
        tk.Button(action_frame, text="Back", font=("Arial", 16), width=12, height=2, command=self.show_welcome).grid(
            row=0, column=1, padx=10
        )

    def append_digit(self, d):
        self.manual_id_var.set(self.manual_id_var.get() + d)

    def backspace_id(self):
        self.manual_id_var.set(self.manual_id_var.get()[:-1])

    def clear_id(self):
        self.manual_id_var.set("")

    def submit_manual_id(self):
        user_id = self.manual_id_var.get().strip()
        if not user_id:
            self.show_error("Please enter a valid ID")
            return
        user = get_user_by_id(user_id)
        if user:
            self.show_catalog(user)
        else:
            self.show_error("Invalid ID")

    def show_catalog(self, user):
        """Display medicine catalog."""
        self.current_user = user
        self.clear_screen()
        tk.Label(self, text=f"Welcome, {user['name']}!", font=("Arial", 20)).pack(pady=10)

        frame = tk.Frame(self)
        frame.pack()

        medicines = load_medicines()
        row = 0
        col = 0
        for med_id, med in medicines.items():
            btn = tk.Button(
                frame,
                text=med.get("name", str(med_id)),
                font=("Arial", 16),
                width=15,
                height=3,
                command=lambda m=med: self.select_medicine(m),
            )
            btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col == 3:
                col = 0
                row += 1

        tk.Button(
            self,
            text="I don't know what I need",
            font=("Arial", 16),
            width=20,
            height=2,
            command=self.show_mcq,
        ).pack(pady=20)

    def select_medicine(self, medicine):
        """Handle medicine selection and dispense, then go to payment screen."""
        success = dispense(medicine["slot"])
        if success:
            # Store pending medicine for payment
            self.pending_medicine = medicine
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

    def show_payment_screen(self, medicine: dict):
        """Display amount due and QR image; on Paid, log CSV + print receipt."""
        self.clear_screen()
        price = float(medicine.get("price", 0.0))
        
        # Create main container with padding
        container = ttk.Frame(self.container, padding=30)
        container.pack(expand=YES, fill=BOTH)
        
        # Header
        ttk.Label(container, text="Payment", style='Title.TLabel').pack(pady=(0, 20))
        
        # Amount display
        amount_frame = ttk.Frame(container)
        amount_frame.pack(pady=(0, 20))
        
        ttk.Label(amount_frame, text="Total Amount:", font=('Helvetica', 18)).pack(side=LEFT, padx=5)
        ttk.Label(amount_frame, text=f"₹{price:.2f}", style='Price.TLabel').pack(side=LEFT, padx=5)
        
        # QR Code Section
        qr_frame = ttk.LabelFrame(container, text="Payment Options", padding=20)
        qr_frame.pack(pady=20)
        
        # Load static QR code image if it exists, otherwise show message
        qr_path = os.path.join(os.path.dirname(__file__), "static_qr.png")
        
        if os.path.exists(qr_path):
            try:
                # Load and display the static QR code
                qr_img = Image.open(qr_path)
                qr_img = qr_img.resize((250, 250), Image.Resampling.LANCZOS)
                self._qr_photo = ImageTk.PhotoImage(qr_img)
                qr_label = ttk.Label(qr_frame, image=self._qr_photo)
                qr_label.image = self._qr_photo  # Keep reference
                qr_label.pack()
                
                ttk.Label(qr_frame, 
                         text="Scan the QR code with any UPI app",
                         font=('Helvetica', 12)).pack(pady=(15, 5))
                
            except Exception as e:
                print(f"Error loading QR code: {str(e)}")
                ttk.Label(qr_frame, 
                         text="[QR Code Loading Error]",
                         font=('Helvetica', 12),
                         foreground='red').pack()
        else:
            # If no static QR code found, show payment instructions
            ttk.Label(qr_frame, 
                     text="Please make payment to the following UPI ID:",
                     font=('Helvetica', 14, 'bold')).pack(pady=(10, 5))
            ttk.Label(qr_frame, 
                     text="your-upi-id@okbizaxis",
                     font=('Helvetica', 16, 'bold'),
                     foreground=PRIMARY).pack(pady=(0, 10))
            ttk.Label(qr_frame, 
                     text=f"Amount: ₹{price:.2f}",
                     font=('Helvetica', 14)).pack(pady=(0, 10))
            ttk.Label(qr_frame, 
                     text="After payment, click 'Payment Done' below",
                     font=('Helvetica', 12, 'italic')).pack(pady=(10, 0))
        
        # Action buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="✓ Payment Done",
            style='success.TButton',
            width=15,
            command=lambda: self.on_paid(medicine, price),
        ).grid(row=0, column=0, padx=10, ipady=10)
        
        ttk.Button(
            btn_frame,
            text="← Back to Home",
            style='outline.TButton',
            width=15,
            command=self.show_welcome,
        ).grid(row=0, column=1, padx=10, ipady=10)

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
        tk.Label(self, text="Thank you! Please take your medicine.", font=("Arial", 24)).pack(pady=20)
        tk.Button(self, text="Done", font=("Arial", 16), width=10, height=2, command=self.show_welcome).pack(pady=20)

    def show_error(self, message):
        """Display error message."""
        self.clear_screen()
        tk.Label(self, text=message, font=("Arial", 20), fg="red").pack(pady=20)
        tk.Button(self, text="Back", font=("Arial", 16), width=10, height=2, command=self.show_welcome).pack(pady=20)

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
