import cv2
import pytesseract
import os
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image_path):
    if not os.path.exists(image_path):
        return "", 0
    
    img = cv2.imread(image_path)
    if img is None:
        return "", 0
    
    height, width = img.shape[:2]
    is_small_or_char = width < 200 or height < 200 or 'char' in image_path.lower()
    
    if is_small_or_char:
        config = '--oem 3 --psm 10'
    else:
        config = '--oem 3 --psm 6'
    
    lang = 'ben'
    
    # Try raw image first
    try:
        raw_text = pytesseract.image_to_string(img, lang=lang, config=config).strip()
        if raw_text:
            data = pytesseract.image_to_data(img, lang=lang, config=config, output_type=pytesseract.Output.DICT)
            conf_list = [int(c) for c in data['conf'] if c != '-1']
            avg_conf = int(np.mean(conf_list)) if conf_list else 0
            return raw_text, avg_conf
    except:
        pass
    
    # Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    
    if is_small_or_char:
        # For chars: Stricter thresholding and erosion to isolate single char
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((2,2), np.uint8)  # Erosion kernel
        thresh = cv2.erode(thresh, kernel, iterations=1)  # Remove small noise
        gray = thresh
    
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    resized = cv2.resize(gray, None, fx=1.5 if is_small_or_char else 1.2, fy=1.5 if is_small_or_char else 1.2, interpolation=cv2.INTER_LANCZOS4)
    
    try:
        text = pytesseract.image_to_string(resized, lang=lang, config=config).strip()
        data = pytesseract.image_to_data(resized, lang=lang, config=config, output_type=pytesseract.Output.DICT)
        conf_list = [int(c) for c in data['conf'] if c != '-1']
        avg_conf = int(np.mean(conf_list)) if conf_list else 0
        return text, avg_conf
    except:
        return "", 0