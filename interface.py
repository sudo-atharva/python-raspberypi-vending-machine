import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os

FILE_PATH = "/home/pi/Desktop/drug_vending_machine_data.csv"

def load_data():
    try:
        df = pd.read_csv(FILE_PATH)
        return df
    except Exception as e:
        messagebox.showerror("File Error", f"Could not load CSV file: {e}")
        return None

def generate_bill_popup(medicine):
    bill_text = (
        f"🧾 Bill Generated:\n\n"
        f"Medicine: {medicine['Medicine Name']}\n"
        f"Price: ₹{medicine['Price (₹)']}\n"
        f"Dosage: {medicine['Dosage Instructions']}\n\n"
        f"✅ Thank you for your purchase!"
    )
    messagebox.showinfo("Bill", bill_text)

def select_by_medicine(df):
    win = tk.Toplevel(root)
    win.title("Select Medicine")
    win.geometry("400x400")

    tk.Label(win, text="Choose Medicine:", font=("Helvetica", 14)).pack(pady=10)

    for _, row in df.iterrows():
        btn = tk.Button(win, text=f"{row['Medicine Name']} (₹{row['Price (₹)']})", 
                        command=lambda r=row: generate_bill_popup(r), 
                        width=30, height=2, bg="#c2f0c2")
        btn.pack(pady=5)

def select_by_symptom(df):
    win = tk.Toplevel(root)
    win.title("Select Symptom")
    win.geometry("400x400")

    tk.Label(win, text="Choose Symptom:", font=("Helvetica", 14)).pack(pady=10)

    symptoms = df["Symptom"].dropna().unique()
    for symptom in symptoms:
        btn = tk.Button(win, text=symptom, command=lambda s=symptom: show_medicines_for_symptom(df, s),
                        width=30, height=2, bg="#f0e68c")
        btn.pack(pady=5)

def show_medicines_for_symptom(df, symptom):
    win = tk.Toplevel(root)
    win.title(f"Medicines for {symptom}")
    win.geometry("400x400")

    tk.Label(win, text=f"Medicines for {symptom}:", font=("Helvetica", 14)).pack(pady=10)

    matching = df[df["Symptom"] == symptom]
    for _, row in matching.iterrows():
        btn = tk.Button(win, text=f"{row['Medicine Name']} (₹{row['Price (₹)']})", 
                        command=lambda r=row: generate_bill_popup(r), 
                        width=30, height=2, bg="#d0e0f0")
        btn.pack(pady=5)

# ----- Main UI -----
root = tk.Tk()
root.title("Smart Drug Vending Machine")
root.geometry("480x320")
root.configure(bg="#f5f5f5")

df = load_data()
if df is None:
    root.destroy()

tk.Label(root, text="Welcome to the Vending Machine", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=20)

btn1 = tk.Button(root, text="🔍 Select by Medicine", font=("Helvetica", 14), width=25, height=2,
                 command=lambda: select_by_medicine(df), bg="#b3d9ff")
btn1.pack(pady=10)

btn2 = tk.Button(root, text="😷 Select by Symptom", font=("Helvetica", 14), width=25, height=2,
                 command=lambda: select_by_symptom(df), bg="#ffcccb")
btn2.pack(pady=10)

btn3 = tk.Button(root, text="🚪 Exit", font=("Helvetica", 12), width=15, height=1,
                 command=root.quit, bg="#ddd")
btn3.pack(pady=20)

root.mainloop()
