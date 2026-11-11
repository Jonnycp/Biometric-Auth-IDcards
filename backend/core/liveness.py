import numpy as np
import os
import onnxruntime as ort
import cv2

# Carica modello MiniFASNet per test liveness
def loadLivenessModel(modelPath: str):
    if not os.path.exists(modelPath):
        raise FileNotFoundError(f"Modello MiniFASNet non trovato: {modelPath}")
    
    return ort.InferenceSession(modelPath, providers=["CPUExecutionProvider"])

# Scala bbox faccia per liveness
def scaleBbox(image: np.ndarray, bbox: np.ndarray, scale: float = 2.7, out_size: tuple = (80, 80)):
    src_h, src_w = image.shape
    x1, y1, x2, y2 = bbox

    w_box = x2 - x1
    h_box = y2 - y1

    center_x = x1 + w_box / 2
    center_y = y1 + h_box / 2

    # Calcola max scale per evitare di uscire fuori bordi src
    scale = min((src_h - 1)/h_box, (src_w - 1)/w_box, scale)

    new_w = w_box * scale
    new_h = h_box * scale

    left = int(center_x - new_w / 2)
    top = int(center_y - new_h / 2)
    right = int(center_x + new_w / 2)
    bottom = int(center_y + new_h / 2)

    # gestione overflow
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

    crop = image[max(0, top):min(src_h, bottom), max(0, left):min(src_w, right)]

    if crop.size == 0:
        return None
    return cv2.resize(crop, out_size)

# Previsione liveness con MiniFASNet
def predictLiveness(session: ort.InferenceSession, crop_bgr: np.ndarray):
    blob = crop_bgr.astype(np.float32) #int to float
    blob = np.transpose(blob, (2, 0, 1)) #HWC (height, width, channels) -> CHW (channels, height, width)
    blob = np.expand_dims(blob, axis=0) #to list of 1 image (batch size = 1)
   
    outputs = session.run(None, {"input": blob})
    logits = np.array(outputs[0])[0] #valori grezzi non normalizzati (logits)

    # SOFTMAX stabile (normalizza logits in probabilità)
    exp_l = np.exp(logits - np.max(logits))
    probs = exp_l / np.sum(exp_l)

    return float(probs[1]), float(probs[0]), float(probs[2]) #real, print, screen

# Check liveness con soglia
def checkLiveness(session: ort.InferenceSession, image: np.ndarray, bbox: np.ndarray, threshold: float = 0.5):
    crop = cropLiveness(image, bbox)
    if not crop is None:
        p_real, p_print, p_screen = predictLiveness(session, crop)

        is_live = (p_real >= threshold) and (p_real > p_print) and (p_real > p_screen)
        attack_type = "NONE"
        if not is_live:
            if p_print > p_screen:
                attack_type = "PRINT"
            else:
                attack_type = "SCREEN"
        return {
            "is_live": is_live,
            "score": p_real,
            "attack_type": attack_type,
            "probabilities": {
                "real": p_real,
                "print": p_print,
                "screen": p_screen
            },
            "treshold": threshold
        }
    return {
        "is_live": False,
        "score": 0.0,
        "attack_type": "CROP FAILED",
        "probabilities": {
            "real": 0.0,
            "print": 0.0,
            "screen": 0.0
        },
        "treshold": threshold
    }