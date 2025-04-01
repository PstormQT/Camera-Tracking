import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
# Assuming counter.py is in the same directory, and contains the PeopleCounter class
import counter

class PeopleCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("People Counter")
        # Set the window to fullscreen
        self.root.attributes('-fullscreen', True)

        self.people_counter = counter.PeopleCounter(line_position=0.5)
        self.camera = cv2.VideoCapture(0)  # Use 0 for the default camera

        self.enter_count = tk.StringVar(value="Entered: 0")
        self.exit_count = tk.StringVar(value="Exited: 0")
        self.is_running = True # Add a flag to control the update loop

        self.create_widgets()
        self.update_frame()

    def create_widgets(self):
        # Camera Display (占据大部分窗口)
        self.camera_label = ttk.Label(self.root)
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Count Labels (放在窗口顶部中央)
        count_frame = ttk.Frame(self.root)
        count_frame.pack(side=tk.TOP, pady=(10,0))  # 上方留白

        enter_label = ttk.Label(count_frame, textvariable=self.enter_count, font=("Arial", 16))
        enter_label.pack(side=tk.LEFT, padx=20)

        exit_label = ttk.Label(count_frame, textvariable=self.exit_count, font=("Arial", 16))
        exit_label.pack(side=tk.LEFT, padx=20)

        # Exit Button (放在窗口底部中央)
        exit_button = ttk.Button(self.root, text="Exit", command=self.close_app, font=("Arial", 14), padding=(10, 10))
        exit_button.pack(side=tk.BOTTOM, pady=(0, 10))  # 下方留白

    def update_frame(self):
        if not self.is_running: # Stop updating if the app is closed.
            return
        ret, frame = self.camera.read()
        if ret:
            try:
                enter, exit = self.people_counter.process_frame(frame)
                self.enter_count.set(f"Entered: {enter}")
                self.exit_count.set(f"Exited: {exit}")

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
                print(f"Error processing frame: {e}") # Log errors.  Don't crash on frame processing.

        self.root.after(30, self.update_frame)  # Continue updating

    def close_app(self):
        self.is_running = False # Stop the update_frame loop
        self.camera.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PeopleCounterApp(root)
    root.mainloop()
