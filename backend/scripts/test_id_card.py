"""
test_id_card.py — Pipeline Ottimizzata Real-Time:
- Module Pruning (solo detection + recognition)
- Risoluzione differenziata: 640x640 per la CIE, 320x320 per la Live Camera
- Frame Skipping: video fluido a 30 FPS costanti su CPU M2
- Anti-Spoofing MiniFASNet + Face Matching
"""

import cv2
import numpy as np
import sys
import os
import onnxruntime as ort
from insightface.app import FaceAnalysis

# ─── 1. CONFIGURAZIONE ────────────────────────────────────────────────────────

ID_CARD_PATH = "/Users/jonathan/Desktop/Tesi/backend/datasets/id_cards/jonathan.jpeg"
MODEL_NAME = "buffalo_l"
LIVENESS_MODEL_PATH = "/Users/jonathan/Desktop/Tesi/backend/.insightface/minifasnet_v2.onnx"

SIMILARITY_THRESHOLD = 0.35
LIVENESS_THRESHOLD = 0.50

# Salta l'OCR per partire istantaneamente
RUN_OCR = False

# Elabora l'AI ogni N frame (2 = ~15 valutazioni/sec con video a 30 FPS fluidi)
INFERENCE_EVERY_N_FRAMES = 2

CAMERA_INDEX = 2

# ─── 2. FUNZIONI DI SUPPORTO ──────────────────────────────────────────────────

def cosine_similarity(emb1, emb2):
    dot = np.dot(emb1, emb2)
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))


def crop_for_liveness(img, bbox, scale=2.7, out_size=(80, 80)):
    src_h, src_w, _ = img.shape
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1

    scale = min((src_h - 1) / h, min((src_w - 1) / w, scale))
    new_w = w * scale
    new_h = h * scale
    cx = x1 + w / 2
    cy = y1 + h / 2

    left = int(cx - new_w / 2)
    top = int(cy - new_h / 2)
    right = int(cx + new_w / 2)
    bottom = int(cy + new_h / 2)

    if left < 0:
        right -= left
        left = 0
    if top < 0:
        bottom -= top
        top = 0
    if right > src_w - 1:
        left -= right - src_w + 1
        right = src_w - 1
    if bottom > src_h - 1:
        top -= bottom - src_h + 1
        bottom = src_h - 1

    crop = img[max(0, top):min(src_h, bottom), max(0, left):min(src_w, right)]
    if crop.size == 0:
        return None
    return cv2.resize(crop, out_size)

def extract_and_rectify_card(image):
    """
    Rileva i 4 angoli della carta d'identità nell'immagine,
    ne corregge la prospettiva e la ritaglia su ratio ICAO TD1 (856x540).
    """
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Rileva i bordi
    edged = cv2.Canny(blurred, 50, 150)
    
    # Trova i contorni e ordina per area decrescente
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    card_contour = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # Se ha 4 vertici ed è sufficientemente grande
        if len(approx) == 4 and cv2.contourArea(c) > (image.shape[0] * image.shape[1] * 0.1):
            card_contour = approx
            break
            
    if card_contour is None:
        # Fallback: se non trova un rettangolo netto, usa l'immagine originale
        return image
        
    # Ordina i 4 punti: top-left, top-right, bottom-right, bottom-left
    pts = card_contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # Top-left
    rect[2] = pts[np.argmax(s)] # Bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # Top-right
    rect[3] = pts[np.argmax(diff)] # Bottom-left
    
    # Destinazione standard ratio TD1 (856x540)
    dst = np.array([
        [0, 0],
        [856 - 1, 0],
        [856 - 1, 540 - 1],
        [0, 540 - 1]
    ], dtype="float32")
    
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(orig, M, (856, 540))
    return warped

def predict_liveness(session, crop_bgr):
    blob = crop_bgr.astype(np.float32)
    blob = np.transpose(blob, (2, 0, 1))
    blob = np.expand_dims(blob, axis=0)

    outputs = session.run(None, {"input": blob})
    logits = outputs[0][0]

    exp_l = np.exp(logits - np.max(logits))
    probs = exp_l / np.sum(exp_l)

    return probs[1], probs[0], probs[2]  # real, print, replay

# ─── 3. CARICAMENTO E OTTIMIZZAZIONE MODELLI ───────────────────────────────────

print("=" * 65)
print("   SISTEMA BIOMETRICO AD ALTE PRESTAZIONI (M2 OPTIMIZED)")
print("=" * 65)

# 1. Carichiamo InsightFace SOLO con i moduli che servono
print(f"\n[1/3] Inizializzazione InsightFace con Module Pruning...")
app = FaceAnalysis(
    name=MODEL_NAME, 
    root="~/.insightface",
    allowed_modules=['detection', 'recognition']  # Esclude genderage e 106-landmarks
)
# Per la webcam usiamo det_size=(320, 320) per massima fluidità
app.prepare(ctx_id=-1, det_size=(320, 320))
print("   ✅ Detector & ArcFace pronti!")

