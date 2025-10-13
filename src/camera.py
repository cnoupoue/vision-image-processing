import cv2
import numpy as np

class Camera:
    def __init__(self):
        self.source = self.detect_camera_index()
        self.cap = None
        self.open_camera()

    def detect_camera_index(self, max_index=5):
        """
        Automatically detect the first available camera.
        Useful for systems with multiple cameras (like Camo Studio).
        """
        print("Scanning for available cameras...")
        available_index = None
        for i in range(max_index):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"Camera index {i} OK")
                available_index = i
                cap.release()
                break
            cap.release()
        if available_index is None:
            print("No camera detected. Falling back to index 0.")
            available_index = 0
        return available_index

    def open_camera(self):
        """Open the camera and handle if it's unavailable."""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            print(f"Unable to open camera at index {self.source}")
            self.cap = None

    def generate_frames(self):
        """Yield frames for Flask or a placeholder if camera is disconnected."""
        while True:
            if self.cap is None or not self.cap.isOpened():
                # Return a blank frame with a message
                blank_frame = self.create_blank_frame("Camera disconnected")
                ret, buffer = cv2.imencode('.jpg', blank_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                success, frame = self.cap.read()
                if not success:
                    print("Camera stream lost")
                    self.cap.release()
                    self.cap = None
                    continue
                # Resize to reduce latency
                frame = cv2.resize(frame, (640, 480))
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def create_blank_frame(self, text=""):
        """Create a black image with optional text."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        if text:
            cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2, cv2.LINE_AA)
        return frame

