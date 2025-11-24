import cv2
import numpy as np
import os


class Camera:
    def __init__(self, width=1280, height=720):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # État global de la détection (c'est cette variable que le front-end regarde)
        self.is_board_detected = False

        # Stabilisation spatiale
        self.prev_pts = None
        self.frames_without_detection = 0
        self.MAX_MISSED_FRAMES = 10

        # Stabilisation de la rotation
        self.last_rotation_code = None

        # Template Matching
        self.go_template = None
        template_path = 'assets/go_template.jpg'
        if os.path.exists(template_path):
            self.go_template = cv2.imread(template_path, 0)
        else:
            print(f"ATTENTION : Manque {template_path}")

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

    def find_go_corner_index(self, warped_img):
        if self.go_template is None: return None
        h, w = warped_img.shape[:2]
        gray_img = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
        cw = int(w * 0.15)
        ch = int(h * 0.15)
        rois = [(0, 0, cw, ch), (w - cw, 0, cw, ch), (w - cw, h - ch, cw, ch), (0, h - ch, cw, ch)]
        best_score = 0
        best_idx = -1
        for idx, (x, y, rw, rh) in enumerate(rois):
            roi = gray_img[y:y + rh, x:x + rw]
            try:
                resized_template = cv2.resize(self.go_template, (rw, rh))
                res = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > best_score:
                    best_score = max_val
                    best_idx = idx
            except:
                pass
        if best_score > 0.45: return best_idx
        return None

    def apply_rotation(self, image, go_idx):
        if go_idx is None:
            rotation = self.last_rotation_code
        else:
            rotation = None
            if go_idx == 0:
                rotation = cv2.ROTATE_180
            elif go_idx == 1:
                rotation = cv2.ROTATE_90_CLOCKWISE
            elif go_idx == 3:
                rotation = cv2.ROTATE_90_COUNTERCLOCKWISE
            self.last_rotation_code = rotation
        if self.last_rotation_code is not None:
            return cv2.rotate(image, self.last_rotation_code)
        return image

    def draw_monopoly_grid(self, warped_img):
        h, w = warped_img.shape[:2]
        corner_pct = 0.135
        prop_pct = (1.0 - (2 * corner_pct)) / 9.0
        cuts = [0.0, corner_pct]
        curr = corner_pct
        for _ in range(9): curr += prop_pct; cuts.append(curr)
        cuts.append(1.0)
        x_cuts = [int(p * w) for p in cuts]
        y_cuts = [int(p * h) for p in cuts]

        inner_start_x, inner_end_x = x_cuts[1], x_cuts[-2]
        inner_start_y, inner_end_y = y_cuts[1], y_cuts[-2]
        warped_img[inner_start_y:inner_end_y, inner_start_x:inner_end_x] = [0, 0, 0]

        color = (0, 255, 0)
        for x in x_cuts:
            cv2.line(warped_img, (x, 0), (x, inner_start_y), color, 2)
            cv2.line(warped_img, (x, inner_end_y), (x, h), color, 2)
        for y in y_cuts:
            cv2.line(warped_img, (0, y), (inner_start_x, y), color, 2)
            cv2.line(warped_img, (inner_end_x, y), (w, y), color, 2)
        cv2.rectangle(warped_img, (inner_start_x, inner_start_y), (inner_end_x, inner_end_y), color, 2)

        # Draw GO
        br_x, br_y = x_cuts[-2], y_cuts[-2]
        overlay = warped_img.copy()
        cv2.rectangle(overlay, (br_x, br_y), (w, h), (0, 255, 0), -1)
        cv2.addWeighted(overlay, 0.4, warped_img, 0.6, 0, warped_img)
        text_size = cv2.getTextSize("DEPART", cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = br_x + (w - br_x - text_size[0]) // 2
        text_y = br_y + (h - br_y + text_size[1]) // 2
        cv2.putText(warped_img, "DEPART", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return warped_img

    def process_frame(self):
        original = self.get_frame()
        display = original.copy()

        # 1. Tenter la détection
        pts = self.detect_board_contour(original)

        # 2. LOGIQUE D'ÉTAT (CRUCIALE POUR LE TEXTE)
        if pts is not None:
            # Cas A : On voit le plateau maintenant
            self.prev_pts = pts
            self.frames_without_detection = 0
            self.is_board_detected = True  # <--- C'est ici que ça passe à True

        elif self.prev_pts is not None:
            # Cas B : On l'a vu il y a pas longtemps (mémoire)
            self.frames_without_detection += 1
            if self.frames_without_detection < self.MAX_MISSED_FRAMES:
                pts = self.prev_pts
                self.is_board_detected = True  # <--- On maintient à True
            else:
                self.is_board_detected = False  # <--- Trop vieux, on passe à False
        else:
            # Cas C : Jamais vu ou perdu
            self.is_board_detected = False  # <--- False

        # 3. Traitement visuel
        if self.is_board_detected and pts is not None:
            try:
                warped = self.four_point_transform(original, pts)
                go_idx = self.find_go_corner_index(warped)
                rotated_warped = self.apply_rotation(warped, go_idx)
                final_img = self.draw_monopoly_grid(rotated_warped)
                return final_img
            except Exception as e:
                print(f"Erreur processing: {e}")
                return display  # En cas de pépin, on rend l'original

        return display

    def generate_jpeg_frames(self):
        while True:
            processed = self.process_frame()
            ret, buffer = cv2.imencode('.jpg', processed)
            if not ret: continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    def release(self):
        self.cap.release()