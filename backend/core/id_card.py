import numpy as np
import cv2

# Migliora contrasto immagine con CLAHE (Contrast Limited Adaptive Histogram Equalization)
# CLAHE lavora a zone di tileGridSize aumentando di clipLimit, evitando di creare artefatti
def enhanceContrast(image: np.ndarray, clipLimit: float = 2.0, tileGridSize: tuple = (8, 8)):
    # BGR (blue, green, red) -> LAB (Lightness, A, B)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB) 
    l_channel, a_channel, b_channel = cv2.split(lab)

    # Applica CLAHE al canale L
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    l_enhanced = clahe.apply(l_channel)

    # Ricomponi in LAB e poi torna a BGR
    lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
    return cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

# Ordina punti per correzione prospettiva in senso orario: top-left (0,0), top-right, bottom-right, bottom-left
def orderPoints(pts: np.ndarray):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1) # somma x+y
    rect[0] = pts[np.argmin(s)]  # top-left (il più piccolo)
    rect[2] = pts[np.argmax(s)]  # bottom-right (il più grande)

    diff = np.diff(pts, axis=1) #differenza y-x
    rect[1] = pts[np.argmin(diff)]  # top-right (il più piccolo: differenza minore (x più grande di y))
    rect[3] = pts[np.argmax(diff)]  # bottom-left (il più grande)

    return rect

# Identifica contorno carta di identità e raddrizza prospettiva
# Formato standard ID-1 (85.6 mm × 54 mm) con ratio ICAO TD1 (856x540)
def fixProspective(image: np.ndarray, targetSize = (856, 856)):
    # Riduci rumore
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #bianco è nero, più efficiente per trovare contorni
    blurred = cv2.GaussianBlur(gray, (5, 5), 0) #sfocando leggermente, riduci disturbi e rumore
    edged = cv2.Canny(blurred, 50, 150) #trova bordi

    # Trova contorni
    counters, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #trova forme esterne
    counters = sorted(counters, key=cv2.contourArea, reverse=True)[:5] #prende le 5 più grandi

    # Trova contorno della carta di identità
    target_contour = None
    min_area = image.shape[0] * image.shape[1] * 0.1 #almeno 10% dell'immagine
    for c in counters:
        peri = cv2.arcLength(c, True)
        area = cv2.contourArea(c)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True) #approssima contorno a poligono
        if len(approx) == 4 and area > min_area:
            target_contour = approx
            break

    if target_contour is None:
        # Se non trova un rettangolo netto, ritorna immagine originale
        return original, False

    # Correzione prospettiva
    punti = target_contour.reshape(4, 2)
    rect = orderPoints(punti)

    # Matrice output
    out_w, out_h = targetSize
    out_pts = np.array([
        [0, 0],
        [out_w - 1, 0],
        [out_w - 1, out_h - 1],
        [0, out_h - 1]], dtype="float32")

    matrix = cv2.getPerspectiveTransform(rect, out_pts) #combina punti input e output per calcolare matrice prospettiva
    fixedImage = cv2.warpPerspective(original, matrix, targetSize)
    return fixedImage, True


