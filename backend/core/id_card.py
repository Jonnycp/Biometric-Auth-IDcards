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
    pts = np.asarray(pts, dtype="float32").reshape(4, 2)
    #il vecchio approccio non funzionava se carta ruotata
    center = pts.mean(axis=0)
    angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0]) #angolo di ogni punto rispetto al centro
    rect = pts[np.argsort(angles)] #angoli in ordine crescente
    tl_idx = int(np.argmin(rect.sum(axis=1))) #vertice top-left (somma x+y minima)
    rect = np.roll(rect, -tl_idx, axis=0) #lo mette come primo vertice, mantenendo l'ordine orario
    # Garantisce che il lato superiore (TL->TR) sia quello lungo (formato landscape ID-1)
    top_len = np.linalg.norm(rect[1] - rect[0])
    left_len = np.linalg.norm(rect[3] - rect[0])
    if top_len < left_len:
        cand_cw = np.roll(rect, -1, axis=0)
        cand_ccw = np.roll(rect, 1, axis=0)
        rect = cand_cw if (cand_cw[0, 1] + cand_cw[1, 1]) < (cand_ccw[0, 1] + cand_ccw[1, 1]) else cand_ccw

    return rect.astype("float32")

# Verifica che i 4 vertici formino un quadrilatero compatibile con una carta ID-1 (ratio 1.585)
def isValidCardQuad(pts: np.ndarray, min_ratio: float = 1.25, max_ratio: float = 2.05):
    rect = orderPoints(pts)

    top = np.linalg.norm(rect[1] - rect[0])
    right = np.linalg.norm(rect[2] - rect[1])
    bottom = np.linalg.norm(rect[2] - rect[3])
    left = np.linalg.norm(rect[3] - rect[0])

    if min(top, right, bottom, left) < 20:
        return False, "lato troppo corto"

    # Coerenza lati opposti (evita trapezi degenerati)
    if min(top, bottom) / max(top, bottom) < 0.55 or min(left, right) / max(left, right) < 0.55:
        return False, f"lati opposti sbilanciati (T={top:.0f}, B={bottom:.0f}, L={left:.0f}, R={right:.0f})"

    # Rapporto d'aspetto compatibile con formato ID-1
    avg_w = (top + bottom) / 2.0
    avg_h = (left + right) / 2.0
    ratio = max(avg_w, avg_h) / min(avg_w, avg_h)
    if not (min_ratio <= ratio <= max_ratio):
        return False, f"ratio={ratio:.2f} fuori range [{min_ratio}, {max_ratio}]"

    # Angoli interni plausibili (evita poligoni schiacciati)
    for i in range(4):
        p_prev = rect[(i - 1) % 4]
        p_curr = rect[i]
        p_next = rect[(i + 1) % 4]
        v1 = p_prev - p_curr
        v2 = p_next - p_curr
        cos_a = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.degrees(np.arccos(np.clip(cos_a, -1.0, 1.0)))
        if not (55.0 <= angle <= 125.0):
            return False, f"angolo={angle:.1f}° fuori range [55, 125]"

    return True, f"ok (ratio={ratio:.2f})"

# Estrae e valida il quadrilatero con varie percentuali
def _detectQuadOnEdges(edged: np.ndarray, min_area: float, debug: bool = False):
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda c: cv2.contourArea(cv2.convexHull(c)), reverse=True)[:5] #prende i 5 più grandi

    for i, c in enumerate(contours): #analizza i contorni selezionati
        peri = cv2.arcLength(c, True)
        area = cv2.contourArea(c)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True) #approssimazione poligonale con tolleranza del2%

        if len(approx) == 4 and area > min_area:
            valid, reason = isValidCardQuad(approx)
            if debug:
                print(f"[DEBUG]   Top #{i} raw: area={area:.0f} -> {reason}")
            if valid:
                return approx

        # se poligono non validi, prova con l'inviluppo complesso (hull) e varie tolleranze
        hull = cv2.convexHull(c)
        peri_h = cv2.arcLength(hull, True)
        area_h = cv2.contourArea(hull)
        if area_h <= min_area:
            continue

        for eps in (0.02, 0.03, 0.04, 0.05):
            approx_h = cv2.approxPolyDP(hull, eps * peri_h, True)
            if len(approx_h) == 4:
                valid, reason = isValidCardQuad(approx_h)
                if debug:
                    print(f"[DEBUG]   Top #{i} hull (eps={eps}): area={area_h:.0f} -> {reason}")
                if valid:
                    return approx_h
                break

    return None

# Trova bordi e 4 vertici del documento
def findCardContour(image: np.ndarray, max_dim: int = 800, debug: bool = False):
    orig_h, orig_w = image.shape[:2]
    scale = min(1.0, max_dim / max(orig_h, orig_w)) # ridimensiona se più grande di max_dim
    work = cv2.resize(image, (int(orig_w * scale), int(orig_h * scale))) if scale < 1.0 else image

    h, w = work.shape[:2]
    img_area = h * w
    min_area = img_area * 0.1
    gray = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)

    # Due strategie: prima filtro bilaterale (ignora texture dello sfondo), poi fallback classico
    attempts = [
        ("bilateral+canny(75,200)", cv2.bilateralFilter(gray, 9, 75, 75), 75, 200),
        ("gaussian+canny(50,150)", cv2.GaussianBlur(gray, (5, 5), 0), 50, 150),
    ]

    last_edged = None
    for name, smooth, t1, t2 in attempts:
        edged = cv2.Canny(smooth, t1, t2)
        edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) #chiudi piccole interruzioni lungo i bordi
        last_edged = edged

        if debug:
            px_pct = np.count_nonzero(edged) / img_area * 100
            print(f"[DEBUG] Tentativo '{name}': morph_px={px_pct:.2f}%")

        target_contour = _detectQuadOnEdges(edged, min_area, debug=debug)
        if target_contour is not None:
            punti = target_contour.reshape(4, 2).astype("float32") / scale
            return edged, punti

    return last_edged, None

# Identifica contorno carta di identità e raddrizza prospettiva
# Formato standard ID-1 (85.6 mm × 54 mm) con ratio ICAO TD1 (856x540)
def fixProspective(image: np.ndarray, targetSize=(856, 540), debug: bool = False):
    original = image.copy()
    _, punti = findCardContour(image, debug=debug)
    if punti is None:
        return original, False

    rect = orderPoints(punti)

    out_w, out_h = targetSize
    out_pts = np.array([
        [0, 0],
        [out_w - 1, 0],
        [out_w - 1, out_h - 1],
        [0, out_h - 1]], dtype="float32")

    # matrice di trasformazione prospettica
    matrix = cv2.getPerspectiveTransform(rect, out_pts)
    fixedImage = cv2.warpPerspective(original, matrix, targetSize)
    return fixedImage, True

# Pipeline unificata per correggere immagine ID card
def preprocessIDCard(img: np.ndarray):
    fixes = {"prospective": False, "contrast": False} 

    img, rectified = fixProspective(img)
    fixes["prospective"] = rectified

    img = enhanceContrast(img)
    fixes["contrast"] = True

    return img, fixes

# Decodifica immagine da bytes a numpy array BGR
def decodeImage(image_bytes: bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img