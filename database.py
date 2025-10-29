import json
import os
from datetime import datetime
from config import MEDICINES_FILE, USERS_FILE, QUESTIONNAIRE_FILE, LOG_FILE

def load_json(file_path):
    """Load data from JSON file with error handling."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        else:
            print(f"Warning: File not found: {file_path}")
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Create an empty file
            with open(file_path, 'w') as f:
                json.dump({}, f)
            return {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {str(e)}")
        return {}
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return {}

def save_json(file_path, data):
    """Save data to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_medicines():
    """Load medicines data."""
    return load_json(MEDICINES_FILE)

def save_medicines(medicines):
    """Save medicines data."""
    save_json(MEDICINES_FILE, medicines)

def load_users():
    """Load users data."""
    return load_json(USERS_FILE)

def save_users(users):
    """Save users data."""
    save_json(USERS_FILE, users)

def load_questionnaire():
    """Load questionnaire data."""
    return load_json(QUESTIONNAIRE_FILE)

def save_questionnaire(questionnaire):
    """Save questionnaire data."""
    save_json(QUESTIONNAIRE_FILE, questionnaire)

def get_user_by_id(user_id):
    """Get user details by ID."""
    users = load_users()
    return users.get(str(user_id))

def get_medicine_by_slot(slot_id):
    """Get medicine details by slot ID."""
    medicines = load_medicines()
    for med in medicines.values():
        if med['slot'] == slot_id:
            return med
    return None

def log_transaction(user_id, medicine_name, slot_id):
    """Log a transaction."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp}: User {user_id} dispensed {medicine_name} from slot {slot_id}\n")