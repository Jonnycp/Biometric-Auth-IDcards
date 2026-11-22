import warnings
warnings.filterwarnings("ignore")

import cv2
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

# ─── 1. CARICAMENTO MODELLI ───────────────────────────────────────────────────
print("Caricamento Face Detector (buffalo_sc)...")
detector = FaceAnalysis(name="buffalo_sc", root="~/.insightface")
detector.prepare(ctx_id=-1, det_size=(480, 480))

print("Caricamento MiniFASNet Anti-Spoofing...")
# Percorso relativo dalla root del progetto (Desktop/Tesi)
MODEL_PATH = "../backend/.insightface/minifasnet_v2.onnx"
liveness_session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
print("Modelli caricati con successo!\n")

# ─── 2. PARAMETRI SOGLIA ──────────────────────────────────────────────────────
BUFFER_SIZE = 60            # Numero di frame da analizzare in sequenza (~2 secondi a 30fps)
SCORE_THRESHOLD = 0.50      # MiniFASNet: soglia minima di media per considerare la texture vera
MOVEMENT_THRESHOLD = 0.025  # Deviazione standard minima dello yaw (rotazione orizzontale della testa)

# ─── 3. FUNZIONI DI SUPPORTO ─────────────────────────────────────────────────

def crop_for_liveness(img, bbox, scale=2.7, out_size=(80, 80)):
    """
    MiniFASNet richiede un ritaglio allargato a scala 2.7x rispetto al bbox del volto,
    in modo da vedere anche mento, capelli e collo.
    """
    src_h, src_w, _ = img.shape
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1

    # Calcola il riquadro espanso
    scale = min((src_h - 1) / h, min((src_w - 1) / w, scale))
    new_w = w * scale
    new_h = h * scale
    cx = x1 + w / 2
    cy = y1 + h / 2

    left   = int(cx - new_w / 2)
    top    = int(cy - new_h / 2)
    right  = int(cx + new_w / 2)
    bottom = int(cy + new_h / 2)

    # Correzione coordinate fuori dallo schermo
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


def predict_liveness(crop_bgr):
    """
    Esegue l'inferenza con MiniFASNet.
    Input atteso: BGR float32 con valori [0, 255] (NO DIVISIONE PER 255!)
    Output classi:
      0: Print Attack (foto cartacea)
      1: Real Face (volto reale)
      2: Replay/Screen (schermo cellulare/PC)
    """
    blob = crop_bgr.astype(np.float32)                 # Float grezzo [0, 255]
    blob = np.transpose(blob, (2, 0, 1))               # HWC (80,80,3) -> CHW (3,80,80)
    blob = np.expand_dims(blob, axis=0)                # Aggiunge dimensione batch -> (1, 3, 80, 80)

    outputs = liveness_session.run(None, {"input": blob})
    logits = outputs[0][0]

    # Softmax stabile per calcolare le probabilità
    exp_l = np.exp(logits - np.max(logits))
    probs = exp_l / np.sum(exp_l)

    p_print = probs[0]
    p_real = probs[1]
    p_replay = probs[2]

    return p_real, p_print, p_replay


def compute_yaw(kps):
    """
    Stima la rotazione orizzontale (yaw) usando i 5 punti chiave (keypoints) di InsightFace:
    kps[0] = occhio dx, kps[1] = occhio sx, kps[2] = naso.
    Se la testa è dritta, il rapporto è ~0.5.
    Se giri la testa a destra o sinistra, il rapporto varia.
    """
    right_eye = kps[0]
    left_eye  = kps[1]
    nose      = kps[2]

    eye_width = left_eye[0] - right_eye[0]
    if eye_width < 10:  # Troppo piccolo o di profilo estremo
        return None

    # Posizione relativa orizzontale del naso rispetto agli occhi
    return (nose[0] - right_eye[0]) / eye_width


# ─── 4. STATO E BUFFER ───────────────────────────────────────────────────────
scores = []      # Buffer per raccogliere i punteggi di MiniFASNet
yaw_values = []  # Buffer per raccogliere la rotazione della testa

