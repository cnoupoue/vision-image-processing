import cv2
import numpy as np

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.show_virtual = False
        self.board_pts = None  # coins du plateau
        self.cells = []        # quadrilatères des 40 cases

    def generate_frames(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame = cv2.resize(frame, (640, 480))

            try:
                self.update_board_and_cells(frame)

                if self.show_virtual:
                    frame = self.create_virtual_board()
                else:
                    self.draw_board_and_cells(frame)

            except Exception as e:
                print("Frame error:", e)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def update_board_and_cells(self, frame):
        # Détecte uniquement le contour externe
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blur, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return

        board_contour = max(contours, key=cv2.contourArea)
        epsilon = 0.02 * cv2.arcLength(board_contour, True)
        approx = cv2.approxPolyDP(board_contour, epsilon, True)
        if len(approx) != 4:
            return

        self.board_pts = self.order_points(approx.reshape(4,2))
        self.cells = self.compute_monopoly_cells(self.board_pts)

    def order_points(self, pts):
        rect = np.zeros((4,2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]   # top-left
        rect[2] = pts[np.argmax(s)]   # bottom-right
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)] # top-right
        rect[3] = pts[np.argmax(diff)] # bottom-left
        return rect

    def compute_monopoly_cells(self, pts):
        # 40 cases : 4 coins + 9 par côté
        tl, tr, br, bl = pts
        cells = []

        def interpolate(p1, p2, n):
            return [p1 + (p2 - p1) * i / n for i in range(n+1)]

        # Coins
        cells.append(np.array([tl, tl, tl, tl]))  # top-left corner
        cells.append(np.array([tr, tr, tr, tr]))  # top-right
        cells.append(np.array([br, br, br, br]))  # bottom-right
        cells.append(np.array([bl, bl, bl, bl]))  # bottom-left

        # Top edge
        top_pts = interpolate(tl, tr, 10)
        for i in range(1,10):
            cell = np.array([top_pts[i-1], top_pts[i], top_pts[i], top_pts[i-1]])
            cells.append(cell)

        # Right edge
        right_pts = interpolate(tr, br, 10)
        for i in range(1,10):
            cell = np.array([right_pts[i-1], right_pts[i], right_pts[i], right_pts[i-1]])
            cells.append(cell)

        # Bottom edge
        bottom_pts = interpolate(br, bl, 10)
        for i in range(1,10):
            cell = np.array([bottom_pts[i-1], bottom_pts[i], bottom_pts[i], bottom_pts[i-1]])
            cells.append(cell)

        # Left edge
        left_pts = interpolate(bl, tl, 10)
        for i in range(1,10):
            cell = np.array([left_pts[i-1], left_pts[i], left_pts[i], left_pts[i-1]])
            cells.append(cell)

        return cells

    def draw_board_and_cells(self, frame):
        if self.board_pts is not None:
            cv2.polylines(frame, [self.board_pts.astype(int)], True, (255,0,0), 3)
        for idx, cell in enumerate(self.cells):
            cv2.polylines(frame, [cell.astype(int)], True, (0,255,0), 2)
            x, y, w, h = cv2.boundingRect(cell)
            cv2.putText(frame, str(idx+1), (x+5, y+15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,200,200), 1)

    def create_virtual_board(self):
        board = np.zeros((480, 480, 3), dtype=np.uint8)
        board[:] = (30,30,60)
        if self.board_pts is not None:
            cv2.polylines(board, [self.board_pts.astype(int)], True, (255,0,0), 3)
        for idx, cell in enumerate(self.cells):
            cv2.polylines(board, [cell.astype(int)], True, (0,255,0), 2)
            x, y, w, h = cv2.boundingRect(cell)
            cv2.putText(board, str(idx+1), (x+5, y+15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,200,200), 1)
        return board

    def toggle_view(self):
        self.show_virtual = not self.show_virtual
