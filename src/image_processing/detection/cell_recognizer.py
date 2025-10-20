import cv2
import pytesseract


class CellRecognizer:
    def __init__(self):
        try:
            # essaie de détecter tesseract automatiquement
            pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
            pytesseract.get_tesseract_version()
            self.available = True
        except (EnvironmentError, pytesseract.TesseractNotFoundError):
            print("⚠️ Tesseract non trouvé, la reconnaissance de texte sera désactivée.")
            self.available = False

    def recognize_cell(self, cell_img):
        avg_color = cv2.mean(cell_img)[:3]
        text = ""
        if self.available:
            try:
                gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
                text = pytesseract.image_to_string(thresh, config='--psm 6').strip()
            except Exception:
                text = ""
        else:
            text = "N/A"
        return {"text": text, "color": avg_color}
