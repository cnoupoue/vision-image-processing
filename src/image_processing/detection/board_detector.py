import cv2
import numpy as np


class BoardDetector:
    def detect_board_and_cells(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        # Contour externe du plateau
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, []

        board_contour = max(contours, key=cv2.contourArea)
        epsilon = 0.02 * cv2.arcLength(board_contour, True)
        approx_board = cv2.approxPolyDP(board_contour, epsilon, True)
        if len(approx_board) != 4:
            return None, []

        pts = self.order_points(approx_board.reshape(4, 2))
        width = int(max(np.linalg.norm(pts[0] - pts[1]), np.linalg.norm(pts[2] - pts[3])))
        height = int(max(np.linalg.norm(pts[1] - pts[2]), np.linalg.norm(pts[3] - pts[0])))
        dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(pts, dst)
        warped = cv2.warpPerspective(frame, M, (width, height))

        # Seuil adaptatif pour mieux détecter les cases
        gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray_warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 15, 4)

        # Contours internes (cases)
        contours_cells, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cells = []
        for c in contours_cells:
            epsilon = 0.02 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, epsilon, True)
            if len(approx) == 4 and cv2.contourArea(approx) > 500:  # filtre bruit
                x, y, w, h = cv2.boundingRect(approx)
                # garder uniquement les cases proches du bord
                margin = 0.05
                if x < width * margin or x + w > width * (1 - margin) or y < height * margin or y + h > height * (
                        1 - margin):
                    cells.append(approx.reshape(4, 2))

        # Tri des cases pour l'ordre Monopoly
        cells = self.sort_cells(cells, width, height)
        return pts, cells

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # top-left
        rect[2] = pts[np.argmax(s)]  # bottom-right
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # top-right
        rect[3] = pts[np.argmax(diff)]  # bottom-left
        return rect

    def sort_cells(self, cells, w, h):
        """
        Trie les cases selon le contour du plateau: top->right->bottom->left
        """
        top = []
        right = []
        bottom = []
        left = []

        for c in cells:
            x, y, cw, ch = cv2.boundingRect(c)
            if y < h * 0.1:
                top.append(c)
            elif x > w * 0.9:
                right.append(c)
            elif y > h * 0.9:
                bottom.append(c)
            elif x < w * 0.1:
                left.append(c)

        top.sort(key=lambda c: c[0])
        right.sort(key=lambda c: c[1])
        bottom.sort(key=lambda c: c[0], reverse=True)
        left.sort(key=lambda c: c[1], reverse=True)

        return top + right + bottom + left
