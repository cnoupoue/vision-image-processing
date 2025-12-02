import cv2
import numpy as np


class DiceDetector:
    def __init__(self):
        # On garde les réglages "petits points"
        self.min_area = 5
        self.max_area = 400
        self.min_circularity = 0.3

    def detect(self, warped_img):
        h, w = warped_img.shape[:2]

        # 1. ZONE DE RECHERCHE
        x1, y1 = int(w * 0.35), int(h * 0.35)
        x2, y2 = int(w * 0.65), int(h * 0.65)
        roi = warped_img[y1:y2, x1:x2]

        # 2. PRÉ-TRAITEMENT
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # --- AMELIORATION CONTRASTE ---
        # On "étire" les couleurs : le gris devient blanc, le noir devient plus noir.
        # Ça aide énormément quand on manque de lumière.
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # --- CORRECTION MAJEURE : OTSU ---
        # Au lieu de mettre "150", on met "0" et on ajoute le drapeau THRESH_OTSU.
        # OpenCV va analyser ton image et trouver tout seul la limite entre le dé et les points.
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # 3. ANALYSE
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        dice_pips = []

        # Vue Debug : On convertit le thresh en couleur pour dessiner dessus
        debug_view = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)

            if perimeter == 0: continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))

            # Dessin rouge pour tout ce qu'il voit
            cv2.drawContours(debug_view, [cnt], -1, (0, 0, 255), 1)

            if area > self.min_area and area < self.max_area and circularity > self.min_circularity:
                dice_pips.append(cnt)
                # Vert pour les points validés
                cv2.drawContours(debug_view, [cnt], -1, (0, 255, 0), -1)

        total_score = len(dice_pips)

        # 4. AFFICHAGE
        cv2.drawContours(roi, dice_pips, -1, (0, 255, 0), 2)
        warped_img[y1:y2, x1:x2] = roi
        cv2.rectangle(warped_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        if total_score > 0:
            cv2.putText(warped_img, f"SCORE: {total_score}", (x1, y1 - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return warped_img, total_score, debug_view