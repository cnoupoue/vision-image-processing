import cv2
import numpy as np
import os
from game.dice import DiceDetector


class Camera:
    def __init__(self, width=1280, height=720):
        self.cap = cv2.VideoCapture(1)  # Vérifie que c'est bien 0 ou 1
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.is_board_detected = False
        self.prev_pts = None
        self.frames_without_detection = 0
        self.MAX_MISSED_FRAMES = 10

        self.dice_detector = DiceDetector()
        self.validated_dice_value = None  # La valeur finale validée à envoyer au jeu
        # Stabilisation rotation : on garde la dernière rotation valide
        self.current_rotation = None

        # Chargement du template
        # ATTENTION : Assure-toi que le fichier est bien dans src/assets/go_template.jpg
        self.go_template = None
        template_path = 'assets/go_template.jpg'
        if os.path.exists(template_path):
            # On le charge en niveau de gris
            self.go_template = cv2.imread(template_path, 0)
            print(f"Template DÉPART chargé avec succès : {template_path}")
        else:
            print(f"ERREUR CRITIQUE : Impossible de trouver {template_path}")
            # On crée un carré noir par défaut pour éviter le crash
            self.go_template = np.zeros((100, 100), dtype=np.uint8)

    def find_go_corner_index(self, warped_img):
        if self.go_template is None: return None
        h, w = warped_img.shape[:2]
        gray_img = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
        cw = int(w * 0.15)
        ch = int(h * 0.15)

        # Les 4 coins
        rois = [(0, 0, cw, ch), (w - cw, 0, cw, ch), (w - cw, h - ch, cw, ch), (0, h - ch, cw, ch)]

        best_score = -1
        best_idx = -1

        for idx, (x, y, rw, rh) in enumerate(rois):
            roi = gray_img[y:y + rh, x:x + rw]

            # Redimensionnement du template
            resized_template = cv2.resize(self.go_template, (rw, rh))

            # Matching
            res = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)


            if max_val > best_score:
                best_score = max_val
                best_idx = idx

        # Si le score est suffisant, on retourne l'index
        if best_score > 0.25:
            # J'ai aussi supprimé le rectangle VERT de confirmation ici
            return best_idx

        return None

    def apply_rotation(self, image, go_idx):
        """
        Tourne l'image pour que la case DÉPART (go_idx) se retrouve en BAS À DROITE.
        """
        rotation = None

        # Si on a trouvé une nouvelle orientation valide, on la garde
        if go_idx is not None:
            if go_idx == 0:  # Départ en Haut-Gauche -> Rotation 180
                rotation = cv2.ROTATE_180
            elif go_idx == 1:  # Départ en Haut-Droite -> Rotation 90 Horaire
                rotation = cv2.ROTATE_90_CLOCKWISE
            elif go_idx == 2:  # Départ en Bas-Droite -> Pas de rotation (C'est la norme)
                rotation = None
            elif go_idx == 3:  # Départ en Bas-Gauche -> Rotation 90 Anti-Horaire
                rotation = cv2.ROTATE_90_COUNTERCLOCKWISE

            # Mise à jour de la mémoire
            self.current_rotation = rotation

        # Application de la rotation mémorisée
        if self.current_rotation is not None:
            return cv2.rotate(image, self.current_rotation)

        return image

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret: return np.zeros((720, 1280, 3), dtype=np.uint8)
        return frame

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # TL
        rect[2] = pts[np.argmax(s)]  # BR
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # TR
        rect[3] = pts[np.argmax(diff)]  # BL
        return rect

    def four_point_transform(self, image, pts):
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))
        side = max(maxWidth, maxHeight)
        dst = np.array([[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(image, M, (side, side))

    def detect_board_contour(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best_cnt = None
        max_area = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 20000:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if len(approx) == 4 and area > max_area:
                    best_cnt = approx
                    max_area = area
        return best_cnt.reshape(4, 2) if best_cnt is not None else None

    def draw_monopoly_grid(self, warped_img):
        # Cette méthode sert juste à l'AFFICHAGE pour toi (debug)
        squares = self.get_grid_coordinates(warped_img)

        for idx, (x, y, w, h) in squares.items():
            # Dessine un rectangle vert autour de la case
            cv2.rectangle(warped_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Affiche le numéro de la case au centre (pour vérifier l'ordre)
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.putText(warped_img, str(idx), (center_x - 10, center_y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        return warped_img

        # ... (Tout le début jusqu'à apply_rotation reste pareil) ...

    def get_grid_coordinates(self, warped_img):
        """
        CALCUL MATHEMATIQUE : Découpe le plateau en 40 zones.
        C'est le cerveau de la vision.
        """
        h, w = warped_img.shape[:2]
        squares = {}

        CORNER_PCT = 0.135
        MIDDLE_PCT = (1.0 - (2 * CORNER_PCT)) / 9.0

        cuts = [0.0, CORNER_PCT]
        curr = CORNER_PCT
        for _ in range(9):
            curr += MIDDLE_PCT
            cuts.append(curr)
        cuts.append(1.0)

        col_x = [int(p * w) for p in cuts]
        row_y = [int(p * h) for p in cuts]

        # --- GENERATION DES CASES (0=Départ, etc) ---

        # BAS (0-10)
        y_start, h_cell = row_y[-2], row_y[-1] - row_y[-2]
        for i in range(11):
            squares[i] = (col_x[-(i + 2)], y_start, col_x[-(i + 1)] - col_x[-(i + 2)], h_cell)

        # GAUCHE (11-19)
        x_start, w_cell = col_x[0], col_x[1] - col_x[0]
        for i in range(1, 10):
            idx = 10 + i
            squares[idx] = (x_start, row_y[-(i + 2)], w_cell, row_y[-(i + 1)] - row_y[-(i + 2)])

        # HAUT (20-30)
        y_start, h_cell = row_y[0], row_y[1] - row_y[0]
        for i in range(11):
            squares[20 + i] = (col_x[i], y_start, col_x[i + 1] - col_x[i], h_cell)

        # DROITE (31-39)
        x_start, w_cell = col_x[-2], col_x[-1] - col_x[-2]
        for i in range(1, 10):
            squares[30 + i] = (x_start, row_y[i], w_cell, row_y[i + 1] - row_y[i])

        return squares

    def process_frame(self):
        original = self.get_frame()
        display = original.copy()
        squares = None  # Par défaut, pas de cases

        # 1. Detection
        pts = self.detect_board_contour(original)

        # Logique de stabilité (ta logique existante)
        if pts is not None:
            self.prev_pts = pts
            self.frames_without_detection = 0
            self.is_board_detected = True
        elif self.prev_pts is not None:
            self.frames_without_detection += 1
            if self.frames_without_detection < self.MAX_MISSED_FRAMES:
                pts = self.prev_pts
                self.is_board_detected = True
            else:
                self.is_board_detected = False
        else:
            self.is_board_detected = False

        # 2. Traitement
        if self.is_board_detected and pts is not None:
            try:
                # 1. Mise à plat
                warped = self.four_point_transform(original, pts)
                # 2. Rotation auto
                go_idx = self.find_go_corner_index(warped)
                rotated_warped = self.apply_rotation(warped, go_idx)

                # 3. RECUPERATION DES CASES (Le cœur du système)
                squares = self.get_grid_coordinates(rotated_warped)

                # --- DETECTION DES ---
                final_img, dice_score, debug_view = self.dice_detector.detect(rotated_warped)
                # small_debug = cv2.resize(debug_view, (150, 150))
                #final_img[0:150, 0:150] = small_debug
                if dice_score > 0:
                    print(f"Dés détectés : {dice_score}")
                    self.validated_dice_value = dice_score
                # 4. Dessin pour le debug (OPTIONNEL, juste pour tes yeux)
                for idx, (x, y, w, h) in squares.items():
                    cv2.rectangle(rotated_warped, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    # Affiche le numéro si tu veux vérifier
                    # cv2.putText(rotated_warped, str(idx), (x+5, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

                return rotated_warped, squares

            except Exception as e:
                print(f"Erreur processing: {e}")
                return display, squares

        return display, squares

    def generate_jpeg_frames(self):
        while True:
            processed = self.process_frame()
            ret, buffer = cv2.imencode('.jpg', processed)
            if not ret: continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    def release(self):
        self.cap.release()
