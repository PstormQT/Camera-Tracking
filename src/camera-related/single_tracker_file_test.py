import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
import json
import datetime
import counter  # Assuming this is in the same directory

# DataRecord Class to handle JSON logging
class DataRecord:
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


# PeopleCounterApp to manage the GUI and people counting
class PeopleCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("People Counter")
        self.root.attributes('-fullscreen', True)  # Set the window to fullscreen

        self.people_counter = counter.PeopleCounter(line_position=0.5)
        self.camera = cv2.VideoCapture(0)  # Use 0 for the default camera

        self.enter_count = tk.StringVar(value="Entered: 0")
        self.exit_count = tk.StringVar(value="Exited: 0")
        self.is_running = True  # Add a flag to control the update loop

        # Initialize the DataRecord instance to log data
        self.data_record = DataRecord()

        self.create_widgets()
        self.update_frame()

    def create_widgets(self):
        # Camera Display
        self.camera_label = ttk.Label(self.root)
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Count Labels
        count_frame = ttk.Frame(self.root)
        count_frame.pack(side=tk.TOP, pady=(10, 0))  # Top margin

        enter_label = ttk.Label(count_frame, textvariable=self.enter_count, font=("Arial", 16))
        enter_label.pack(side=tk.LEFT, padx=20)

        exit_label = ttk.Label(count_frame, textvariable=self.exit_count, font=("Arial", 16))
        exit_label.pack(side=tk.LEFT, padx=20)

        # Exit Button
        exit_button = tk.Button(self.root, text="Exit", command=self.close_app, font=("Arial", 14), padx=10, pady=10)
        exit_button.pack(side=tk.BOTTOM, pady=(0, 10))  # Bottom margin

    def update_frame(self):
        if not self.is_running:  # Stop updating if the app is closed
            return
        ret, frame = self.camera.read()
        if ret:
            try:
                enter, exit = self.people_counter.process_frame(frame)
                self.enter_count.set(f"Entered: {enter}")
                self.exit_count.set(f"Exited: {exit}")

                # Log entries and exits in the JSON file
                if enter > self.data_record.enter:
                    self.data_record.increase_enter()
                if exit > self.data_record.exit:
                    self.data_record.increase_exit()

                # Draw the counting line and counts on the frame
                line_x = int(frame.shape[1] * self.people_counter.line_position)
                cv2.line(frame, (line_x, 0), (line_x, frame.shape[0]), (0, 0, 255), 2)
                cv2.putText(frame, f"Entered: {enter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Exited: {exit}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Convert frame to PIL Image and then to Tkinter PhotoImage
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(image=img)

                self.camera_label.img_tk = img_tk
                self.camera_label.config(image=img_tk)
            except Exception as e:
                print(f"Error processing frame: {e}")  # Log errors

        self.root.after(30, self.update_frame)  # Continue updating

    def close_app(self):
        self.is_running = False  # Stop the update_frame loop
        self.camera.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PeopleCounterApp(root)
    root.mainloop()