# 2. Caricamento MiniFASNet ONNX
print(f"\n[2/3] Caricamento MiniFASNet...")
liveness_session = ort.InferenceSession(LIVENESS_MODEL_PATH, providers=["CPUExecutionProvider"])
print("   ✅ Anti-Spoofing pronto!")

# 3. Estrazione volto CIE (con risoluzione alta 640x640 una tantum)
print(f"\n[3/3] Estrazione volto da CIE ({ID_CARD_PATH})...")
id_card_img = extract_and_rectify_card(cv2.imread(ID_CARD_PATH))
if id_card_img is None:
    print(f"❌ Impossibile trovare il file {ID_CARD_PATH}")
    sys.exit(1)

# Per la CIE impostiamo momentaneamente det_size a 640 per non perdere dettagli
app.det_model.det_size = (640, 640)
cie_faces = app.get(id_card_img)
# Reimpostiamo a 320x320 per la webcam live
app.det_model.det_size = (320, 320)

if not cie_faces:
    print("❌ Nessun volto trovato nella CIE!")
    sys.exit(1)

best_cie_face = max(cie_faces, key=lambda f: f.det_score)
reference_embedding = best_cie_face.embedding.copy()
print(f"   ✅ Volto CIE registrato! (Confidenza: {best_cie_face.det_score:.2f})")

# ─── 4. WEBCAM STREAM FLUIDO ──────────────────────────────────────────────────

print("\n" + "=" * 65)
print("   STREAM WEBCAM ATTIVO — 30 FPS")
print("   👉 [S] Salva screenshot   |   [Q/ESC] Esci")
print("=" * 65 + "\n")

cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

# Thumbnail CIE
id_card_thumb = extract_and_rectify_card(id_card_img)
id_card_thumb = cv2.resize(id_card_thumb, (160, 213))

# Variabili di stato per mantenere i risultati tra i frame saltati
last_faces = []
last_box_color = (180, 180, 180)
last_header = "Inquadra il volto..."
last_sub = ""
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # Esegui l'AI solo ogni N fotogrammi
    if frame_count % INFERENCE_EVERY_N_FRAMES == 0:
        faces = app.get(frame)
        last_faces = faces

        if faces:
            face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
            x1, y1, x2, y2 = face.bbox.astype(int)

            # Liveness
            crop = crop_for_liveness(frame, (x1, y1, x2, y2))
            is_live = False
            p_real, p_print, p_replay = 0.0, 0.0, 0.0

            if crop is not None:
                p_real, p_print, p_replay = predict_liveness(liveness_session, crop)
                is_live = (p_real >= LIVENESS_THRESHOLD) and (p_real > p_print) and (p_real > p_replay)

            if is_live:
                sim = cosine_similarity(reference_embedding, face.embedding)
                if sim >= SIMILARITY_THRESHOLD:
                    last_box_color = (0, 255, 0)
                    last_header = f"ACCESSO OK ({sim:.2f})"
                    last_sub = f"Live:{p_real*100:.0f}% | Match con CIE"
                else:
                    last_box_color = (0, 165, 255)
                    last_header = f"NON RICONOSCIUTO ({sim:.2f})"
                    last_sub = f"Live:{p_real*100:.0f}% | Sotto soglia {SIMILARITY_THRESHOLD}"
            else:
                last_box_color = (0, 0, 255)
                attack_type = "SCHERMO" if p_replay > p_print else "FOTO CARTA"
                last_header = f"ATTACCO DETECTED! ({attack_type})"
                last_sub = f"Real:{p_real*100:.0f}% | Print:{p_print*100:.0f}% | Screen:{p_replay*100:.0f}%"
        else:
            last_box_color = (180, 180, 180)
            last_header = "In attesa di un volto..."
            last_sub = ""

    # Disegna l'ultimo stato noto (in modo che ogni fotogramma sia renderizzato senza buchi)
    if last_faces:
        face = max(last_faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        x1, y1, x2, y2 = face.bbox.astype(int)
        cv2.rectangle(frame, (x1, y1), (x2, y2), last_box_color, 2)
        cv2.putText(frame, last_header, (x1, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, last_box_color, 2)
        cv2.putText(frame, last_sub, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1)

    # Mostra la miniatura della CIE nell'angolo
    th_h, th_w = id_card_thumb.shape[:2]
    frame[15:15+th_h, 15:15+th_w] = id_card_thumb
    cv2.rectangle(frame, (15, 15), (15+th_w, 15+th_h), (255, 255, 255), 1)
    cv2.putText(frame, "CIE Riferimento", (20, 15+th_h+18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    cv2.imshow("Autenticazione CIE + Liveness (M2 Smooth)", frame)

    key = cv2.waitKey(1) & 0xFF
    if key in (ord('q'), 27):
        break
    elif key == ord('s'):
        cv2.imwrite("screenshot_smooth_demo.png", frame)
        print("📸 Screenshot salvato!")

cap.release()
cv2.destroyAllWindows()