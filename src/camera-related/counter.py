import json
import datetime  # Fixed typo from 'datatime' to 'datetime'

class DataRecord:  # Class names should follow PascalCase
    def __init__(self):
        self.enter = 0
        self.exit = 0
        self.data = []

        # Load existing data from the JSON file
        try:
            with open("data.json", "r") as file:
                self.data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error opening database file or file is empty. Starting fresh.")

    def increase_enter(self):
        self.enter += 1
        self.log_formatting(True)  # Automatically log when someone enters
        self.update_json()

    def increase_exit(self):
        self.exit += 1
        self.log_formatting(False)  # Automatically log when someone exits
        self.update_json()

    def log_formatting(self, enter_check):
        log_entry = {
            "Enter Check": enter_check,  # True for entry, False for exit
            "Time Stamp": datetime.datetime.now().isoformat()  # Proper timestamp format
        }
        
        self.data.append(log_entry)  # Append new log entry to data list

    def update_json(self):
        # Save updated data back to the file
        with open("data.json", "w") as file:
            json.dump(self.data, file, indent=4)

# Example usage
record = DataRecord()

# Simulate someone entering and exiting
record.increase_enter()  # This will automatically update the JSON file
record.increase_exit()   # This will also automatically update the JSON file
