import cv2
import numpy as np


class Camera:
    def __init__(self, width=1280, height=720):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Variables pour la stabilisation
        self.prev_pts = None
        self.frames_without_detection = 0
        self.MAX_MISSED_FRAMES = 10  # Garde le dernier plateau connu pendant 10 frames

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return np.zeros((720, 1280, 3), dtype=np.uint8)
        return frame

    def order_points(self, pts):
        """
        Ordonne les coordonnées : haut-gauche, haut-droit, bas-droit, bas-gauche
        Nécessaire pour que le redressement de perspective ne soit pas inversé.
        """
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # TL
        rect[2] = pts[np.argmax(s)]  # BR
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # TR
        rect[3] = pts[np.argmax(diff)]  # BL
        return rect

    def four_point_transform(self, image, pts):
        """Transforme la perspective pour obtenir une vue de dessus (oiseau)."""
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # Calcul de la largeur maximale
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))

        # Calcul de la hauteur maximale
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))

        # On force un carré pour le Monopoly (optionnel, mais plus joli)
        side = max(maxWidth, maxHeight)

        dst = np.array([
            [0, 0],
            [side - 1, 0],
            [side - 1, side - 1],
            [0, side - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (side, side))
        return warped

    def detect_board_contour(self, frame):
        """Trouve le plus grand quadrilatère dans l'image."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Petit flou pour réduire le bruit de la nappe/table
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Canny plus permissif ou adaptatif
        edges = cv2.Canny(blurred, 30, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_cnt = None
        max_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 20000:  # Filtre les petits objets
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

                if len(approx) == 4:
                    if area > max_area:
                        best_cnt = approx
                        max_area = area

        if best_cnt is not None:
            return best_cnt.reshape(4, 2)
        return None

    def draw_monopoly_grid(self, warped_img):
        """
        Masque le centre en noir et dessine les séparations des cases
        uniquement sur le contour.
        """
        h, w = warped_img.shape[:2]

        # Un Monopoly standard c'est 11x11 unités (9 cases + 2 coins par côté)
        units = 11

        # Taille d'une case (approximative)
        u_w = w // units  # Largeur d'une unité
        u_h = h // units  # Hauteur d'une unité

        # 1. LE "TEJ" DU MILIEU : Remplir le centre de noir
        # On définit la zone centrale : de la fin de la 1ère case jusqu'au début de la dernière
        # Syntaxe NumPy : image[y_start : y_end, x_start : x_end] = couleur
        warped_img[u_h: h - u_h, u_w: w - u_w] = [0, 0, 0]

        # 2. Dessiner les lignes de séparation des cases (uniquement sur les bords)
        color = (0, 255, 0)  # Vert matrix
        thickness = 2

        for i in range(units + 1):
            # --- Lignes Verticales ---
            x = int(w * i / units)
            # Trait sur la bande du HAUT
            cv2.line(warped_img, (x, 0), (x, u_h), color, thickness)
            # Trait sur la bande du BAS
            cv2.line(warped_img, (x, h - u_h), (x, h), color, thickness)

            # --- Lignes Horizontales ---
            y = int(h * i / units)
            # Trait sur la bande de GAUCHE
            cv2.line(warped_img, (0, y), (u_w, y), color, thickness)
            # Trait sur la bande de DROITE
            cv2.line(warped_img, (w - u_w, y), (w, y), color, thickness)

        # Optionnel : Dessiner un cadre vert autour de la zone noire centrale pour faire propre
        cv2.rectangle(warped_img, (u_w, u_h), (w - u_w, h - u_h), color, thickness)

        return warped_img

    def process_frame(self):
        original_frame = self.get_frame()
        display_frame = original_frame.copy()

        # 1. Détection
        pts = self.detect_board_contour(original_frame)

        # 2. Stabilisation
        if pts is not None:
            self.prev_pts = pts
            self.frames_without_detection = 0

            # Dessiner le contour détecté sur l'image originale pour le debug
            cv2.drawContours(display_frame, [pts.astype(int).reshape((-1, 1, 2))], -1, (0, 255, 0), 2)

        elif self.prev_pts is not None:
            # Si on perd le plateau, on garde le dernier connu quelques instants
            self.frames_without_detection += 1
            if self.frames_without_detection < self.MAX_MISSED_FRAMES:
                pts = self.prev_pts

        # 3. Transformation & Affichage
        if pts is not None:
            # On redresse l'image (Vue de dessus)
            warped = self.four_point_transform(original_frame, pts)

            # On dessine la grille théorique PAR DESSUS l'image redressée
            warped_with_grid = self.draw_monopoly_grid(warped.copy())

            # Pour l'interface web, on renvoie l'image redressée.
            # Si tu préfères voir la caméra normale avec le cadre vert, renvoie 'display_frame'
            return warped_with_grid

        return display_frame

    def generate_jpeg_frames(self):
        while True:
            processed_frame = self.process_frame()

            # Encodage JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def release(self):
        self.cap.release()
