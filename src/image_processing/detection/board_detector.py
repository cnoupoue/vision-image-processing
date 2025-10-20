import cv2
import numpy as np


class BoardDetector:
    def detect_board(self, frame):
        """
        Détecte le plateau de Monopoly dans la frame.
        Retourne le plateau recadré et la bounding box réelle.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, None

        board_contour = max(contours, key=cv2.contourArea)
        epsilon = 0.02 * cv2.arcLength(board_contour, True)
        approx = cv2.approxPolyDP(board_contour, epsilon, True)
        if len(approx) != 4:
            return None, None

        x, y, w, h = cv2.boundingRect(approx)
        board = frame[y:y + h, x:x + w]
        self.board_bbox = (x, y, w, h)
        return board, self.board_bbox

    def extract_cells(self, board_bbox):
        """
        Retourne les cases réelles à partir du rectangle du plateau.
        board_bbox = (x, y, w, h)
        """
        if board_bbox is None:
            return []

        x, y, w, h = board_bbox
        cells = []

        n_horizontal = 10
        n_vertical = 8

        # Top & bottom
        cell_w = w // n_horizontal
        for i in range(n_horizontal):
            cells.append({'bbox': (x + i * cell_w, y, cell_w, cell_w)})  # top
            cells.append({'bbox': (x + i * cell_w, y + h - cell_w, cell_w, cell_w)})  # bottom

        # Left & right
        cell_h = h // n_vertical
        for i in range(n_vertical):
            cells.append({'bbox': (x, y + i * cell_h, cell_h, cell_h)})  # left
            cells.append({'bbox': (x + w - cell_h, y + i * cell_h, cell_h, cell_h)})  # right

        return cells
