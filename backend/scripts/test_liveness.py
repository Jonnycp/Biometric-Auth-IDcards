import cv2
import numpy as np
import onnxruntime as ort
import time
from insightface.app import FaceAnalysis
import cv2
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

# 1. Caricamento Face Detector
print("Caricamento Face Detector (buffalo_sc)...")
detector = FaceAnalysis(name="buffalo_sc", root="~/.insightface")
detector.prepare(ctx_id=-1, det_size=(480, 480))
# 2. Caricamento MiniFASNet ONNX
print("Caricamento MiniFASNet Anti-Spoofing...")
MODEL_PATH = "../backend/.insightface/minifasnet_v2.onnx"
liveness_session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
print("Modelli pronti!\n")
def crop_for_liveness(img, bbox, scale=2.7, out_size=(80, 80)):
    src_h, src_w, _ = img.shape
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1
    # Calcolo del box allargato centrato sul viso
    scale = min((src_h - 1) / h, min((src_w - 1) / w, scale))
    new_w = w * scale
    new_h = h * scale
    center_x, center_y = x1 + w / 2, y1 + h / 2
    left = int(center_x - new_w / 2)
    top = int(center_y - new_h / 2)
    right = int(center_x + new_w / 2)
    bottom = int(center_y + new_h / 2)
    # Correzioni coordinate ai bordi
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
    # Preprocessing: BGR in range [0.0, 1.0], formato (1, 3, 80, 80)
    blob = crop_bgr.astype(np.float32)
    blob = np.transpose(blob, (2, 0, 1))
    blob = np.expand_dims(blob, axis=0)
    # Inferenza
    outputs = liveness_session.run(None, {"input": blob})
    logits = outputs[0][0]
    # Softmax
    exp_logits = np.exp(logits - np.max(logits))
    probs = exp_logits / np.sum(exp_logits)
    # Classi: 0 = Print attack, 1 = Real face, 2 = Replay/Screen attack
    p_print = probs[0]
    p_real = probs[1]
    p_replay = probs[2]
    return p_real, p_print, p_replay
# Usa la webcam (prova 0 se sei con la webcam del Mac)
cap = cv2.VideoCapture(2)
print("="*50)
print("👉 Mettiti a circa mezzo metro dallo schermo.")
print("👉 Guarda i 3 valori a schermo (Real, Print, Replay).")
print("👉 Premi [q] o [ESC] per uscire.")
print("="*50)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    faces = detector.get(frame)
    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)
        crop = crop_for_liveness(frame, (x1, y1, x2, y2))
        if crop is not None:
            p_real, p_print, p_replay = predict_liveness(crop)
            # Se la probabilità reale è la più alta ed è sopra il 50%
            is_live = (p_real > p_print) and (p_real > p_replay) and (p_real >= 0.50)
            if is_live:
                color = (0, 255, 0)
                status_text = f"REAL ({p_real*100:.1f}%)"
            else:
                color = (0, 0, 255)
                # Capiamo se sospetta sia una foto stampata o uno schermo
                attack_type = "SCHERMO" if p_replay > p_print else "FOTO CARTA"
                status_text = f"FAKE: {attack_type} ({max(p_print, p_replay)*100:.1f}%)"
            # Disegna riquadro e testo
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, status_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)
            # Debug dettagliato
            debug_text = f"Real:{p_real:.2f} | Print:{p_print:.2f} | Replay:{p_replay:.2f}"
            cv2.putText(frame, debug_text, (x1, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
            # Mostra la miniatura 80x80 in alto a destra per vedere cosa "vede" il modello
            thumb = cv2.resize(crop, (120, 120))
            frame[20:140, frame.shape[1]-140:frame.shape[1]-20] = thumb
            cv2.rectangle(frame, (frame.shape[1]-140, 20), (frame.shape[1]-20, 140), (255, 255, 255), 1)
            cv2.putText(frame, "Input AI", (frame.shape[1]-135, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    cv2.imshow("Test Anti-Spoofing (MiniFASNet)", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break
cap.release()
cv2.destroyAllWindows()