decision = "Inquadra il volto e muovi leggermente la testa..."
decision_color = (0, 200, 255)

# ─── 5. AVVIO WEBCAM ──────────────────────────────────────────────────────────
# Usa 3 se la fotocamera integrata del Mac è la 3 (come avevi visto l'altra volta),
# altrimenti rimetti 0.
CAMERA_INDEX = 2
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print(f"Errore apertura camera {CAMERA_INDEX}, provo con 0...")
    cap = cv2.VideoCapture(0)

print("=" * 60)
print("👉 Mettiti davanti alla fotocamera")
print("👉 Muovi lentamente la testa a destra e sinistra")
print("👉 Premi [Q] o [ESC] per terminare")
print("=" * 60)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Errore lettura frame webcam.")
        break

    faces = detector.get(frame)

    if faces:
        # Se ci sono più volti (es. tu e una foto che mostri), prendi il più grande/vicino
        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        x1, y1, x2, y2 = face.bbox.astype(int)

        # 1. Analisi texture (MiniFASNet)
        crop = crop_for_liveness(frame, (x1, y1, x2, y2))
        if crop is not None:
            p_real, p_print, p_replay = predict_liveness(crop)
            scores.append(float(p_real))

            # Mostra la miniatura 80x80 ingrandita in alto a destra per debug
            thumb = cv2.resize(crop, (100, 100))
            h_f, w_f = frame.shape[:2]
            frame[10:110, w_f - 110:w_f - 10] = thumb

        # 2. Analisi movimento (Yaw dai keypoints)
        yaw = compute_yaw(face.kps)
        if yaw is not None:
            yaw_values.append(yaw)

        # 3. Valutazione ogni BUFFER_SIZE frame
        if len(scores) >= BUFFER_SIZE:
            avg_score = float(np.mean(scores))
            mov_std = float(np.std(yaw_values)) if len(yaw_values) > 10 else 0.0

            texture_ok = (avg_score >= SCORE_THRESHOLD)
            movement_ok = (mov_std >= MOVEMENT_THRESHOLD)

            if texture_ok and movement_ok:
                decision = f"ACCESSO OK (Reale) [score:{avg_score:.2f} mov:{mov_std:.3f}]"
                decision_color = (0, 255, 0) # Verde
            elif texture_ok and not movement_ok:
                decision = f"SOSPETTO STATICO! Muovi la testa [mov:{mov_std:.3f}]"
                decision_color = (0, 165, 255) # Arancione
            else:
                decision = f"ATTACCO DETECTED (Texture falsa) [score:{avg_score:.2f}]"
                decision_color = (0, 0, 255) # Rosso

            # Reset dei buffer per il prossimo controllo
            scores = []
            yaw_values = []

        # ── INTERFACCIA A SCHERMO ──
        # Barra di progresso dell'accumulo frame sotto il volto
        progress = int((len(scores) / BUFFER_SIZE) * (x2 - x1))
        cv2.rectangle(frame, (x1, y2 + 5), (x2, y2 + 15), (60, 60, 60), -1)
        cv2.rectangle(frame, (x1, y2 + 5), (x1 + progress, y2 + 15), (0, 200, 255), -1)

        # Riquadro e testo
        cv2.rectangle(frame, (x1, y1), (x2, y2), decision_color, 2)
        cv2.putText(frame, decision, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, decision_color, 2)

        # Valori istantanei dell'ultimo frame
        if scores:
            debug_text = f"P_Real:{scores[-1]:.2f} Print:{p_print:.2f} Screen:{p_replay:.2f}"
            if yaw is not None:
                debug_text += f" Yaw:{yaw:.2f}"
            cv2.putText(frame, debug_text, (x1, y2 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (220, 220, 220), 1)

    else:
        # Nessun volto: resetta i buffer
        scores = []
        yaw_values = []
        decision = "In attesa di un volto..."
        decision_color = (150, 150, 150)

    cv2.imshow("Test Liveness V2 - Texture + Movimento", frame)

    key = cv2.waitKey(1) & 0xFF
    if key in (ord('q'), 27):
        break

cap.release()
cv2.destroyAllWindows()