import pandas as pd
import os

def load_data():
    file_path = "/home/pi/Desktop/drug_vending_machine_data.csv"  # Adjust path as per your setup
    if not os.path.exists(file_path):
        print("Error: Data file not found! Make sure the Excel file is in the correct location.")
        return None
    return pd.read_excel(file_path)

def display_medicines(df):
    print("\nAvailable Medicines:")
    for i, medicine in enumerate(df["Medicine Name"], start=1):
        print(f"{i}. {medicine}")

    try:
        choice = int(input("\nSelect a medicine by entering the corresponding number: "))
        if 1 <= choice <= len(df):
            selected_medicine = df.iloc[choice - 1]
            print("\nYou have selected:")
            print(selected_medicine.to_string())
            generate_bill(selected_medicine)
        else:
            print("Invalid selection! Please try again.")
    except ValueError:
        print("Invalid input! Please enter a valid number.")

def display_symptoms(df):
    symptoms = df["Symptom"].dropna().unique()
    print("\nAvailable Symptoms:")
    for i, symptom in enumerate(symptoms, start=1):
        print(f"{i}. {symptom}")

    try:
        choice = int(input("\nSelect a symptom by entering the corresponding number: "))
        if 1 <= choice <= len(symptoms):
            selected_symptom = symptoms[choice - 1]
            matching_medicines = df[df["Symptom"] == selected_symptom]

            if not matching_medicines.empty:
                print("\nMatching Medicines:")
                for i, (index, row) in enumerate(matching_medicines.iterrows(), start=1):
                    print(f"{i}. {row['Medicine Name']}")

                choice = int(input("\nSelect a medicine from the above list: "))
                if 1 <= choice <= len(matching_medicines):
                    selected_medicine = matching_medicines.iloc[choice - 1]
                    print("\nYou have selected:")
                    print(selected_medicine.to_string())
                    generate_bill(selected_medicine)
                else:
                    print("Invalid selection! Please try again.")
            else:
                print("No matching medicines found!")
        else:
            print("Invalid selection! Please try again.")
    except ValueError:
        print("Invalid input! Please enter a valid number.")

def generate_bill(medicine):
    print("\nGenerating Bill...")
    print("-----------------------------")
    print(f"Medicine: {medicine['Medicine Name']}")
    print(f"Price: ₹{medicine['Price (₹)']}")
    print(f"Dosage Instructions: {medicine['Dosage Instructions']}")
    print("-----------------------------")
    print("Thank you for your purchase!")

def main():
    df = load_data()
    if df is None:
        return
    while True:
        print("\nDrug Vending Machine")
        print("1. Select by Medicine Name")
        print("2. Select by Symptom")
        print("3. Exit")

        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                display_medicines(df)
            elif choice == 2:
                display_symptoms(df)
            elif choice == 3:
                print("Exiting... Thank you!")
                break
            else:
                print("Invalid choice! Please enter a valid option.")
        except ValueError:
            print("Invalid input! Please enter a valid number.")

if __name__ == "__main__":
    main()
