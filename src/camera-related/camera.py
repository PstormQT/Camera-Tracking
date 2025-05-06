import cv2
import numpy as np
import counter 

class PeopleCounter:
    def __init__(self, line_position=None):
        self.enter_count = 0
        self.exit_count = 0
        self.tracker = cv2.createBackgroundSubtractorMOG2()
        self.line_position = line_position if line_position is not None else 0.5  # Default at 50% of frame width
        self.tracked_objects = {}
        self.next_id = 0
        self.dataRecord = counter.DataRecord()
        self.crossed_ids = set()  # Track IDs of objects that have already crossed
        self.cooldown_tracker = {}  # Track cooldown for each object ID
    
    def process_frame(self, frame):
        fg_mask = self.tracker.apply(frame)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        line_x = int(frame.shape[1] * self.line_position)  # Calculate vertical line position
        new_tracked_objects = {}
        
        for contour in contours:
            if cv2.contourArea(contour) > 1000:  # Adjust size threshold to avoid noise
                x, y, w, h = cv2.boundingRect(contour)
                obj_center_x = x + w // 2
                obj_center_y = y + h // 2
                
                # Draw a bounding box around detected objects
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Assign an ID to new objects
                matched_id = None
                for obj_id, (prev_x, prev_y) in self.tracked_objects.items():
                    if abs(prev_x - obj_center_x) < 50 and abs(prev_y - obj_center_y) < 50:
                        matched_id = obj_id
                        break
                
                if matched_id is None:
                    matched_id = self.next_id
                    self.next_id += 1
                
                new_tracked_objects[matched_id] = (obj_center_x, obj_center_y)
                
                # Check if the object crossed the line
                if matched_id in self.tracked_objects and matched_id not in self.crossed_ids:
                    prev_x, _ = self.tracked_objects[matched_id]
                    if matched_id not in self.cooldown_tracker or self.cooldown_tracker[matched_id] <= 0:
                        # Ensure the object fully crosses the line in the correct direction
                        if prev_x > line_x and obj_center_x < line_x:
                            self.enter_count += 1
                            self.dataRecord.increase_enter()
                            self.crossed_ids.add(matched_id)  # Mark as crossed
                            self.cooldown_tracker[matched_id] = 10  # Set cooldown
                        elif prev_x < line_x and obj_center_x > line_x:
                            self.exit_count += 1
                            self.dataRecord.increase_exit()
                            self.crossed_ids.add(matched_id)  # Mark as crossed
                            self.cooldown_tracker[matched_id] = 10  # Set cooldown

        # Decrease cooldown for all tracked objects
        for obj_id in list(self.cooldown_tracker.keys()):
            self.cooldown_tracker[obj_id] -= 1
            if self.cooldown_tracker[obj_id] <= 0:
                del self.cooldown_tracker[obj_id]

        self.tracked_objects = new_tracked_objects  # Update tracked objects
        return self.enter_count, self.exit_count
    
    def get_counts(self):
        return self.enter_count, self.exit_count

# Remove the example usage block at the bottom of the file
# This block opens its own window, which conflicts with the GUI in camera_gui_test.py
# Example usage:
# counter = PeopleCounter(line_position=0.4)  # Set the line at 40% of frame width
# camera = cv2.VideoCapture(0)
# try:
#     while True:
#         ret, frame = camera.read()
#         if not ret:
#             break
#         
#         enter_count, exit_count = counter.process_frame(frame)
#         line_x = int(frame.shape[1] * counter.line_position)
#         cv2.line(frame, (line_x, 0), (line_x, frame.shape[0]), (0, 0, 255), 2)  # Draw vertical line on frame
#         cv2.putText(frame, f"Entered: {enter_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#         cv2.putText(frame, f"Exited: {exit_count}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
#         cv2.imshow("People Counter", frame)
#         
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
# except KeyboardInterrupt:
#     print("KeyboardInterrupt detected. Exiting gracefully.")
# finally:
#     # Release resources
#     camera.release()
#     cv2.destroyAllWindows()