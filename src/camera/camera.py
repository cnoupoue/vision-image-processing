import cv2
import numpy as np
from image_processing.detection.board_detector import BoardDetector


class Camera:
    def __init__(self):
        self.source = self.detect_camera_index()
        self.cap = None
        self.open_camera()
        self.board_detector = BoardDetector()

    def detect_camera_index(self, max_index=5):
        print("Scanning for available cameras...")
        for i in range(max_index):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"Camera detected at index {i}")
                cap.release()
                return i
            cap.release()
        print("No camera detected, fallback to index 0")
        return 0

    def open_camera(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            print(f"Unable to open camera at index {self.source}")
            self.cap = None

    def generate_frames(self):
        while True:
            if self.cap is None or not self.cap.isOpened():
                blank_frame = self.create_blank_frame("Camera disconnected")
                ret, buffer = cv2.imencode('.jpg', blank_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                continue

            success, frame = self.cap.read()
            if not success:
                print("Camera stream lost")
                self.cap.release()
                self.cap = None
                continue

            frame = cv2.resize(frame, (640, 480))

            try:
                board, board_bbox = self.board_detector.detect_board(frame)
                cells = self.board_detector.extract_cells(board_bbox)

                # Dessiner le contour du plateau
                if board_bbox is not None:
                    x, y, w, h = board_bbox
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Dessiner les cases détectées
                for i, cell in enumerate(cells):
                    x, y, w, h = cell['bbox']
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"{i}", (x + 5, y + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

            except Exception as e:
                print("Board detection failed:", e)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def create_blank_frame(self, text=""):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        if text:
            cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2, cv2.LINE_AA)
        return frame
