import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from camera import PeopleCounter  # Import the working PeopleCounter class from camera.py

class PeopleCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("People Counter")
        self.root.attributes('-fullscreen', False)  # Fullscreen mode

        # Initialize the PeopleCounter instance
        self.people_counter = PeopleCounter(line_position=0.5)

        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("Error: Could not access the camera.")
            tk.messagebox.showerror("Camera Error", "Could not access the camera. Please check your device.")
            self.root.destroy()  # Close the Tkinter window
            return  # Exit if camera is unavailable

        self.enter_count = tk.StringVar(value="Entered: 0")
        self.exit_count = tk.StringVar(value="Exited: 0")
        self.is_running = True  # Control the update loop
        self.frame = None  # Store the latest frame
        self.frame_resolution = (1600, 900)  # Set resolution to 1600x900

        self.create_widgets()

        # Start a separate thread for capturing frames
        self.thread = threading.Thread(target=self.capture_frames, daemon=True)
        self.thread.start()

        # Schedule UI updates
        self.update_ui()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("Exit.TButton", font=("Arial", 14), padding=(10, 10))

        # Camera Display
        self.camera_label = ttk.Label(self.root)
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Count Labels
        count_frame = ttk.Frame(self.root)
        count_frame.pack(side=tk.TOP, pady=(10, 0))

        enter_label = ttk.Label(count_frame, textvariable=self.enter_count, font=("Arial", 16))
        enter_label.pack(side=tk.LEFT, padx=20)

        exit_label = ttk.Label(count_frame, textvariable=self.exit_count, font=("Arial", 16))
        exit_label.pack(side=tk.LEFT, padx=20)

        # Exit Button
        exit_button = ttk.Button(self.root, text="Exit", command=self.close_app, style="Exit.TButton")
        exit_button.pack(side=tk.BOTTOM, pady=(0, 10))

    def capture_frames(self):
        """Runs in a separate thread to capture frames without freezing the UI."""
        while self.is_running and self.camera.isOpened():
            ret, frame = self.camera.read()
            if not ret:
                print("Error: Failed to capture frame.")
                continue  # Skip this iteration if the frame is invalid

            try:
                # Process the frame using the PeopleCounter instance
                enter, exit = self.people_counter.process_frame(frame)

                # Update the latest frame
                self.frame = frame

                # Update UI numbers dynamically
                self.root.after(0, self.update_counts, enter, exit)
            except Exception as e:
                print(f"Error processing frame: {e}")

    def update_ui(self):
        """Updates the UI smoothly without flickering."""
        if self.frame is not None:
            frame = self.frame.copy()

            # Group close detections to avoid duplicate recognition
            grouped_objects = {}
            distance_threshold = 50  # Threshold to merge close detections

            for obj_id, (x, y) in self.people_counter.tracked_objects.items():
                merged = False
                for group_id, (gx, gy) in grouped_objects.items():
                    if abs(x - gx) < distance_threshold and abs(y - gy) < distance_threshold:
                        grouped_objects[group_id] = ((gx + x) // 2, (gy + y) // 2)  # Merge positions
                        merged = True
                        break
                if not merged:
                    grouped_objects[obj_id] = (x, y)

            # Draw detection bounding boxes with increased sensitivity
            for obj_id, (x, y) in grouped_objects.items():
                cv2.rectangle(frame, (x-35, y-35), (x+35, y+35), (0, 255, 0), 2)  # Larger bounding box for sensitivity
                cv2.putText(frame, f"ID: {obj_id}", (x-40, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Collect data about detected entities
                # print(f"Entity ID: {obj_id}, Position: ({x}, {y})")  # Log entity data for analysis

            # Draw the counting line
            line_x = int(frame.shape[1] * self.people_counter.line_position)
            cv2.line(frame, (line_x, 0), (line_x, frame.shape[0]), (0, 0, 255), 2)

            # Increase resolution for better display
            frame = cv2.resize(frame, self.frame_resolution)  # Set resolution to 1600x900

            # Convert frame for Tkinter display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)

            self.camera_label.img_tk = img_tk
            self.camera_label.config(image=img_tk)

        self.root.after(30, self.update_ui)  # Keep updating every 30ms

    def update_counts(self, enter, exit):
        """Updates the enter and exit count in the UI dynamically."""
        self.enter_count.set(f"Entered: {enter}")
        self.exit_count.set(f"Exited: {exit}")

    def close_app(self):
        self.is_running = False  # Stop the update loop
        if self.camera.isOpened():
            self.camera.release()  # Release the camera
        self.root.quit()  # Close the Tkinter window

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PeopleCounterApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
