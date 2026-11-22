import cv2
import matplotlib.pyplot as plt
from insightface.app import FaceAnalysis
import numpy as np

# ==============================================================================
# 1. PERCORSI DELLE TUE IMMAGINI REALI
# ==============================================================================
PATH_CIE  = "/Users/jonathan/Downloads/0_front.png"
PATH_LIVE = "/Users/jonathan/Downloads/PairDrop_files_20261121_1956/0c9b737552a8_m_live_0_p_d1.png"

# ==============================================================================
# 2. INIZIALIZZAZIONE INSIGHTFACE
# ==============================================================================
app = FaceAnalysis(
    name="buffalo_l",
    root="../../../backend/.insightface",
    allowed_modules=["detection", "recognition"]
)
app.prepare(ctx_id=-1, det_size=(320, 320))

def draw_custom_detection(img_bgr: np.ndarray, face, radius: int = 6, box_thickness: int = 3):
    canvas = img_bgr.copy()
    
    # 1. Disegno del Bounding Box
    x1, y1, x2, y2 = face.bbox.astype(int)
    cv2.rectangle(canvas, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=box_thickness)
    
    # 2. Disegno dei 5 Keypoint con raggio personalizzabile
    if face.kps is not None:
        colors = [
            (255, 0, 0),    # Occhio destro (Blu)
            (0, 255, 0),    # Occhio sinistro (Verde)
            (0, 255, 255),  # Punta del naso (Giallo)
            (255, 0, 255),  # Angolo destro bocca (Magenta)
            (0, 165, 255)   # Angolo sinistro bocca (Arancione)
        ]
        for i, kp in enumerate(face.kps):
            color = colors[i]
            cx, cy = int(kp[0]), int(kp[1])
            cv2.circle(canvas, (cx, cy), radius=radius, color=color, thickness=-1)
            cv2.circle(canvas, (cx, cy), radius=radius, color=(0, 0, 0), thickness=1)
            
    return canvas

def process_and_draw(image_path: str, radius: int, box_thickness: int):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Impossibile caricare l'immagine: {image_path}")
    
    faces = app.get(img)
    if not faces:
        raise ValueError(f"Nessun volto rilevato in: {image_path}")
    
    main_face = max(
        faces,
        key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
    )
    
    annotated_bgr = draw_custom_detection(img, main_face, radius=radius, box_thickness=box_thickness)
    annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
    return annotated_rgb, float(main_face.det_score)

img_cie_rgb, score_cie   = process_and_draw(PATH_CIE, radius=5, box_thickness=3)
img_live_rgb, score_live = process_and_draw(PATH_LIVE, radius=7, box_thickness=3)

# ==============================================================================
# 3. CREAZIONE FIGURA AFFIANCATA E SALVATAGGIO
# ==============================================================================
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10.5
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=300)

# Pannello sinistro: CIE rettificata
ax1.imshow(img_cie_rgb)
ax1.set_title(f"(a) Documento CIE rettificato\n(det_score = {score_cie:.2f})", fontsize=9, fontweight="bold", pad=8)
ax1.axis("off")

# Pannello destro: Frame Live
ax2.imshow(img_live_rgb)
ax2.set_title(f"(b) Fotogramma live da webcam\n(det_score = {score_live:.2f})", fontsize=9, fontweight="bold", pad=8)
ax2.axis("off")

plt.tight_layout()
plt.savefig("../confronto_bbox_kps.png", format="png", dpi=300, bbox_inches="tight")
plt.show()
print("Immagine salvata correttamente in ../confronto_bbox_kps.png")
