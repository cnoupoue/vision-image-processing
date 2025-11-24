import cv2
import numpy as np


class Camera:

    def __init__(self, width=1280, height=720):
        """
        Initialise la caméra.
        width, height : dimensions souhaitées pour la capture.
        """
        self.cap = cv2.VideoCapture(0)  # Ouvre la caméra par défaut
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)  # Définit la largeur de capture
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)  # Définit la hauteur de capture
        self.prev_rect = None  # quadrilatère du plateau précédent
        self.prev_warped = None  # image recadrée précédente

    def get_frame(self):
        """
        Capture une seule image depuis la caméra.
        Retourne l'image sous forme de tableau numpy BGR.
        """
        ret, frame = self.cap.read()
        if not ret:
            # Si la capture échoue, retourne une image noire de la taille définie
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame = np.zeros((height, width, 3), dtype=np.uint8)
        return frame

    def crop_board(self, frame, threshold=50):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        best_rect = None
        for cnt in contours:
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if len(approx) == 4:
                area = cv2.contourArea(approx)
                if area > max_area and area > 10000:
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 2:
                        max_area = area
                        best_rect = approx

        if best_rect is not None:
            if self.prev_rect is not None:
                # Calculer distance entre anciens et nouveaux points
                dist = np.linalg.norm(self.prev_rect.reshape(-1, 2) - best_rect.reshape(-1, 2))
                if dist < threshold:
                    # Pas de changement significatif → réutiliser l'image précédente
                    return self.prev_warped

            # Nouveau plateau détecté ou changement majeur
            pts = best_rect.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]

            (tl, tr, br, bl) = rect
            widthA = np.linalg.norm(br - bl)
            widthB = np.linalg.norm(tr - tl)
            maxWidth = max(int(widthA), int(widthB))

            heightA = np.linalg.norm(tr - br)
            heightB = np.linalg.norm(tl - bl)
            maxHeight = max(int(heightA), int(heightB))

            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]
            ], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(frame, M, (maxWidth, maxHeight))

            # Dessiner contour et grille
            cv2.polylines(warped, [best_rect.reshape(-1, 1, 2)], isClosed=True, color=(0, 255, 0), thickness=3)
            h, w = warped.shape[:2]
            for i in range(1, 8):
                cv2.line(warped, (i * w // 8, 0), (i * w // 8, h), (0, 255, 0), 2)
                cv2.line(warped, (0, i * h // 8), (w, i * h // 8), (0, 255, 0), 2)

            # Sauvegarder pour la prochaine frame
            self.prev_rect = best_rect
            self.prev_warped = warped
            return warped

        # Si aucun plateau détecté, retourner le précédent stable
        return self.prev_warped if self.prev_warped is not None else frame

    def highlight_grid(self, warped, rows=8, cols=8):
        h, w = warped.shape[:2]
        for i in range(1, cols):
            cv2.line(warped, (i * w // cols, 0), (i * w // cols, h), (0, 255, 0), 2)
        for i in range(1, rows):
            cv2.line(warped, (0, i * h // rows), (w, i * h // rows), (0, 255, 0), 2)
        return warped

    def to_edges(self, frame):
        """
        Transforme l'image en contours blancs sur fond noir.
        frame : image BGR
        Retourne image BGR avec contours en blanc sur fond noir.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convertit en gris
        edges = cv2.Canny(gray, 100, 200)  # Détecte les contours
        # Pour garder 3 canaux (BGR) pour le streaming
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return edges_bgr

    def detect_cells(self, edges_warped, min_area=500):
        """
        Détecte les contours des cases dans l'image en noir et blanc (edges).
        Retourne une liste de rectangles [(x, y, w, h), ...].
        """
        contours, _ = cv2.findContours(edges_warped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cells = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                cells.append((x, y, w, h))
        return cells

    def draw_cells(self, warped, cells):
        """
        Dessine les contours des cases détectées sur l'image couleur.
        """
        for (x, y, w, h) in cells:
            cv2.rectangle(warped, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return warped

    def generate_jpeg_frames(self):
        while True:
            frame = self.get_frame()
            warped = self.crop_board(frame)  # Recadre et stabilise le plateau
            edges = self.to_edges(warped)
            gray_edges = cv2.cvtColor(edges, cv2.COLOR_BGR2GRAY)
            cells = self.detect_cells(gray_edges, min_area=2000)  # min_area adapté à la taille des cases Monopoly
            warped_with_cells = self.draw_cells(warped, cells)

            ret, buffer = cv2.imencode('.jpg', warped_with_cells, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def release(self):
        """Libère la caméra pour éviter de bloquer d'autres applications."""
        self.cap.release()
