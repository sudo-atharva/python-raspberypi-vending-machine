import tkinter as tk
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from database import load_medicines, load_questionnaire, log_transaction
from motor_control import dispense
from printer import print_receipt

class VendingGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Medicine Vending Machine")
        self.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.current_user = None
        self.show_welcome()

    def show_welcome(self):
        """Display welcome screen."""
        self.clear_screen()
        tk.Label(self, text="Welcome to Medicine Vending Machine", font=("Arial", 24)).pack(pady=20)
        tk.Label(self, text="Please scan your barcode to continue", font=("Arial", 18)).pack(pady=20)

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
            btn = tk.Button(frame, text=med['name'], font=("Arial", 16), width=15, height=3,
                            command=lambda m=med: self.select_medicine(m))
            btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col == 3:
                col = 0
                row += 1

        tk.Button(self, text="I don't know what I need", font=("Arial", 16), width=20, height=2,
                  command=self.show_mcq).pack(pady=20)

    def select_medicine(self, medicine):
        """Handle medicine selection and dispense."""
        success = dispense(medicine['slot'])
        if success:
            print_receipt(self.current_user['id'], self.current_user['name'], medicine['name'], medicine['slot'])
            log_transaction(self.current_user['id'], medicine['name'], medicine['slot'])
            self.show_thank_you()
        else:
            self.show_error("Out of Stock")

    def show_mcq(self):
        """Display MCQ questionnaire."""
        self.clear_screen()
        questionnaire = load_questionnaire()
        if 'questions' in questionnaire and questionnaire['questions']:
            question = questionnaire['questions'][0]
            tk.Label(self, text=question['text'], font=("Arial", 18)).pack(pady=20)
            for option in question['options']:
                tk.Button(self, text=option['text'], font=("Arial", 14), width=20, height=2,
                          command=lambda o=option: self.recommend_medicine(o['medicine'])).pack(pady=5)
        else:
            self.show_error("No questionnaire available")

    def recommend_medicine(self, med_id):
        """Show recommended medicine for confirmation."""
        self.clear_screen()
        medicines = load_medicines()
        if med_id in medicines:
            med = medicines[med_id]
            tk.Label(self, text=f"Recommended: {med['name']}", font=("Arial", 20)).pack(pady=20)
            tk.Button(self, text="Confirm", font=("Arial", 16), width=10, height=2,
                      command=lambda: self.select_medicine(med)).pack(pady=10)
            tk.Button(self, text="Cancel", font=("Arial", 16), width=10, height=2,
                      command=lambda: self.show_catalog(self.current_user)).pack(pady=10)
        else:
            self.show_error("Medicine not found")

    def show_thank_you(self):
        """Display thank you screen."""
        self.clear_screen()
        tk.Label(self, text="Thank you! Please take your medicine.", font=("Arial", 24)).pack(pady=20)
        tk.Button(self, text="Done", font=("Arial", 16), width=10, height=2,
                  command=self.show_welcome).pack(pady=20)

    def show_error(self, message):
        """Display error message."""
        self.clear_screen()
        tk.Label(self, text=message, font=("Arial", 20), fg="red").pack(pady=20)
        tk.Button(self, text="Back", font=("Arial", 16), width=10, height=2,
                  command=self.show_welcome).pack(pady=20)

    def clear_screen(self):
        """Clear all widgets from the screen."""
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = VendingGUI()
    app.mainloop()